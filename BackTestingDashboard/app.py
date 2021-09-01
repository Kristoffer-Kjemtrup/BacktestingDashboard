import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash_extensions.enrich import DashProxy, MultiplexerTransform
from BackTestingDashboard.Processes import BackTradeBackEnd as BT, FigureCreator as FC
from BackTestingDashboard.Dashboard_layouts import BackTestDashboard, MainDashboard

app = DashProxy(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True,
                transforms=[MultiplexerTransform()])
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '16rem',
    'padding': '2rem 1rem',
    'background-color': '#f8f9fa',
}

CONTENT_STYLE = {
    'margin-left': '18rem',
    'margin-right': '2rem',
    'padding': '2rem 1rem',
}

sidebar = html.Div(
    [
        html.H2('Back testing Dash'),
        html.Hr(),
        html.P('Pick the Main Dashboard to inspect a ticker and apply technical indicators.'),
        html.P('Pick the Back Testing board to apply a simple trading strategy on a ticker'),
        dbc.Nav(
            [
                dbc.NavLink('Main Dashboard', href='/MainBoard', active='exact'),
                dbc.NavLink('Back Testing', href='/BackTest', active='exact'),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id='page-content', children=[], style=CONTENT_STYLE)

app.layout = html.Div([
    dcc.Location(id='url', pathname='/MainBoard'),
    sidebar,
    content
])


@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def render_page_content(pathname):
    if pathname == '/MainBoard':
        return [
                html.H1('Main Dashboard',
                        style={'textAlign': 'center'}),
                MainDashboard.layout]
    elif pathname == '/BackTest':
        return [
                html.H1('Back Testing',
                        style={'textAlign': 'center'}),
                BackTestDashboard.layout
                ]


@app.callback(
    Output('MainDash-symbol-graph', 'figure'),
    Input('MainDash-symbol', 'value'),
    Input('MainDash-selPeriod', 'value'),
    Input('MainDash-selInterval', 'value'),
    Input('MainDash-indicators', 'value'),
    Input('MainDash-settings', 'value')
)
def update_graph(symbol_value, period_value, interval_value, indicators, settings):
    figure = FC.CreateMainFig(symbol_value, period_value, interval_value, indicators, settings)
    return figure


@app.callback(
    Output('BackTest-symbol-graph', 'figure'),
    Input('BackTest-symbol', 'value'),
    Input('BackTest-selPeriod', 'value'),
    Input('BackTest-selInterval', 'value'),
    Input('BackTest-indicators', 'value'),
    Input('BackTest-settings', 'value')
)
def update_graph(symbol_value, period_value, interval_value, indicator, settings):
    figure = FC.CreateMainFig(symbol_value, period_value, interval_value, indicator.split(), settings)
    return figure


@app.callback(
    Output('BackTest-symbol-graph', 'figure'),
    Output('BackTest-return-graph', 'figure'),
    Output('BackTest-Backer', 'children'),
    Input('BackTest-Execute', 'n_clicks'),
    State('BackTest-symbol', 'value'),
    State('BackTest-selPeriod', 'value'),
    State('BackTest-selInterval', 'value'),
    State('BackTest-indicators', 'value'),
    State('BackTest-settings', 'value'),
    State('BackTest-investmentSize', 'value'),
    State('BackTest-BrokerFee', 'value'),
)
def getBacker(n, symbol_value, period_value, interval_value, indicator, settings, size, fee):
    if n is None:
        return dash.no_update

    bt_val, bt_trades, bt_returns = BT.doBacktest(symbol_value, period_value, interval_value, settings,
                                                  indicator.split(), size, fee)
    figures = FC.CreateMainFig(symbol_value, period_value, interval_value, indicator.split(), settings,
                               bt_returns=bt_returns, bt_trades=bt_trades)

    mainfig, returnfig = figures
    bt_val = f'Final portfolio value: {round(bt_val, 2):,}'

    return mainfig, returnfig, bt_val


if __name__ == '__main__':
    app.run_server(debug=True)
