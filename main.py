import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import yfinance as yf
import plotly.graph_objs as go
from IPython.display import display, clear_output
import time
import pandas as pd

# Define moving average crossover function
def moving_average_crossover(data, short_window=10, long_window=20):
    signals = pd.DataFrame(index=data.index)
    signals['Price'] = data['Close']

    signals['Short_MA'] = data['Close'].rolling(window=short_window, min_periods=1, center=False).mean()
    signals['Long_MA'] = data['Close'].rolling(window=long_window, min_periods=1, center=False).mean()

    signals['Signal'] = signals['Short_MA'] > signals['Long_MA']
    signals['Buy_Signal'] = signals['Signal'] & ~signals['Signal'].shift(1).fillna(False)
    signals['Sell_Signal'] = ~signals['Signal'] & signals['Signal'].shift(1).fillna(False)

    return signals

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div(
   [
      html.H2("Real-Time Bitcoin Price with Moving Average Crossover"),
      dcc.Graph(id="live-candlestick-graph"),
      dcc.Interval(id="graph-update", interval=60 * 1000, n_intervals=0),  # Update every 60 seconds
   ]
)

# Callback function to update the candlestick chart
@app.callback(Output("live-candlestick-graph", "figure"), [Input("graph-update", "n_intervals")])
def update_candlestick_graph(n):
    ticker = "BTC"
    data = yf.download(ticker, period="5d", interval="5m")
    signals = moving_average_crossover(data)

    candlestick_trace = go.Candlestick(x=data.index,
                                        open=data['Open'],
                                        high=data['High'],
                                        low=data['Low'],
                                        close=data['Close'],
                                        name='Candlestick Data')

    short_ma_trace = go.Scatter(x=signals.index,
                                y=signals['Short_MA'],
                                mode='lines',
                                name='Short-term MA',
                                line=dict(color='orange'))

    long_ma_trace = go.Scatter(x=signals.index,
                               y=signals['Long_MA'],
                               mode='lines',
                               name='Long-term MA',
                               line=dict(color='green'))

    buy_signal_trace = go.Scatter(x=signals[signals['Buy_Signal']].index,
                                  y=signals['Price'][signals['Buy_Signal']],
                                  mode='markers',
                                  marker=dict(symbol='triangle-up', size=10, color='green'),
                                  name='Buy Signal')

    sell_signal_trace = go.Scatter(x=signals[signals['Sell_Signal']].index,
                                   y=signals['Price'][signals['Sell_Signal']],
                                   mode='markers',
                                   marker=dict(symbol='triangle-down', size=10, color='red'),
                                   name='Sell Signal')

    fig = go.Figure(data=[candlestick_trace, short_ma_trace, long_ma_trace, buy_signal_trace, sell_signal_trace])

    fig.update_layout(title='NIFTY 50 with Moving Average Crossover Strategy',
                      xaxis_title='Date',
                      yaxis_title='Price',
                      xaxis_rangeslider_visible=False,
                      showlegend=True)

    return fig

if __name__ == "__main__":
    app.run(debug=True, port=8057)
