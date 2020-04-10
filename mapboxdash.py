import pandas as pd
import numpy as np
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import os
import plotly.express as px
import plotly.offline as py
import plotly.graph_objs as go
import flask
import random

import sys


mapbox_access_token = 'pk.eyJ1IjoiZGJvc3RvbmMiLCJhIjoiY2p3NWhibWcxMXN2bjQzcXFmdmZhejBrcyJ9.4yN_W6nIO8TlXX9_vWq1qw'



banks = pd.read_csv(os.getcwd() + '/2019banks.csv')
bank_color = {}
for bank in banks['namehcr'].unique():
    bank_color.update({bank:np.random.rand()*random.choice([-1,1])})
banks['zcta5_firm_specific'] = banks['namehcr'].map(bank_color)

for col in banks.columns.values:
    if 'zcta5_' in col:
        banks[col] = banks[col].fillna(0).astype(float)
        if 'zcta5_firm_specific' not in col:
            banks[col+'scaled'] = (banks[col]-banks[col].mean())/banks[col].std()
        else:
            banks[col+'scaled'] = banks[col]
        banks[col+'scaled'] = np.where(banks[col+'scaled']>1,1,np.where(banks[col+'scaled']<-1,-1,banks[col+'scaled']))

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)

app.layout = html.Div([

            dcc.Dropdown(id='bank_name',
                         options=[{'label':str(b),'value':b} for b in sorted(banks['namehcr'].unique())],
                         # value=[b for b in sorted(banks['namehcr'].unique())],
                         value=[sorted(banks['namehcr'].unique())[0]],
                         multi=True
#                           value=None,
                         ),
            dcc.Dropdown(id='demo_name',
                         options=[{'label':str(c).replace('zcta5_',''),'value':c} for c in [col for col in banks.columns.values if 'zcta5_' in col and 'scaled' not in col]],
                         # value=[b for b in sorted(banks['namehcr'].unique())],
                         value=[col for col in banks.columns.values if 'zcta5_' in col and 'scaled' not in col],
                         multi=False
                         ),
            dcc.Graph(id='graph-banks'
            ,config={'displayModeBar':False,'scrollZoom':True},
             style={'background':'#00FC87','padding-bottom':'2px','padding-left':'2px','height':'100vh'}
             )

])

@app.callback(Output('graph-banks','figure'),
            [Input('bank_name','value'),Input('demo_name','value')])

def update_figure(chosen_bank,demo_name):
    df_sub = banks[(banks['namehcr'].isin(chosen_bank))]
    locations = [go.Scattermapbox(
        lon = df_sub['sims_longitude'],
        lat = df_sub['sims_latitude'],
        mode='markers',
        marker=dict(
        # size=16,
        cmax=1,
        cmin=-1,
        color=df_sub[demo_name[0]+'scaled' if type(demo_name) is list else demo_name+'scaled'],
        colorbar=dict(
            title="Colorbar"),
        colorscale="Viridis"
        ),
        hoverinfo='text',
        hovertext=df_sub['namehcr'] + '<br>' + str(demo_name[0].replace('zcta5_','') if type(demo_name) is list else demo_name.replace('zcta5_','')) +": " + df_sub[demo_name[0] if type(demo_name) is list else demo_name].map(str)
    )]
    return {
        'data':locations,
        'layout':go.Layout(
            uirevision='foo',
            clickmode='event+select',
            hovermode='closest',
            hoverdistance=2,
            title=dict(text="Bank Branch Locations",font=dict(size=20,color='black')),
            mapbox=dict(
                layers=[],
                accesstoken=mapbox_access_token,
                bearing=25,
                style='light',
                center=dict(
                    lat=df_sub['sims_latitude'].median(),
                    lon=df_sub['sims_longitude'].median()),
            pitch=40,
            zoom=5,
            # width=1600,
            # height=800
            ),
        )
    }
if __name__ == '__main__':
    app.run_server(debug=True)
