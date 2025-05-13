from pybit.unified_trading import HTTP
from api_secret import API_KEY, API_SECRET

class BybitClient:
    def __init__(self, symbol: str, category: str, api_key: str, api_secret: str, demo=True):
        """
        Инициализация клиента Bybit.

        :param symbol: Торговая пара, например 'BTCUSDT'
        :param category: Категория ('spot', 'linear', 'inverse')
        :param api_key: API ключ
        :param api_secret: Секретный ключ
        :param demo: Использовать демо-трейдинг (True) или реальный (False)
        """
        self.symbol = symbol
        self.category = category
        self.session = HTTP(
            demo=demo,
            api_key=api_key,
            api_secret=api_secret
        )

    def get_min_order_qty(self):
        """
        Получает минимальное количество для торговли для каждой монеты в паре USDT.

        :return: Минимальное количество для торговли (float)
        """
        data = self.session.get_symbol_info(symbol=self.symbol, category=self.category)
        if "result" in data and "list" in data["result"]:
            symbol_info = data["result"]["list"][0]
            min_qty = float(symbol_info["minTradeQty"])  # Минимальное количество для торговли
            return min_qty
        else:
            print(f"Ошибка: Не удалось получить информацию о торговой паре {self.symbol}.")
            return None


# Пример использования:
api_key = API_KEY
api_secret = API_SECRET

symbols = ["SOLUSDT", "XRPUSDT", "XMRUSDT", "ETCUSDT"]
category = 'linear'  # Категория, например 'linear', 'spot' или 'inverse'

client = BybitClient(api_key=api_key, api_secret=api_secret, category=category, demo=True, symbol='')

for symbol in symbols:
    client.symbol = symbol
    min_qty = client.get_min_order_qty()
    if min_qty:
        print(f"Минимальное количество для пары {symbol}: {min_qty} {symbol.split('USDT')[0]}")
    else:
        print(f"Не удалось получить минимальное количество для торговой пары {symbol}.")
