import json
import time
import threading
import os
from datetime import datetime

from utils.history_writer import write_trade_history

ORDER_FILE = "active_orders.json"

def load_orders():
    if os.path.exists(ORDER_FILE):
        with open(ORDER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_orders(orders):
    with open(ORDER_FILE, "w") as f:
        json.dump(orders, f, indent=2)

def track_tp(order_id, symbol, entry_price, direction, bybit, interval, timeout=180, tp_percent=0.02):
    """
    Отслеживает TP адаптивно: по росту X% или по времени (timeout сек).
    Сохраняет итог сделки в CSV и удаляет ордер из JSON.
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            current_price, _ = bybit.get_latest_price()

            if direction == "Buy" and current_price >= entry_price * (1 + tp_percent):
                sell_id = bybit.place_market_order("Sell", 1)
                print(f"[TP] Продано по TP +{tp_percent*100:.1f}%: {current_price} | ID: {sell_id}")
                write_trade_history(symbol, interval, direction, entry_price, current_price)
                break

            elif direction == "Sell" and current_price <= entry_price * (1 - tp_percent):
                buy_id = bybit.place_market_order("Buy", 1)
                print(f"[TP] Куплено по TP -{tp_percent*100:.1f}%: {current_price} | ID: {buy_id}")
                write_trade_history(symbol, interval, direction, entry_price, current_price)
                break

        except Exception as e:
            print(f"[TP-Check] Ошибка: {e}")
        time.sleep(5)

    else:
        # Если не достигнут TP за timeout — выйти по текущей цене
        try:
            current_price, _ = bybit.get_latest_price()
            if direction == "Buy":
                sell_id = bybit.place_market_order("Sell", 1)
                print(f"[TP] Продано по времени: {current_price} | ID: {sell_id}")
            else:
                buy_id = bybit.place_market_order("Buy", 1)
                print(f"[TP] Куплено по времени: {current_price} | ID: {buy_id}")
            write_trade_history(symbol, interval, direction, entry_price, current_price)
        except Exception as e:
            print(f"[TP-Time] Ошибка при выходе по времени: {e}")

    # Удаляем ордер из JSON
    orders = load_orders()
    orders.pop(order_id, None)
    save_orders(orders)


def start_tp_tracker(order_id, symbol, entry_price, direction, bybit, interval, tp_percent=0.02):
    """
    Запускает трекер TP в отдельном потоке. Можно задать процент TP.
    """
    orders = load_orders()
    orders[order_id] = {
        "symbol": symbol,
        "price": entry_price,
        "direction": direction,
        "interval": interval,
        "tp_percent": tp_percent,
        "time": datetime.now().isoformat()
    }
    save_orders(orders)

    thread = threading.Thread(
        target=track_tp,
        args=(order_id, symbol, entry_price, direction, bybit, interval),
        kwargs={"tp_percent": tp_percent}
    )
    thread.start()
