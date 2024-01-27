from dash import Dash, dcc, html, Input, Output, State
import numpy as np
import datetime
from jugaad_data.nse import NSELive
from pprint import pprint
n = NSELive()
from scipy.stats import norm


import requests
import json
import math

# symbol="NIFTY"


app = Dash(__name__, title='Option Pricing Tool')

app.layout = html.Div(style={'backgroundColor': '#6399EB'},
                      children=[

                        #   html.Div([
                        #       html.Img(className="logo", src='/assets/image.png')
                        #   ]),

                          html.Div(
                              className="header",
                              children=[
                                  html.Span('Welcome to Mathematical Option Pricing and Comparison Tool',
                                            className="header--title"),html.Img(className="logo", src='/assets/image.png')
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
    # print(business_days)
    return abs(business_days)


# Placeholder function for now
def option_pricing_calculations(underlying, expiry):
    symbol = underlying
    r = 0.0711                                           
    n = 4     
    T1 = datetime.datetime.strptime(expiry, "%d-%b-%Y").date()
    T = calculate_business_days_to_date(T1)
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

    calc_call = []
    calc_put = []

    for i in range(len(strikePrice)):
        calc_put.append(blackScholes(r, underlyingValue, strikePrice[i], T/365, PutIV[i]/100, type='P'))
        calc_call.append(blackScholes(r, underlyingValue, strikePrice[i], T/365, CallIV[i]/100, type='C'))

    # print(blackScholes(r, underlyingValue, 20100, T, CallIV[2], type='C'))
 
    arr = (np.column_stack((CallLastPrice, calc_call, strikePrice, PutLastPrice, calc_put)))
    return arr


def blackScholes(r, S, K, T, sigma, type='C'):
    if sigma == 0:
        return ('ILLIQUIDITY')
        
    else:

        d1 = (np.log(S/K) + (r + (sigma**2)/2)*T)/(sigma*np.sqrt(T))
        d2 = d1 - sigma*np.sqrt(T)
        try:
            if (type == 'C'):
                price = S*norm.cdf(d1, 0, 1) - K*np.exp(-r*T)*norm.cdf(d2, 0, 1)
            elif (type == 'P'):
                price = K*np.exp(-r*T)*norm.cdf(-d2, 0, 1) - S*norm.cdf(-d1, 0, 1)
            return (round(price,2))
        except:
            print("Please enter C or P for Call & Put options respectively")




if __name__ == "__main__":
    app.run_server(debug=True)
