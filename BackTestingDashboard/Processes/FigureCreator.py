import plotly.graph_objects as go
from plotly.subplots import make_subplots
from BackTestingDashboard.Processes import DataProcessing as DP


def CreateMainFig(symbol_value, period_value, interval_value, indicators, settings, bt_returns=0, bt_trades=0):
    if len(indicators) > 0:
        tempsettings = dict(zip(indicators, settings.replace(' ', '').replace('(', '').replace(')', '').split(';')))
        settings = {}
        if type(tempsettings) is dict:
            for key, value in tempsettings.items():
                temp = value.split(',')
                settings[key] = [int(item) for item in temp if item.isdigit()]

        data = DP.getTicker(symbol_value, period_value, interval_value, indicators, settings)
    else:
        data = DP.getTicker(symbol_value, period_value, interval_value, indicators)

    addrows = list(sorted(set(indicators).intersection(['MACD', 'sRSI', 'RSI'])))
    if not type(bt_returns) is int:
        addrows.append('Back test portfolio value')

    figure = make_subplots(rows=2 + len(addrows), cols=1, shared_xaxes=True,
                           vertical_spacing=0.03, subplot_titles=(['OHLC', 'Volume'] + addrows),
                           row_width=([0.4] * len(addrows) + [0.2, 0.7]))

    figure.add_trace(go.Candlestick(x=list(data.datetime),
                                    open=data['Open'],
                                    high=data['High'],
                                    low=data['Low'],
                                    close=data['Close'], name='Candles', showlegend=False), row=1, col=1)

    figure.add_trace(go.Bar(x=list(data.datetime), y=data.Volume, showlegend=False,
                            marker=dict(color=DP.getVolumeColor(data))), row=2, col=1)

    if 'SMA' in indicators:
        figure.add_traces(data=[go.Scatter(x=list(data.datetime), y=data.SMAshort, name='50 period SMA'
                                           if 'SMA' not in settings or len(settings['SMA']) == 0
                                           else f'{settings["SMA"][0]} period SMA', hoverinfo='none'),
                                go.Scatter(x=list(data.datetime), y=data.SMAlong, name='200 period SMA'
                                           if 'SMA' not in settings or len(settings['SMA']) < 2
                                           else f'{settings["SMA"][1]} period SMA', hoverinfo='none')],
                          rows=[1] * 2, cols=[1] * 2)

    if 'BB' in indicators:
        figure.add_traces(data=[go.Scatter(x=list(data.datetime), y=data.BB_higher, line=dict(width=1),
                                           marker=dict(color='#ccc'), legendgroup='Bollinger Bands',
                                           name='Bollinger Band[20, 2, 2] [upper]' if 'BB' not in settings
                                                                                      or len(settings['BB']) == 0
                                           else f'Bollinger Band{settings["BB"]} [upper]', hoverinfo='skip'),
                                go.Scatter(x=list(data.datetime), y=data.BB_lower, line=dict(width=1),
                                           marker=dict(color='#ccc'), legendgroup='Bollinger Bands',
                                           name='Bollinger Band[20, 2, 2] [lower]' if 'BB' not in settings
                                                                                      or len(settings['BB']) == 0
                                           else f'Bollinger Band{settings["BB"]} [lower]', hoverinfo='skip'),
                                go.Scatter(x=list(data.datetime), y=data.BB_mid, line=dict(width=1),
                                           marker=dict(color='#ccc'), legendgroup='Bollinger Bands',
                                           name='Bollinger Band[20] [SMA]' if 'BB' not in settings
                                                                              or len(settings['BB']) == 0
                                           else f'Bollinger Band[{settings["BB"][0]}] [SMA]',
                                           hoverinfo='skip')],
                          rows=[1] * 3, cols=[1] * 3)

    if 'RSI' in indicators:
        figure.add_traces(data=[go.Scatter(x=list(data.datetime), y=data.RSI, marker=dict(color='#4586b4'),
                                           name='RSI[14, 30, 70]' if 'RSI' not in settings or len(settings['RSI']) == 0
                                           else f'RSI {settings["RSI"]}'),
                                go.Scatter(x=list(data.datetime),
                                           y=[settings['RSI'][1] if 'RSI' in settings and len(settings['RSI']) > 1 else
                                              30] * len(data),
                                           line=dict(dash='dash', width=1),
                                           marker=dict(color='#f9b958'), hoverinfo='none', name='RSI[Upper]'),
                                go.Scatter(x=list(data.datetime),
                                           y=[settings['RSI'][2] if 'RSI' in settings and len(settings['RSI']) > 2 else
                                              70] * len(data),
                                           line=dict(dash='dash', width=1),
                                           marker=dict(color='#28ce97'), hoverinfo='none', name='RSI[Lower]')],
                          rows=[3 + addrows.index('RSI')] * 3, cols=[1] * 3)

    if 'sRSI' in indicators:
        figure.add_traces(data=[go.Scatter(x=list(data.datetime), y=data.sRSId, marker=dict(color='#67bbf6'),
                                           name='Stoch RSI[14, 3, 3]' if 'sRSI' not in settings
                                                                         or len(settings['sRSI']) == 0
                                           else f'Stoch RSI {settings["sRSI"]}'),
                                go.Scatter(x=list(data.datetime), y=data.sRSIk, marker=dict(color='#ff2812'),
                                           name='Stoch RSI[14, 3, 3]' if 'sRSI' not in settings
                                                                         or len(settings['sRSI']) == 0
                                           else f'Stoch RSI {settings["sRSI"]}'),
                                go.Scatter(x=list(data.datetime), y=[0.2] * len(data), line=dict(dash='dash', width=1),
                                           marker=dict(color='#f9b958'), hoverinfo='none', name='sRSI[Upper]'),
                                go.Scatter(x=list(data.datetime), y=[0.8] * len(data), line=dict(dash='dash', width=1),
                                           marker=dict(color='#28ce97'), hoverinfo='none', name='sRSI[Lower]')],
                          rows=[3 + addrows.index('sRSI')] * 4, cols=[1] * 4)

    if 'MACD' in indicators:
        figure.add_traces(data=[go.Scatter(x=list(data.datetime), y=data.MACD, marker=dict(color='black'),
                                           name='MACD[26, 12, 9]' if 'MACD' not in settings
                                                                     or len(settings['MACD']) == 0
                                           else f'MACD{settings["MACD"]}'),
                                go.Scatter(x=list(data.datetime), y=data.MACD_sign,
                                           marker=dict(color='red'),
                                           name='MACD[26, 12, 9] [Sign]' if 'MACD' not in settings
                                                                            or len(settings['MACD']) == 0
                                           else f'MACD{settings["MACD"]} [Sign]'),
                                go.Bar(x=list(data.datetime), y=data['MACD_hist'],
                                       name='MACD[26, 12, 9] [Hist]' if 'MACD' not in settings
                                                                        or len(settings['MACD']) == 0
                                       else f'MACD{settings["MACD"]} [Hist]',
                                       marker=dict(color=['#3fa93c' if data.MACD_hist[i] > 0 else '#ff6666'
                                                          for i in range(len(data.MACD_hist))]))],
                          rows=[3 + addrows.index('MACD')] * 3, cols=[1] * 3)

    if not type(bt_returns) is int:
        if not type(bt_trades) is int and len(bt_trades) > 0:
            marker_data = DP.getBackTestStats(data, bt_trades)
            figure.add_trace(go.Scatter(x=marker_data.date, y=marker_data.Marker, mode='markers', name='Trades',
                                        marker=go.Marker(size=14, symbol=marker_data.Symbol, color=marker_data.Color)),
                             row=1, col=1)

        return_data = DP.getBackTestReturns(bt_returns)
        figure.add_trace(go.Scatter(x=return_data.date, y=return_data.Return, name='Portfolio value'),
                         row=3+addrows.index('Back test portfolio value'), col=1)

    figure.update_xaxes(
        rangeslider_visible=False,
        rangebreaks=[
            dict(bounds=[16, 9.5], pattern="hour") if interval_value < 5 else dict(bounds=["sat", "mon"]),
            dict(bounds=["sat", "mon"])
        ])
    figure.update_layout(margin={'l': 40, 'b': 20, 't': 20, 'r': 0}, hovermode='closest')
    figure.layout.xaxis.type = 'category'

    return figure
