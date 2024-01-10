from dash import Dash, dcc, html, Input, Output, callback, State
import numpy as np
from datetime import datetime

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Welcome to Mathematical Option Pricing and Comparison Tool"),
    html.H3("ProfNITT"),
    html.Div([
        dcc.Dropdown(
            id="select-underlying",
            options=[
                {"label": "NIFTY", "value": "NIFTY"},
                {"label": "BANK NIFTY", "value": "BANK NIFTY"}
            ],
            placeholder="Select Underlying"
        ),
        dcc.Input(id="enter-expiry", placeholder="Enter Expiry (in days)"),
        html.Button("Run", id="run-button")
    ]),
    html.Div(id="output-div")
])

@callback(
    Output("output-div", "children"),
    [Input("run-button", "n_clicks")],
      [State("select-underlying", "value"),
       State("enter-expiry", "value")])
def calculate_option_price(n_clicks, underlying, expiry):
    # Placeholder for external calculation logic
    results = perform_option_pricing_calculations(underlying, expiry)
    print(results)
    return html.Div([
        html.Table([
            html.Thead(html.Tr([
                html.Th("Actual"),
                html.Th("Calculated"),
                html.Th("Strike Price"),
                html.Th("Actual"),
                html.Th("Calculated")
            ])),
            html.Tbody([
                html.Tr([html.Td(x) for x in row]) for row in results
            ])
        ]),
        html.P("Last Updated: {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    ])
       

# Placeholder function for now
def perform_option_pricing_calculations(underlying, expiry):
    return np.random.rand(50, 3)  # Replace with actual calculation logic

# app.css.append_css({"external_url": "https://path/to/your/external.css"})  # Link your CSS file

if __name__ == "__main__":
    app.run_server(debug=True)
