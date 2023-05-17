#!/usr/bin/env python

from dash import Dash, dcc, html
import json
import logging as lg
import sys

from dota_utils import DotaData, TeamsData
import dota_plots 
def main():
    data = DotaData(**args['matchs_api'])
    # print(data.match_data.columns)
    app = Dash(__name__)
    app.layout = html.Div(
        children = [
            html.H1('Dota alytics'),
            html.P(children=('Analisis of Dota data matches')),
            html.H2('Matches duration by mmr rank'),
            html.Div([
                dcc.Graph(figure=dota_plots.duration_hist(data), 
                          style={'width': '50%', 'display': 'inline-block'}),
                dcc.Graph(figure=dota_plots.duration_box(data), 
                          style={'width': '50%', 'display': 'inline-block'}),                
            ]),
            html.Div([
                dcc.Graph(figure=dota_plots.heroes_heatmap(data)),

            ])
        ]
    )
    app.run_server(debug=True)

if __name__ == '__main__':
    ### define logger
    lg.basicConfig(filename='data_collector.log', filemode='w',
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=lg.INFO)
    logger = lg.getLogger()
    stdout_handler = lg.StreamHandler(sys.stdout)
    logger.addHandler(stdout_handler)
    ### read config file
    args = json.load(open('data_transform_config.json'))
    ### running main app
    main()