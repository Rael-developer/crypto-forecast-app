import requests
import pandas as pd
from datetime import datetime

BASE_URL = "https://api.binance.com"

def get_price(symbol="BTCUSDT"):
    url = f"{BASE_URL}/api/v3/ticker/price?symbol={symbol}"
    r = requests.get(url).json()
    return float(r['price'])

def get_all_symbols():
    url = f"{BASE_URL}/api/v3/exchangeInfo"
    r = requests.get(url).json()
    symbols = [s['symbol'] for s in r['symbols'] if s['quoteAsset'] == 'USDT']
    return symbols

def get_historical_data(symbol="BTCUSDT", interval="1d", limit=500):
    url = f"{BASE_URL}/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    r = requests.get(url).json()
    data = []
    for k in r:
        data.append([datetime.fromtimestamp(k[0]/1000), float(k[4])])
    df = pd.DataFrame(data, columns=['ds', 'y'])
    return df
