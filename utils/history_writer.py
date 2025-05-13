import os
import csv
from datetime import datetime

def write_trade_history(symbol: str, interval: int, side: str, entry: float, exit_price: float):
    """
    Сохраняет завершённую сделку в CSV-файл для анализа.
    """
    profit = round(exit_price - entry if side == "Buy" else entry - exit_price, 4)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    folder = "logs"
    os.makedirs(folder, exist_ok=True)
    filename = f"{folder}/history_{symbol}_{interval}m.csv"

    file_exists = os.path.exists(filename)
    with open(filename, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "symbol", "interval", "side", "entry", "exit", "profit"])
        writer.writerow([timestamp, symbol, f"{interval}m", side, entry, exit_price, profit])
