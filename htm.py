# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


from dash import Dash, html
import pandas as pd
import numpy as np

# df = pd.read_csv('https://gist.githubusercontent.com/chriddyp/c78bf172206ce24f77d6363a2d754b59/raw/c353e8ef842413cae56ae3920b8fd78468aa4cb2/usa-agricultural-exports-2011.csv')
SP = np.arange(19000,25000,100)
Bs_C, Bi_C = np.arange(1400,7400,100),np.arange(1400,7400,100)
Bs_P, Bi_P = np.arange(7400,1400,-100),np.arange(7400,1400,-100)
LTP_P, LTP_C = np.arange(1400,7400,100), np.arange(1400,7400,100)
IV_C, IV_P = np.arange(40,100), np.arange(40,100)
B_H = np.zeros(60)
l = [IV_P, Bs_P, Bi_P, LTP_P, SP, LTP_C, Bi_C, Bs_P, IV_C, B_H]

def generate_table():
    return html.Table([
        html.Thead(html.Tr([
            html.Th('IV_P'),
            html.Th('Bi_P'),
            html.Th('Bs_P'),
            html.Th('LTP_P'),
            html.Th('SP'),
            html.Th('LTP_C'),
            html.Th('Bs_C'),
            html.Th('Bi_C'),
            html.Th('IV_C'),
            # html.Th('B/H'),
        ])),
            html.Tbody(
                [html.Tr([
                    html.Td(IV_P[i]),
                    html.Td(Bi_P[i]), 
                    html.Td(Bs_P[i]) ,
                    html.Td(LTP_P[i]) ,
                    html.Td(SP[i]) ,
                    html.Td(LTP_C[i]) ,
                    html.Td(Bs_C[i]) ,
                    html.Td(Bi_C[i]) ,
                    html.Td(IV_C[i]) ,
                    # html.Td(B_H[i]),
                ])for i in range(60)]
            )
        ]
    )


app = Dash(__name__)

app.layout = html.Div([
    html.H4(children='OPTION PRICE'),
    generate_table()
])

if __name__ == '__main__':
    app.run(debug=True)
