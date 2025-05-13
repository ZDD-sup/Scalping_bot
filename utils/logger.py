import csv
from datetime import datetime
import os

def get_log_path(symbol, interval):
    return f"logs/trades_{symbol}_{interval}m.csv"

def init_log(symbol, interval):
    os.makedirs("logs", exist_ok=True)
    log_path = get_log_path(symbol, interval)
    if not os.path.exists(log_path):
        with open(log_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                "timestamp", "signal", "price", "order_id",
                "profit", "rsi", "ema_short", "ema_long"
            ])

def log_trade(symbol, interval, signal, price, order_id, profit=None, rsi=None, ema_short=None, ema_long=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_path = get_log_path(symbol, interval)
    with open(log_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, signal, price, order_id, profit, rsi, ema_short, ema_long])
