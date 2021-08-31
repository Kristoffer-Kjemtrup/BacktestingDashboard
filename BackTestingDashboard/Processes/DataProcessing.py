import pandas as pd
import numpy as np
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator, StochRSIIndicator
from ta.trend import MACD, SMAIndicator
import yfinance as yf

ArgDict = {
    'SMA': [50, 200],
    'RSI': [14, 30, 70],
    'sRSI': [14, 2, 2],
    'MACD': [26, 12, 9],
    'BB': [20, 2]
}


def getArgs(settings, param):
    args = ArgDict[param]
    if param in settings and len(settings[param]) > 0:
        for i in range(min(len(settings[param]), len(ArgDict[param]))):
            args[i] = settings[param][i]
    return args


def getTicker(ticker, period=4, interval=5, indicators = [], settings = {}):
    periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    intervals = ['1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo', '3mo']
    if (period > 6 and interval < 5) or (period > 2 and interval < 4) or (period > 1 and interval < 1):
        interval = 5

    stock = yf.Ticker(ticker)
    bars = stock.history(period=periods[period], interval=intervals[interval])
    bars_df = pd.DataFrame(bars)
    bars_df.drop(bars_df.tail(1).index, inplace=True)
    bars_df['datetime'] = bars_df.index

    if 'RSI' in indicators:
        bars_df['RSI'] = RSIIndicator(bars_df['Close'], getArgs(settings, 'RSI')[0]).rsi()

    if 'sRSI' in indicators:
        bars_df['sRSId'] = StochRSIIndicator(bars_df['Close'], *getArgs(settings, 'sRSI')).stochrsi_d()
        bars_df['sRSIk'] = StochRSIIndicator(bars_df['Close'], *getArgs(settings, 'sRSI')).stochrsi_k()

    if 'SMA' in indicators:
        bars_df['SMAshort'] = SMAIndicator(bars_df['Close'], getArgs(settings, 'SMA')[0]).sma_indicator()
        bars_df['SMAlong'] = SMAIndicator(bars_df['Close'], getArgs(settings, 'SMA')[1]).sma_indicator()

    if 'BB' in indicators:
        bars_df['BB_lower'] = BollingerBands(bars_df['Close'], *getArgs(settings, 'BB')).bollinger_lband()
        bars_df['BB_higher'] = BollingerBands(bars_df['Close'], *getArgs(settings, 'BB')).bollinger_hband()
        bars_df['BB_mid'] = BollingerBands(bars_df['Close'], getArgs(settings, 'BB')[0]).bollinger_mavg()

    if 'MACD' in indicators:
        bars_df['MACD'] = MACD(bars_df['Close'], *getArgs(settings, 'MACD')).macd()
        bars_df['MACD_sign'] = MACD(bars_df['Close'], *getArgs(settings, 'MACD')).macd_signal()
        bars_df['MACD_hist'] = MACD(bars_df['Close'], *getArgs(settings, 'MACD')).macd_diff()

    return bars_df


def getBackTestStats(tempdf, trades):
    if len(trades) > 0:
        date = [key for key in trades.keys()]
        direction = [trades[date[j]][0][0] for j in range(len(date))]

        df = pd.DataFrame(list(zip(date, direction)), columns=['date', 'direction'])
        df['High'] = np.nan
        df['Low'] = np.nan

        for i in range(len(tempdf)):
            for j in range(len(trades)):
                if tempdf.datetime[i] == date[j]:
                    df['High'][j], df['Low'][j] = (tempdf['High'][i], tempdf['Low'][i])


        df['Marker'] = np.where(df['direction'] > 0, df['High'] + 20, df['Low'] - 20)
        df['Symbol'] = np.where(df['direction'] > 0, 'triangle-up', 'triangle-down')
        df['Color'] = np.where(df['direction'] > 0, 'green', 'red')
        
        return df


def getBackTestReturns(bt_returns):
    dates = [key for key in bt_returns.keys()]
    returnpcts = [item[1] for item in bt_returns.items()]

    returns = [1000000]
    for i in range(len(dates)):
        if i == 0:
            continue
        return_num = returns[i - 1] * (1 + returnpcts[i])
        returns.append(return_num)

    returns_df = pd.DataFrame(list(zip(dates, returns)), columns=['date', 'Return'])

    return returns_df


def getVolumeColor(df):
    INCREASING_COLOR = '#3fa93c'
    DECREASING_COLOR = '#ff6666'

    colors = []

    for i in range(len(df.Close)):
        if i != 0:
            if df.Close[i] > df.Close[i-1]:
                colors.append(INCREASING_COLOR)
            else:
                colors.append(DECREASING_COLOR)
        else:
            colors.append(DECREASING_COLOR)

    return colors


