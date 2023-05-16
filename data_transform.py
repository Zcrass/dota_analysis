#!/usr/bin/env python

import json
import logging as lg
import pandas as pd 
import sys
import time
from data_transform_utils import DotaData, TeamsData

def main():
    data = DotaData(**args['matchs_api'])
    ### QUITAR MATCHES QUE YA ESTÁN GUARDADOS
    stored_matches = data.hbym_data_stored_matches
    for id in data.match_data.match_id:
        logger.info(f'transforming data from match {id}')
        t_data = TeamsData(dota_data=data, match_id=id)
        t_data.submit_data()



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
    