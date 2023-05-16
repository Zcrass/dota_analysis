#!/usr/bin/env python

import json
import logging as lg
import sys
import time
import pandas as pd 

from data_collector_utils import DataCollector
def main():
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
        # matches.new_data = pd.concat([matches.new_data, matches.receive_matches()])
        # if (time.time() - submittime) > matches.db_sumbmission_time:
        if matches.new_data.shape[0] > 0:
            matches.submit_data()
            matches.new_data = pd.DataFrame()
        #     submittime = time.time()

if __name__ == '__main__':
    ### define logger
    lg.basicConfig(filename='data_collector.log', filemode='w',
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=lg.INFO)
    logger = lg.getLogger()
    stdout_handler = lg.StreamHandler(sys.stdout)
    logger.addHandler(stdout_handler)
    ### read config file
    args = json.load(open('data_collector_config.json'))
    ### running main app
    main()
    