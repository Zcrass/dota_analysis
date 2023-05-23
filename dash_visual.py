#!/usr/bin/env python

from dash import Dash, dcc, html
import json
import logging as lg
import sys

from utils.dota_data_utils import DotaData 
import utils.dota_plots_utils as dota_plots_utils 

def main():
    data = DotaData(**args['dota_data'])
    app = Dash(__name__)
    app.layout = html.Div(
        children = [
            html.H1('Dota 2 statistics'),
            html.P(children=(f'Analisis of Dota data matches based on data from {len(data.match_data_stored_matches)} matches')),
            html.P(children=(f'Data was collected from the OpenDota API')),
            html.H2('Matches duration by mmr rank'),
            html.Div([
                dcc.Graph(figure=dota_plots_utils.duration_hist(data), 
                          style={'width': '50%', 'display': 'inline-block'}),
                dcc.Graph(figure=dota_plots_utils.duration_box(data), 
                          style={'width': '50%', 'display': 'inline-block'}),                
            ]),
            html.Div([
                dcc.Graph(figure=dota_plots_utils.heroes_heatmap(data),
                          style={'width': '50%', 'display': 'inline-block'}),
                dcc.Graph(figure=dota_plots_utils.heroes_wlr_heatmap(data),
                          style={'width': '50%', 'display': 'inline-block'}),
            ])
        ]
    )
    app.run_server(debug=True)

if __name__ == '__main__':
    ### define logger
    lg.basicConfig(filename='logs/dash_visual.log', filemode='a',
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=lg.INFO)
    logger = lg.getLogger()
    stdout_handler = lg.StreamHandler(sys.stdout)
    logger.addHandler(stdout_handler)
    ### read config file
    args = json.load(open('dota_data_config.json'))
    ### running main app
    main()