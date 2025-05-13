from collections import deque
import statistics

class EMA:
    def __init__(self, period: int):
        self.period = period
        self.k = 2 / (period + 1)
        self.history = deque(maxlen=period)
        self.ema = None
        self.initial_ema_calculated = False

    def update(self, price: float):
        """
        Обновляет EMA на основе новой цены.
        :param price: float — последняя цена
        :return: float | None — новое значение EMA
        """
        self.history.append(price)

        if not self.initial_ema_calculated and len(self.history) == self.period:
            # Рассчитываем SMA за первый период
            self.ema = statistics.mean(self.history)
            self.initial_ema_calculated = True
            return self.ema
        elif self.initial_ema_calculated:
            self.ema = (price * self.k) + (self.ema * (1 - self.k))
            return self.ema
        else:
            return None  # Еще недостаточно данных для расчета начальной EMA