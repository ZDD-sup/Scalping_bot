from pybit.unified_trading import HTTP

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

    def get_latest_price(self):
        """
        Получает последнюю цену и серверное время.

        :return: (lastPrice: float, serverTime: int)
        """
        data = self.session.get_tickers(symbol=self.symbol, category=self.category)
        last_price = float(data["result"]["list"][0]["lastPrice"])
        time_stamp = int(data["time"])
        return last_price, time_stamp

    def get_klines(self, interval: int = 1, limit: int = 100):
        """
        Получает исторические свечи.

        :param interval: Интервал в минутах (1, 3, 5, 15 и т.д.)
        :param limit: Кол-во свечей
        :return: список кортежей (время, цена закрытия)
        """
        data = self.session.get_kline(
            symbol=self.symbol,
            category=self.category,
            interval=str(interval),
            limit=limit
        )
        klines = data["result"]["list"]
        return [(int(item[0]), float(item[4])) for item in klines]

    def place_market_order(self, side: str, qty: float, takeProfit, stopLoss):
        """
        Размещает рыночный ордер.

        :param side: 'Buy' или 'Sell'
        :param qty: Кол-во (в base asset)
        :return: ID ордера или ошибка
        """
        try:
            response = self.session.place_order(
                symbol=self.symbol,
                category=self.category,
                side=side,
                orderType="Market",
                qty=str(qty),
                takeProfit=round(takeProfit, 2),
                stopLoss=round(stopLoss, 2),
                isLeverage=1
            )
            return response["result"]["orderId"]
        except Exception as e:
            print(f"Ошибка при размещении ордера: {e}")
            return None
