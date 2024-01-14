from dash import Dash, dcc, html, Input, Output, State
import numpy as np
from datetime import datetime, date

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
                                          {"label": "BANK NIFTY", "value": "BANK NIFTY"}
                                      ],
                                      placeholder="Select Underlying",
                                      className="inputs--drop"
                                  ),
                                  dcc.Input(
                                      id="select-time",
                                      type="number",
                                      placeholder="Select Time to Expiry",
                                      className="inputs--date"
                                  ),
                                  html.Button("Run", id="run-button", className="inputs--run")
                              ]),
                          html.Div(id="output-div", className="outputs")
                      ])


@app.callback(
    Output("output-div", "children"),
    [Input("run-button", "n_clicks")],
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


# Placeholder function for now
def option_pricing_calculations(underlying, expiry):
    # Run the API here and save the data

    strike_price = np.arange(21000, 22000, 100)  # From API
    actual_call = np.arange(1000, 2000, 100)  # Get from downloaded JSON file from API
    actual_put = np.arange(22000, 23000, 100)  # Get from downloaded JSON file from API

    # YourCode to run from the actual price and strike price
    calc_call = np.arange(22000, 23000, 100)  # You can just call your model here
    calc_put = np.arange(22000, 23000, 100)  # You can just call your model here

    arr = (np.column_stack((actual_call, calc_call, strike_price, actual_put, calc_put)))
    return arr


if __name__ == "__main__":
    app.run_server(debug=True)
