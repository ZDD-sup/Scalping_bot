from collections import deque

class RSI:
    def __init__(self, period: int = 14, smoothing_type: str = 'ema'):
        """
        Класс для расчета индикатора RSI (Relative Strength Index).

        :param period: Период расчета RSI, по умолчанию 14.
        :param smoothing_type: Тип сглаживания ('wilder' или 'ema').
        """
        self.period = period
        self.smoothing_type = smoothing_type.lower()
        if self.smoothing_type not in ['wilder', 'ema']:
            raise ValueError("smoothing_type must be 'wilder' or 'ema'")
        self.gains = deque(maxlen=period)
        self.losses = deque(maxlen=period)
        self.prev_price = None
        self.avg_gain = 0
        self.avg_loss = 0
        self.value = None
        self.count = 0

    def _calculate_rsi(self):
        """
        Расчет текущего значения RSI на основе avg_gain и avg_loss.
        """
        if self.avg_loss == 0 and self.avg_gain == 0:
            return 50  # рынок стоит, RSI нейтральный
        elif self.avg_loss == 0:
            return 100
        elif self.avg_gain == 0:
            return 0
        rs = self.avg_gain / self.avg_loss
        return 100 - (100 / (1 + rs))

    def update_price(self, price: float):
        """
        Обновляет RSI на основе новой цены.

        :param price: float — Новое значение цены.
        :return: float | None — Текущее значение RSI.
        """
        if self.prev_price is None:
            self.prev_price = price
            return None

        change = price - self.prev_price
        gain = max(change, 0)
        loss = abs(min(change, 0))

        self.prev_price = price
        self.count += 1

        if self.count <= self.period:
            self.gains.append(gain)
            self.losses.append(loss)
            if self.count == self.period:
                self.avg_gain = sum(self.gains) / self.period
                self.avg_loss = sum(self.losses) / self.period
                self.value = self._calculate_rsi()
                return self.value
        else:
            if self.smoothing_type == 'wilder':
                self.avg_gain = ((self.avg_gain * (self.period - 1)) + gain) / self.period
                self.avg_loss = ((self.avg_loss * (self.period - 1)) + loss) / self.period
            elif self.smoothing_type == 'ema':
                alpha = 2 / (self.period + 1)
                self.avg_gain = (gain * alpha) + (self.avg_gain * (1 - alpha))
                self.avg_loss = (loss * alpha) + (self.avg_loss * (1 - alpha))

            self.value = self._calculate_rsi()
            return self.value

        return None
