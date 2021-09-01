This dashboard is split into two sections.
In the Main Dashboard, one can graph the candles of a ticker, and apply indicators for technical analysis.
These indicators are derived using the technical analysis library, ta, while the data for the ticker is fetched using
the library, yfinance.
Further customizations of the indicators are possible, as the default parameters for an indicator can be overwritten.

In the Back Testing dashboard, one indicator can be applied to a ticker, which has a trading strategy bound to it.
With this, a back test can be performed that shows how a portfolio, with a starting value of 1.000.000, evolves from
following the given strategy. For the back test, a decimal number is inputted, which is the parameter for how much of
the portfolio value will be invested when a signal is triggered

The back test is simulated using the Back Trader library, where each strategy allows for both long and short positions.
Whenever a trade signal is triggered, position will be taken at the following period open.

The back test simulation is quite simple and further work could include the following:
    Selecting restrictions regarding the direction of positions taken.
    Allowing for strategies to include multiple indicators, either by adding all the rules for decision-making together,
        or by writing individual strategies from scratch for different permutations of indicators in use.
    Adding a table with statistical insights to the back test performance.
    Adding a buy and hold strategy as benchmark.
