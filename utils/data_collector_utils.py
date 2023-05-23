#!/usr/bin/env python

import json
import logging as lg
import pandas as pd 
import requests
import sqlite3

logger = lg.getLogger(__name__)
class DataCollector():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.new_data = pd.DataFrame()
        self.stored_data = pd.DataFrame()

    def get_matches_db(self):
        '''
        Function that retrieves data from db
        '''
        try:
            logger.info(f'Connecting to db {self.db_name}')
            connection = sqlite3.connect(self.db_name)
            logger.info(f'Connection to db {self.db_name} succesfull')    
            try:
                logger.info(f'Retrieving data from table {self.db_match_table}')
                stored_data = pd.read_sql(f'SELECT * FROM {self.db_match_table}', connection)
                logger.info(f'Connection to table {self.db_name} succesfull')
                # connection.close()
                logger.info(f'Received {stored_data.shape[0]} records of data from {self.db_match_table} table')
                return list(stored_data['match_id'].values)
            except:
                logger.error(f'Connection to table {self.db_match_table} fail!')                
        except:
            logger.error(f'Connection to database {self.db_name} fail!')
            
    def receive_matches(self):
        '''
        function that retreieves matches info
        '''
        try:
            logger.info(f'Retrieving data from endpoint {self.api_url}')
            data = json.loads(requests.get(self.api_url).text)
            data = pd.json_normalize(data)
            # logger.info(f'received {data.shape[0]} records from endpoint {self.api_name}')
            data = data.drop_duplicates(subset='match_id')
            data = data.loc[~data['match_id'].isin(self.stored_matches)]
            logger.info(f'received {data.shape[0]} new records from endpoint {self.api_name}')
            return data
        except:
            logger.warning(f'Connection to endpoint {self.api_name} failed...')
    
    def submit_data(self):
        '''
        Function that submits data into db
        '''
        try:
            logger.info(f'Connecting to db {self.db_name}')
            connection=sqlite3.connect(self.db_name)
            try:
                logger.info(f'Submiting data to {self.db_match_table}')
                self.new_data.to_sql(name=self.db_match_table, con=connection, if_exists='append', index=False)
            except:
                logger.error(f'Submission to table {self.db_match_table} fail!')
            else:
                logger.info(f'Submited {self.new_data.shape[0]} into table {self.db_match_table} succesfully!')
        except:
            logger.error(f'Connection to {self.db_name} fail!') 
            
class TeamsData():
    def __init__(self, dota_data, match_id):
        self.match_id = match_id
        self.db_name = dota_data.db_name
        self.db_table_hbym = dota_data.db_heroesbymatch_table
        self.radiant = dota_data.match_data.loc[dota_data.match_data['match_id'] == match_id, 'radiant_team']
        self.dire = dota_data.match_data.loc[dota_data.match_data['match_id'] == match_id, 'dire_team']
        self.combined_teams = self.comb_teams(dota_data)
        
    def comb_teams(self, dota_data):
        combined_teams = pd.DataFrame(columns=dota_data.hbym_data.columns)
        for rad_hero in self.heroes2list(self.radiant.values):
            combined_teams.at[self.match_id, rad_hero] = 1
        for dire_hero in self.heroes2list(self.dire.values):
            combined_teams.at[self.match_id, dire_hero] = -1
        combined_teams.match_id = self.match_id
        combined_teams = combined_teams.fillna(0)
        return combined_teams
    
    def heroes2list(self, heroes):
        heroes_list = str(heroes)
        heroes_list = heroes_list.replace('[', '').replace(']', '').replace("'", '').split(',')
        return heroes_list
    
    def submit_data(self):
        '''
        Function that submits data into db
        '''
        try:
            logger.info(f'Connecting to db {self.db_name}')
            connection=sqlite3.connect(self.db_name)
            try:
                logger.info(f'Submiting data to {self.db_table_hbym}')
                self.combined_teams.to_sql(name=self.db_table_hbym, con=connection, if_exists='append', index=False)
            except:
                logger.error(f'Submission to table {self.db_table_hbym} fail!')
            else:
                logger.info(f'Submited data from match {self.match_id} into table {self.db_table_hbym} succesfully!')
        except:
            logger.error(f'Connection to {self.db_name} fail!') 
    
