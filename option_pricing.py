from dash import Dash, dcc, html, Input, Output, State
import numpy as np
import datetime
from jugaad_data.nse import NSELive
from pprint import pprint
n = NSELive()


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
    # url = "https://www.nseindia.com/api/option-chain-indices?symbol={}".format(symbol)
    # headers={'User-Agent' : 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'}
    # response = requests.get(url, headers=headers, timeout=10)
    # print(response)
    global json_object
    # json_object = json.loads(response.text)

    json_object = n.index_option_chain(symbol)

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
            html.P("Last Updated: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        ])
    else:
        return html.P("Enter the values")


def calculate_business_days_to_date(selected_date, holidays=[]):
    """
    Calculates the difference in business days between today and a selected date.
    """

    today = datetime.date.today()  # Ensure date-only objects are used
    business_days = 0

    business_days = np.busday_count(today, selected_date, holidays=holidays)

    return abs(business_days)


# Placeholder function for now
def option_pricing_calculations(underlying, expiry):
    symbol = underlying
    r = 0.0711                                           
    n = 8     
    T = datetime.datetime.strptime(expiry, "%d-%b-%Y").date()
    T = calculate_business_days_to_date(T)
    underlyingValue = json_object["records"]["underlyingValue"]
    
    strikePrice = []
    PutLastPrice = []
    CallLastPrice = []
    PutIV = []
    CallIV = []

    if underlying=="NIFTY":
        L,H=20000,22000
    else:
        L,H=33000,55000

    for option_data in json_object['records']['data']:

        strike_price = option_data['strikePrice']

        # Only append details for strike prices above the threshold
        if strike_price >= L and strike_price <= H and option_data['expiryDate']==expiry:
            strikePrice.append(strike_price)

            if 'PE' in option_data:
                pe_last_price = option_data['PE']['lastPrice']
                pe_implied_volatility = option_data['PE']['impliedVolatility']  # Access implied volatility
                PutLastPrice.append(pe_last_price)
                PutIV.append(pe_implied_volatility)
            else:
                PutLastPrice.append(0)
                PutIV.append(0)

            if 'CE' in option_data:
                ce_last_price = option_data['CE']['lastPrice']
                ce_implied_volatility = option_data['CE']['impliedVolatility']  # Access implied volatility
                CallLastPrice.append(ce_last_price)
                CallIV.append(ce_implied_volatility)
            else:
                CallLastPrice.append(0)
                CallIV.append(0)


    # for i in range(len(json_object["records"]["data"])):
    #     if (json_object["records"]["data"][i]["expiryDate"]==expiry):  # for bankNifty it has to change
    #         strike_price.append(json_object["records"]["data"][i]["strikePrice"]) 
    #         actual_put.append(json_object["records"]["data"][i]["PE"]["lastPrice"])  # There are some empty values, do some change
    #         actual_call.append(json_object["records"]["data"][i]["CE"]["lastPrice"])
    #         iv_call.append(json_object["records"]["data"][i]["CE"]["impliedVolatility"])
    #         iv_put.append(json_object["records"]["data"][i]["PE"]["impliedVolatility"])

                
    calc_call = binomial_option_prices(underlyingValue,strikePrice,r,T,CallIV,n,"call")  
    calc_put = binomial_option_prices(underlyingValue,strikePrice,r,T,PutIV,n,"put") 

    # calc_call = np.zeros(len(strikePrice)) 
    # calc_put = np.zeros(len(strikePrice))   


    arr = (np.column_stack((CallLastPrice, calc_call, strikePrice, PutLastPrice, calc_put)))
    return arr

def binomial_option_prices(S, X_values, r, T, volatility_values, n, option_type):
    prices = []
    for X in X_values:
        option_prices = []
        for volatility in volatility_values:
            delta_t = T / n
            u = math.exp(volatility * math.sqrt(delta_t))
            
            d = 1 / u
            print(volatility,math.sqrt(delta_t),u,d)
            # ############## it shows divide by 0 error, so added these
            # if not (u-d):
            #     break
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
    print(option_prices)
    return prices

if __name__ == "__main__":
    app.run_server(debug=True)
