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


mapbox_access_token = 'pk.eyJ1IjoiZGJvc3RvbmMiLCJhIjoiY2p3NWhibWcxMXN2bjQzcXFmdmZhejBrcyJ9.4yN_W6nIO8TlXX9_vWq1qw'


banks = pd.read_csv(os.getcwd() + '/sample.csv')
top_banks = banks.groupby('namefull')[['rssdhcr']].count().reset_index().sort_values(by='rssdhcr')['namefull'].tolist()[-10:]
banks = banks[(banks['namefull'].isin(top_banks))].reset_index(drop=True)

app = dash.Dash(__name__)
server=app.server
app.layout = html.Div([
#     html.Div([
#         html.Div([
#             html.Label(children=['Bank: ']),
# #             style=blackbold
            dcc.Checklist(id='bank_name',
                         options=[{'label':str(b),'value':b} for b in sorted(banks['namefull'].unique())],
                         value=[b for b in sorted(banks['namefull'].unique())],
#                           value=None,
                         ),
#             html.Br(),
#             html.Label(['Website:']),
# #             style=blackbold
#             html.Pre(id='web_link',children=[],
#                     style={'white-space':'pre-wrap','word-break':'break-all',
#                           'border':'1px solid black','text-align':'center',
#                           'padding':'12px 12px 12px 12px','color':'blue',
#                           'margin-top':'3px'}
#                     ),
#         ],className='three columns'
#         ),
#         html.Div([
            dcc.Graph(id='graph-banks'
            ,config={'displayModeBar':False,'scrollZoom':True},
             style={'background':'#00FC87','padding-bottom':'2px','padding-left':'2px','height':'100vh'}
             )
#         ],className='nine columns'
#         ),
#     ],className='row'
#     ),
# ],className='ten columns offset-by-one'
])

@app.callback(Output('graph-banks','figure'),
            [Input('bank_name','value')])

def update_figure(chosen_bank):
    df_sub = banks[(banks['namefull'].isin(chosen_bank))]
    locations = [go.Scattermapbox(
        lon = df_sub['sims_longitude'],
        lat = df_sub['sims_latitude'],
        mode='markers',
        marker={'color':'black'},
        hoverinfo='text',
        hovertext=df_sub['namefull']
    )]
    return {
        'data':locations,
        'layout':go.Layout(
            uirevision='foo',
            clickmode='event+select',
            hovermode='closest',
            hoverdistance=2,
            title=dict(text="Bank Zips",font=dict(size=20,color='black')),
            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=25,
                style='light',
                center=dict(
                    lat=df_sub['sims_latitude'].median(),
                    lon=df_sub['sims_longitude'].median()),
            pitch=40,
            zoom=11.5,
            # width=1600,
            # height=800
            ),
        )
    }
# @app.callback(
#     Output('web_link','children'),
#     [Input('graph','clickData')])
#
# def display_click_data(clickData):
#     if clickData is None:
#         return 'Click on any bubble'
#     else:
#         the_link = clickData['points'][0]['customdata']
#         if the_link is None:
#             return 'No Website Available'
#         else:
#             return html.A(the_link,href=the_link,target="_blank")
app.run_server(debug=True)
