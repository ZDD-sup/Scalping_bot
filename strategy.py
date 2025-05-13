class ScalpingStrategy:
    def __init__(self, rsi, ema_short, ema_long):
        """
        Инициализация стратегии.

        :param rsi: объект индикатора RSI
        :param ema_short: объект EMA с коротким окном
        :param ema_long: объект EMA с длинным окном
        """
        self.rsi = rsi
        self.ema_short = ema_short
        self.ema_long = ema_long
        self.last_signal = "Neutral"
        self.high = None
        self.low = None

    def update_extremes(self, klines):
        """
        Обновляет локальные high/low за N последних свечей.

        :param klines: список [(timestamp, close_price), ...]
        """
        closes = [c for _, c in klines]
        self.high = max(closes)
        self.low = min(closes)

    def generate_signal(self, price):
        """
        Генерация сигнала на вход/выход.

        :param price: текущая цена
        :return: 'Buy', 'Sell' или 'Neutral'
        """
        rsi_value = self.rsi.update_price(price)
        ema_s = self.ema_short.update(price)
        ema_l = self.ema_long.update(price)
        # print(ema_l)
        # print(ema_s)

        # Проверка готовности
        if None in [rsi_value, ema_s, ema_l, self.high, self.low]:
            return "Neutral"

        signal = "Neutral"

        # breakout вверх + тренд вверх + RSI не перекуплен
        if price > self.high and ema_s > ema_l and rsi_value > 50:
        # if ema_s > ema_l and rsi_value < 30:
        # if ema_s > ema_l and 70 > rsi_value > 50:
            print(rsi_value)
            signal = "Buy"

        # breakout вниз + тренд вниз + RSI не перепродан
        elif price < self.low and ema_s < ema_l and rsi_value < 50:
        # elif ema_s < ema_l and rsi_value > 70:
        # elif ema_s < ema_l and 30 < rsi_value < 50:
            print(rsi_value)
            signal = "Sell"

        self.last_signal = signal
        return signal
