#!/usr/bin/env python

import json
import logging as lg
import sys
import time
import pandas as pd 

from data_collector_utils import DataCollector, TeamsData
from dota_utils import DotaData 
def main():
    data_colector_options = args['data_collector']
    print(data_colector_options)
    if data_colector_options['collect_data'] == 'True':
        logger.info(f'Starting service')
        matches = DataCollector(**args['matchs_api'])
        matches.stored_matches = matches.get_matches_db()
        starttime = submittime = time.time()
        logger.info(f'Start time: {starttime}')
        c = 0
        while True:
            time.sleep(matches.api_get_wait_time)
            c += 1
            if not matches.new_data.empty:
                logger.info(f'Gatered {matches.new_data.shape[0]} matches data in {c} iterations')
            if (time.time() - starttime) > matches.api_get_uptime:
                break
            matches.new_data = matches.receive_matches()
            matches.stored_matches = matches.stored_matches + list(matches.new_data.match_id.values) 
            # if (time.time() - submittime) > matches.db_sumbmission_time:
            if matches.new_data.shape[0] > 0:
                matches.submit_data()
                matches.new_data = pd.DataFrame()
            #     submittime = time.time()
    if data_colector_options['update_data'] == 'True':    
        data = DotaData(**args['matchs_api'])
        stored_hbym = data.hbym_data_stored_matches
        stored_match = data.match_data_stored_matches
        if stored_match > stored_hbym:
            missing = []
            for match in stored_match:
                if match in stored_hbym:
                    pass
                else:
                    missing = missing + [match]
            logger.info(f'Updating {len(missing)} records')
            for n, id in enumerate(missing):
                logger.info(f'transforming data from match {id}')
                t_data = TeamsData(dota_data=data, match_id=id)
                for i in t_data.combined_teams.columns:
                    t_data.combined_teams[i] = t_data.combined_teams[i].astype(int) 
                logger.info(f'submiting match {n+1}/{len(missing)}...')
                t_data.submit_data()


if __name__ == '__main__':
    ### define logger
    lg.basicConfig(filename='data_collector.log', filemode='w',
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=lg.INFO)
    logger = lg.getLogger()
    stdout_handler = lg.StreamHandler(sys.stdout)
    logger.addHandler(stdout_handler)
    ### read config file
    args = json.load(open('dota_data_config.json'))
    ### running main app
    main()
    