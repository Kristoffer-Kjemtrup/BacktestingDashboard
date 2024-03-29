import dash
import dash_core_components as dcc
import dash_html_components as html

periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max', 'Custom']
intervals = ['1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo', '3mo']

layout = html.Div([
    html.Div([
        html.Div([
            html.Div('Ticker'),
            dcc.Input(
                id='MainDash-symbol',
                type='text',
                value='',
                style={'width': '100%'}
            ),
            html.Div('Period'),
            dcc.Slider(
                id='MainDash-selPeriod',
                min=0,
                max=11,
                marks={i: periods[i] for i in range(len(periods))},
                value=5,
            ),
        ], style={'width': '50%', 'display': 'inline-block'}),

        html.Div([
            html.Div('Select indicator(s)'),
            dcc.Dropdown(
                id='MainDash-indicators',
                placeholder='[n] available arguments' +
                            ' - if one or more arguments are missing, the default is chosen',
                options=[
                    {'label': 'Bollinger Bands [2]', 'value': 'BB'},
                    {'label': 'Moving Average Convergence Divergence [3]', 'value': 'MACD'},
                    {'label': 'Relative Strength Index [3]', 'value': 'RSI'},
                    {'label': 'Stochastic RSI [3]', 'value': 'sRSI'},
                    {'label': 'Simple Moving Average [2]', 'value': 'SMA'}
                ],
                multi=True,
                value=''
            ),
            html.Div('Interval'),
            dcc.Slider(
                id='MainDash-selInterval',
                min=0,
                max=8,
                marks={i: intervals[i] for i in range(len(intervals))},
                value=5,
            ),
        ], style={'width': '50%', 'float': 'right', 'display': 'inline-block'})
    ]),

    html.Div('Specify parameters for indicators:',
             style={'font-weight': 'bold'}),
    html.Div('Specify each indicator inside a set of parenthesis. separate arguments by , and indicators by ;'),

    dcc.Input(id='MainDash-settings',
              type='text',
              placeholder='Ie. (26, 12, 9); (30, 50)',
              value='',
              style={'width': '100%'}
              ),

    html.Br(),
    dcc.Graph(id='MainDash-symbol-graph',
              style={"height": "70vh"}),
])


