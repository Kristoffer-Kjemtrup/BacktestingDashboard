import pandas as pd
import yfinance as yf
import backtrader as bt
from BackTestingDashboard.Processes import DataProcessing as DP
import backtrader.analyzers as btanalyzers


def getTicker(ticker, period=4, interval=5):
    periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    intervals = ['1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo', '3mo']
    if (period > 6 and interval < 5) or (period > 2 and interval < 4) or (period > 1 and interval < 1):
        interval = 5

    stock = yf.Ticker(ticker)
    bars = stock.history(period=periods[period], interval=intervals[interval])
    bars_df = pd.DataFrame(bars)
    bars_df.drop(bars_df.tail(1).index, inplace=True)
    bars_df['datetime'] = bars_df.index
    del bars_df['Dividends']
    del bars_df['Stock Splits']

    return bars_df


class PandasData(bt.feeds.PandasData):
    params = (
        ('datetime', -1),
        ('open', -1),
        ('high', -1),
        ('low', -1),
        ('close', -1),
        ('volume', -1),
        ('openinterest', None),
        ('adj_close', None)
    )

class GoldenCross(bt.Strategy):
    def __init__(self, setting, size):
        self.orderpct = float(size)
        self.fast_moving_average = bt.indicators.SMA(self.data.close, period=setting[0])
        self.slow_moving_average = bt.indicators.SMA(self.data.close, period=setting[1])
        self.crossover = bt.indicators.CrossOver(self.fast_moving_average, self.slow_moving_average)

    def next(self):
        if self.crossover > 0:
            self.order = self.order_target_percent(target=self.orderpct)
        elif self.crossover < 0:
            self.order = self.order_target_percent(target=-self.orderpct)


class MACDstrat(bt.Strategy):
    def __init__(self, setting, size):
        self.orderpct = float(size)
        self.MACDhist = bt.indicators.MACDHisto(self.data, period_me1=setting[1],
                                                period_me2=setting[0], period_signal=setting[2])

    def next(self):
        if self.MACDhist.histo > 0 and self.MACDhist.histo[-1] <= 0:
            self.order = self.order_target_percent(target=self.orderpct)
        elif self.MACDhist.histo < 0 and self.MACDhist.histo[-1] >= 0:
            self.order = self.order_target_percent(target=-self.orderpct)


class BollingerBands(bt.Strategy):
    def __init__(self, setting, size):
        self.orderpct = float(size)
        self.open = self.data.close
        self.high = self.data.high
        self.low = self.data.low

        self.BB = bt.indicators.BollingerBands(self.data, period=setting[0], devfactor=setting[1])
        self.BBh = bt.indicators.BollingerBands(self.data, period=setting[0], devfactor=setting[1]/2)

        self.buysign = bt.indicators.CrossOver(self.open, self.BBh.lines.top)
        self.sellsign = bt.indicators.CrossOver(self.BBh.lines.bot, self.open)


    def next(self):
        if self.position:
            if self.position.size > 0 and self.low < self.BB.lines.mid:
                self.close()
            elif self.position.size > 0 and self.high > self.BB.lines.top:
                self.close()

            if self.position.size < 0 and self.high > self.BB.lines.mid:
                self.close()
            elif self.position.size < 0 and self.low < self.BB.lines.bot:
                self.close()

        elif not self.position:
            if self.buysign > 0:
                self.order_target_percent(target=self.orderpct)

            if self.sellsign > 0:
                self.order_target_percent(target=-self.orderpct)


class RSIstrat(bt.Strategy):
    def __init__(self, setting, size):
        self.orderpct = float(size)

        self.RSIval = bt.indicators.RSI(self.data, period = setting[0])
        self.OBcross = bt.indicators.CrossOver(self.RSIval, 70)
        self.OScross = bt.indicators.CrossOver(self.RSIval, 30)

    def next(self):
        if self.position:
            if self.position.size > 0 and self.OBcross > 0:
                self.close()
            if self.position.size < 0 and self.OScross < 0:
                self.close()

        if not self.position:
            if self.OScross > 0:
                self.order_target_percent(target=self.orderpct)
            if self.OBcross < 0:
                self.order_target_percent(target=-self.orderpct)


class StochRSIstrat(bt.Strategy):
    def __init__(self, setting, size):
        self.orderpct = float(size)

        self.Stoch = bt.indicators.Stochastic(self.data, period=setting[0],
                                              period_dfast=setting[1], period_dslow=setting[2])
        self.RSIcross = bt.indicators.CrossOver(self.Stoch.percK, self.Stoch.percD)

    def next(self):
            if self.RSIcross > 0:
                self.order_target_percent(target=-self.orderpct)
            if self.RSIcross < 0:
                self.order_target_percent(target=self.orderpct)

def doBacktest(ticker, period, interval, settings, indicators, size, fee):
    tempsettings = dict(zip(indicators, settings.replace(' ', '').replace('(', '').replace(')', '').split(';')))
    settings = {}
    if type(tempsettings) is dict:
        for key, value in tempsettings.items():
            temp = value.split(',')
            settings[key] = [int(item) for item in temp if item.isdigit()]
            setting = DP.getArgs(settings, indicators[0])

    stratdict = {
        'SMA': GoldenCross,
        'BB': BollingerBands,
        'RSI': RSIstrat,
        'sRSI': StochRSIstrat,
        'MACD': MACDstrat
    }

    data = getTicker(ticker, period, interval)
    colnames = ['open', 'high', 'low', 'close', 'volume', 'datetime']
    data.columns = colnames

    cerebro = bt.Cerebro()

    df = PandasData(dataname=data)
    cerebro.adddata(df)

    cerebro.broker.set_cash(1000000)
    cerebro.broker.setcommission(commission=float(fee))
    cerebro.addstrategy(stratdict[indicators[0]], setting, size)

    cerebro.addanalyzer(btanalyzers.Transactions, _name='ransactions')
    if interval < 5:
        res = [1, 5, 15, 30, 60][interval-1]
        cerebro.addanalyzer(btanalyzers.TimeReturn, timeframe=bt.TimeFrame.Minutes, compression=1, _name='Rturns')
    else:
        cerebro.addanalyzer(btanalyzers.TimeReturn, _name='Rturns')

    result = cerebro.run()
    results = result[0]
    trades = results.analyzers.ransactions.get_analysis()
    returns = results.analyzers.Rturns.get_analysis()

    return cerebro.broker.getvalue(), trades, returns
