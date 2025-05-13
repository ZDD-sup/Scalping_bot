from pybit.unified_trading import HTTP

def get_min_order_info(symbol: str, category: str = "linear", testnet: bool = True):
    """
    Получает minOrderQty, qtyStep и minNotionalValue для указанного символа с Bybit.

    :param symbol: str — тикер пары (например, "BTCUSDT")
    :param category: str — категория торговли ("linear", "inverse", "option")
    :param testnet: bool — использовать ли тестовую сеть
    :return: dict — {'min_qty': float, 'qty_step': float, 'min_notional': float}
    """
    session = HTTP(testnet=testnet)
    try:
        response = session.get_instruments_info(category=category, symbol=symbol)
        if response["retCode"] != 0 or not response["result"]["list"]:
            raise Exception(f"Ошибка запроса: {response['retMsg']}")

        info = response["result"]["list"][0]["lotSizeFilter"]
        min_qty = float(info["minOrderQty"])
        qty_step = float(info["qtyStep"])
        min_notional = float(info.get("minNotionalValue", 5.0))  # По умолчанию 5 USDT, если нет значения

        return min_qty, qty_step,min_notional

    except Exception as e:
        print(f"[{symbol}] Не удалось получить данные лота: {e}")
        return 1.0, 1.0, 5.0

import math

def calculate_valid_qty(usdt_amount: float, price: float, min_qty: float, qty_step: float, min_notional: float):
    """
    Рассчитывает допустимое количество (qty), исходя из USDT и ограничений биржи.

    :param usdt_amount: сколько USDT хотим потратить
    :param price: текущая цена актива
    :param min_qty: минимальное разрешенное количество
    :param qty_step: шаг изменения количества
    :param min_notional: минимальная стоимость сделки (в USDT)
    :return: float — количество, округленное по правилам биржи или None, если нельзя торговать
    """
    qty = usdt_amount / price

    # Приводим к ближайшему допустимому шагу
    steps = math.floor(qty / qty_step)
    adjusted_qty = round(steps * qty_step, 10)

    # Проверяем на соответствие ограничениям
    if adjusted_qty < min_qty:
        return None
    if adjusted_qty * price < min_notional:
        return None

    return adjusted_qty
