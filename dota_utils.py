import json
import logging as lg
import pandas as pd 
import sqlite3

logger = lg.getLogger(__name__)
class DotaData():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.connection = sqlite3.connect("dota_db.sqlite")
        self.match_data = pd.read_sql(f'select * from publicMatches', self.connection)
        self.heroes_data = pd.read_sql(f'select * from heroes', self.connection)
        self.hbym_data = pd.read_sql(f'select * from heroesbymatch', self.connection)
        self.hbym_data_stored_matches = self.get_matches_db(self.db_heroesbymatch_table)

    def get_team(self, match, team):
        team = self.match_data.loc[self.match_data.match_id == match]
        return team
    
    def get_matches_db(self, db_table_name):
        '''
        Function that retrieves data from db
        '''
        try:
            logger.info(f'Connecting to db {self.db_name}')
            connection = sqlite3.connect(self.db_name)
            logger.info(f'Connection to db {self.db_name} succesfull')    
            try:
                logger.info(f'Retrieving data from table {db_table_name}')
                stored_data = pd.read_sql(f'SELECT * FROM {db_table_name}', connection)
                logger.info(f'Connection to table {self.db_name} succesfull')
                # connection.close()
                logger.info(f'Received {stored_data.shape[0]} records of data from {db_table_name} table')
                return list(stored_data.match_id.values)
            except:
                logger.error(f'Connection to table {db_table_name} fail!')                
        except:
            logger.error(f'Connection to database {self.db_name} fail!')
    
class TeamsData():
    def __init__(self, dota_data, match_id):
        self.match_id = match_id
        self.db_name = dota_data.db_name
        self.db_table_name = dota_data.db_heroesbymatch_table
        self.radiant = dota_data.match_data.loc[dota_data.match_data.match_id == match_id]['radiant_team']
        self.dire = dota_data.match_data.loc[dota_data.match_data.match_id == match_id]['dire_team']
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
                logger.info(f'Submiting data to {self.db_table_name}')
                self.combined_teams.to_sql(name=self.db_table_name, con=connection, if_exists='append', index=False)
            except:
                logger.error(f'Submission to table {self.db_table_name} fail!')
            else:
                logger.info(f'Submited data from match {self.match_id} into table {self.db_table_name} succesfully!')
        except:
            logger.error(f'Connection to {self.db_name} fail!') 
            
class plot_utils():

    def heroes_matrix(data, team):
        if team == 'radiant':
            team = '1'
        elif team == 'dire':
            team = '-1'
        ### get total number of matches by rank
        total_matches = {}
        mat = []
        for rank in range(1,9):
            total_matches[rank] = data.match_data.loc[data.match_data['num_mmr'] == rank].shape[0]
        ### get list of lists
        for hero_id in data.heroes_data.id:
            ### identify matches where hero apear in both radiant or dire teams
            if team == 'both':
                heroe_matches_id = list(data.hbym_data.loc[data.hbym_data[str(hero_id)] != '0']['match_id'])
            else:
                heroe_matches_id = list(data.hbym_data.loc[data.hbym_data[str(hero_id)] == team]['match_id'])
            heroe_matches_id = [int(x) for x in heroe_matches_id]
            ### extract data from matches with the heroe in each team
            heroe_matches_data = data.match_data[data.match_data['match_id'].isin(heroe_matches_id)]
            ### iterate by rank levels
            hero_list = []
            for rank in range(1,9):
                hero_list += [heroe_matches_data.loc[heroe_matches_data.num_mmr == rank].shape[0]/total_matches[rank]]
            mat = mat + [hero_list]
        return(mat)
