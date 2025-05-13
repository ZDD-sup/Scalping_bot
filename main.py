import time
import threading
from datetime import datetime

from bybit_client import BybitClient
from indicators.ema import EMA
from indicators.rsi import RSI
from strategy import ScalpingStrategy
from utils.logger import init_log, log_trade
from utils.history_writer import write_trade_history
from utils.instrument_info import get_min_order_info, calculate_valid_qty
from api_secret import API_KEY, API_SECRET

# ⚙️ Настройки
SYMBOLS = ["SOLUSDT", "XRPUSDT", "XMRUSDT", "ETCUSDT"]
INTERVALS = [1, 3, 5]
CATEGORY = "linear"
USDT = 10
KLINE_LIMIT = 20
TP_PERCENT = 1.03  # +2%
SL_PERCENT = 0.97  # -5%
TIMEOUT = 10  # 3 минуты

def run_bot(symbol: str, interval_minutes: int):
    init_log(symbol, interval_minutes)

    bybit = BybitClient(symbol, CATEGORY, API_KEY, API_SECRET, demo=True)
    min_qty, qty_step, min_notional = get_min_order_info(symbol=symbol, category=CATEGORY, testnet=True)

    ema_short = EMA(period=5)
    ema_long = EMA(period=21)
    rsi = RSI(period=14, smoothing_type="ema")
    strategy = ScalpingStrategy(rsi, ema_short, ema_long)

    print(f"Бот запущен для {symbol} | Таймфрейм: {interval_minutes}m")

    active_order = None

    def log_exit(kind, entry_price, exit_price, direction):
        change = ((exit_price - entry_price) / entry_price) * 100
        change_str = f"{change:+.2f}%"
        action = "Продано" if direction == "Buy" else "Куплено"
        print(f"[{kind}] {symbol} {action} по {exit_price:.4f} ({change_str})")
        write_trade_history(symbol, interval_minutes, direction, entry_price, exit_price)

    while True:
        try:
            start_time = time.time()

            # Получение свечей и обновление индикаторов
            klines = bybit.get_klines(interval=interval_minutes, limit=KLINE_LIMIT)
            strategy.update_extremes(klines)

            # Текущая цена
            price, ts = bybit.get_latest_price()
            price = float(price)
            signal = strategy.generate_signal(price)
            signal="Sell"
            # Проверка активного ордера
            if active_order:
                elapsed = time.time() - active_order["time"]
                entry_price = active_order["entry_price"]
                direction = active_order["direction"]
                qty = active_order["qty"]

                if direction == "Buy" and price >= entry_price * TP_PERCENT:
                    bybit.place_market_order("Sell", qty)
                    log_exit("TP", entry_price, price, direction)
                    active_order = None

                elif direction == "Sell" and price <= entry_price * (2 - TP_PERCENT):
                    bybit.place_market_order("Buy", qty)
                    log_exit("TP", entry_price, price, direction)
                    active_order = None

                elif direction == "Buy" and price <= entry_price * SL_PERCENT:
                    bybit.place_market_order("Sell", qty)
                    log_exit("SL", entry_price, price, direction)
                    active_order = None

                elif direction == "Sell" and price >= entry_price * (2 - SL_PERCENT):
                    bybit.place_market_order("Buy", qty)
                    log_exit("SL", entry_price, price, direction)
                    active_order = None

                elif elapsed >= TIMEOUT:
                    close_side = "Sell" if direction == "Buy" else "Buy"
                    bybit.place_market_order(close_side, qty)
                    log_exit("TIMEOUT", entry_price, price, direction)
                    active_order = None

            else:
                if signal == "Buy":# ЧТОТО ТУТ НЕ ТАК НАВЕРНОЕ НАДО РАЗДЕЛИТЬ СИГНАЛЫ
                    qty = calculate_valid_qty(USDT, price, min_qty, qty_step, min_notional)
                    take_profit = round(price * TP_PERCENT, 3)
                    stop_loss = round(price * SL_PERCENT, 3)
                    order_id = bybit.place_market_order(signal, qty, take_profit, stop_loss)
                    print(f"[{symbol} | {interval_minutes}m] {signal.upper()} @ {price} | ID: {order_id}")
                    log_trade(symbol, interval_minutes, signal, price, order_id, None, rsi.value, ema_short.ema, ema_long.ema)

                    active_order = {
                        "direction": signal,
                        "entry_price": price,
                        "qty": qty,
                        "time": time.time(),
                        "order_id": order_id
                    }
                elif signal == "Sell":
                    qty = calculate_valid_qty(USDT, price, min_qty, qty_step, min_notional)
                    take_profit = round(price * TP_PERCENT, 3)
                    stop_loss = round(price * SL_PERCENT, 3)
                    order_id = bybit.place_market_order(signal, qty, stop_loss, take_profit)
                    print(f"[{symbol} | {interval_minutes}m] {signal.upper()} @ {price} | ID: {order_id}")
                    log_trade(symbol, interval_minutes, signal, price, order_id, None, rsi.value, ema_short.ema, ema_long.ema)

                    active_order = {
                        "direction": signal,
                        "entry_price": price,
                        "qty": qty,
                        "time": time.time(),
                        "order_id": order_id
                    }
                else:
                    print(f"[{symbol} | {interval_minutes}m] NEUTRAL | Цена: {price}")
                    log_trade(symbol, interval_minutes, "Neutral", price, None, None, rsi.value, ema_short.ema, ema_long.ema)

            elapsed = time.time() - start_time
            time.sleep(max(0, 60 * interval_minutes - elapsed))

        except Exception as e:
            print(f"[{symbol} | {interval_minutes}m] Ошибка: {e}")
            time.sleep(5)

def main():
    threads = []

    for symbol in SYMBOLS:
        for interval in INTERVALS:
            t = threading.Thread(target=run_bot, args=(symbol, interval))
            t.start()
            threads.append(t)

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
