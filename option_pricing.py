from dash import Dash, dcc, html, Input, Output, State
import numpy as np
from datetime import datetime, date

import requests
import json
import math

# symbol="NIFTY"


app = Dash(__name__, title='Option Pricing Tool')

app.layout = html.Div(style={'backgroundColor': '#6399EB'},
                      children=[

                          html.Div([
                              html.Img(className="logo", src='/assets/image.png')
                          ]),

                          html.Div(
                              className="header",
                              children=[
                                  html.Span('Welcome to Mathematical Option Pricing and Comparison Tool',
                                            className="header--title")
                              ]
                          ),
                          html.Div(
                              className="inputs",
                              children=[
                                  dcc.Dropdown(
                                      id="select-underlying",
                                      options=[
                                          {"label": "NIFTY", "value": "NIFTY"},
                                          {"label": "BANKNIFTY", "value": "BANKNIFTY"}
                                      ],
                                      placeholder="Select Underlying",
                                      className="inputs--drop"
                                  ),
                                  html.Button("RunSymbol", id="run-symbol", className="inputs--run"),
                                  dcc.Dropdown(id='select-time',placeholder="Select Time to Expiry",className="inputs--date"),
                                  html.Button("RunTime", id="run-time", className="inputs--run"),
                              ]),
                          html.Div(id="output-div", className="outputs")
                      ])


@app.callback(
    Output("select-time", "options"),
    [Input("run-symbol", "n_clicks")],
    [State("select-underlying", "value")],
    prevent_initial_call=True)

def create_expiry_dates(n_clicks,symbol):
    url = "https://www.nseindia.com/api/option-chain-indices?symbol={}".format(symbol)
    headers={'User-Agent' : 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'}
    response = requests.get(url, headers=headers, timeout=10)
    print(response)
    global json_object
    json_object = json.loads(response.text)
    expiryDates = json_object["records"]["expiryDates"]
    return expiryDates


@app.callback(
    Output("output-div", "children"),
    [Input("run-time", "n_clicks")],
    [State("select-underlying", "value"),
     State("select-time", "value")],
    prevent_initial_call=True)

def calculate_option_price(n_clicks, underlying, expiry):
    if underlying and expiry:
        # Placeholder for external calculation logic
        results = option_pricing_calculations(underlying, expiry)
        return html.Div([
            html.Table([
                html.Thead([html.Tr([
                    html.Th(colSpan=2, children='CALL'),
                    html.Th(rowSpan=2, children="Strike Price"),
                    html.Th(colSpan=2, children='PUT'),
                ]), html.Tr([html.Th("Actual"),
                             html.Th("Calculated"), html.Th("Actual"),
                             html.Th("Calculated")])]),
                html.Tbody([
                    html.Tr([html.Td(x) for x in row]) for row in results
                ])
            ]),
            html.P("Last Updated: {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        ])
    else:
        return html.P("Enter the values")

def days_between(d1):
    d2 = datetime.strptime(str(datetime.today().date()), "%Y-%m-%d")
    return abs((d2 - d1).days)

def option_pricing_calculations(underlying, expiry):
    symbol = underlying
    r = 0.0711                                           
    n = 8     
    T = datetime.strptime(expiry, "%d-%b-%Y")
    T = days_between(T)
    underlyingValue = json_object["records"]["data"][0]["PE"]["underlyingValue"]
    
    strike_price = []  # From API
    actual_call = []  # Get from downloaded JSON file from API
    actual_put = []  # Get from downloaded JSON file from API
    iv_call =[]
    iv_put =[]

    for i in range(len(json_object["records"]["data"])):
        if json_object["records"]["data"][i]["expiryDate"]==expiry and json_object["records"]["data"][i]["strikePrice"]>=22000:  # for bankNifty it has to change
            strike_price.append(json_object["records"]["data"][i]["strikePrice"]) 
            actual_put.append(json_object["records"]["data"][i]["PE"]["lastPrice"])  # There are some empty values, do some change
            actual_call.append(json_object["records"]["data"][i]["CE"]["lastPrice"])
            iv_call.append(json_object["records"]["data"][i]["CE"]["impliedVolatility"])
            iv_put.append(json_object["records"]["data"][i]["PE"]["impliedVolatility"])

                
    calc_call = binomial_option_prices(underlyingValue,strike_price,r,T,iv_call,n,"call")  
    calc_put = binomial_option_prices(underlyingValue,strike_price,r,T,iv_put,n,"put")   
    arr = (np.column_stack((actual_call, calc_call, strike_price, actual_put, calc_put)))
    return arr

def binomial_option_prices(S, X_values, r, T, volatility_values, n, option_type):
    prices = []
    for X in X_values:
        option_prices = []
        for volatility in volatility_values:
            delta_t = T / n
            u = math.exp(volatility * math.sqrt(delta_t))
            d = 1 / u
            ############## it shows divide by 0 error, so added these
            if not (u-d):
                break
            p = (math.exp(r * delta_t) - d) / (u - d)
            discount_factor = math.exp(-r * delta_t)

            stock_prices = []
            for i in range(n + 1):
                stock_price = S * (u ** (n - i)) * (d ** i)
                stock_prices.append(stock_price)

            option_values = []
            for stock_price in stock_prices:
                if option_type == "call":
                    option_value = max(stock_price - X, 0)
                else:
                    option_value = max(X - stock_price, 0)
                option_values.append(option_value)

            for i in range(n):
                option_values_next = []
                for j in range(len(option_values) - 1):
                    option_value = (p * option_values[j] + (1 - p) * option_values[j + 1]) * discount_factor
                    option_values_next.append(option_value)
                option_values = option_values_next

            option_prices.append(option_values[0])

        prices.append(option_prices[0])

    return prices

if __name__ == "__main__":
    app.run_server(debug=True)
