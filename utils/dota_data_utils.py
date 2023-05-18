import json
import logging as lg
import pandas as pd 
import sqlite3

logger = lg.getLogger(__name__)
class DotaData():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.connection = sqlite3.connect("dota_db.sqlite")
        self.match_data, self.match_data_stored_matches = self.get_data_db(self.db_match_table)
        ###
        self.match_data['dota rank'] = self.compute_ranks()
        self.hbym_data, self.hbym_data_stored_matches = self.get_data_db(self.db_heroesbymatch_table)
        if self.hbym_data.shape[0] != self.match_data.shape[0]:
            logger.warning(f'WARNING: different number of matches stored in tables. Please UPDATE')
        ### 
        self.heroes_data = pd.read_sql(f'select * from heroes', self.connection)
        
    def get_team(self, match, team):
        team = self.match_data.loc[self.match_data.match_id == match]
        return team
    
    def get_data_db(self, db_table_name):
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
                return stored_data, list(stored_data['match_id'].values)
            except:
                logger.error(f'Connection to table {db_table_name} fail!')                
        except:
            logger.error(f'Connection to database {self.db_name} fail!')
    
    def compute_ranks(data):
        df = data.match_data[['match_id', 'avg_mmr']]
        df = df.loc[df['avg_mmr'].notna()]
        df['dota rank'] = ''
        ranks = data.dota_ranks
        for r in ranks:
            rank_matches = list(df.loc[(df['avg_mmr'] >= ranks[r][0]) & (df['avg_mmr'] <= ranks[r][1]), 'match_id'])
            df.loc[df['match_id'].isin(rank_matches), 'dota rank'] = r
        return df['dota rank']
    
# class TeamsData():
#     def __init__(self, dota_data, match_id):
#         self.match_id = match_id
#         self.db_name = dota_data.db_name
#         self.db_table_hbym = dota_data.db_heroesbymatch_table
#         self.radiant = dota_data.match_data.loc[dota_data.match_data['match_id'] == match_id, 'radiant_team']
#         self.dire = dota_data.match_data.loc[dota_data.match_data['match_id'] == match_id, 'dire_team']
#         self.combined_teams = self.comb_teams(dota_data)
        
#     def comb_teams(self, dota_data):
#         combined_teams = pd.DataFrame(columns=dota_data.hbym_data.columns)
#         for rad_hero in self.heroes2list(self.radiant.values):
#             combined_teams.at[self.match_id, rad_hero] = 1
#         for dire_hero in self.heroes2list(self.dire.values):
#             combined_teams.at[self.match_id, dire_hero] = -1
#         combined_teams.match_id = self.match_id
#         combined_teams = combined_teams.fillna(0)
#         return combined_teams
    
#     def heroes2list(self, heroes):
#         heroes_list = str(heroes)
#         heroes_list = heroes_list.replace('[', '').replace(']', '').replace("'", '').split(',')
#         return heroes_list
    
#     def submit_data(self):
#         '''
#         Function that submits data into db
#         '''
#         try:
#             logger.info(f'Connecting to db {self.db_name}')
#             connection=sqlite3.connect(self.db_name)
#             try:
#                 logger.info(f'Submiting data to {self.db_table_hbym}')
#                 self.combined_teams.to_sql(name=self.db_table_hbym, con=connection, if_exists='append', index=False)
#             except:
#                 logger.error(f'Submission to table {self.db_table_hbym} fail!')
#             else:
#                 logger.info(f'Submited data from match {self.match_id} into table {self.db_table_hbym} succesfully!')
#         except:
#             logger.error(f'Connection to {self.db_name} fail!') 
            
class utils():
    
    def heroes_pick_df(data, team):
        if team == 'radiant':
                team = 1
        elif team == 'dire':
                team = -1
        ### get total number of matches by rank
        total_matches = {}
        df = data.heroes_data[['id', 'localized_name']]
        df = df.set_index('id')
        for rank in data.dota_ranks.keys():
            ### count total matches
            total_matches[rank] = data.match_data.loc[data.match_data['dota rank'] == rank].shape[0]
            ### empty column by rank
            df[rank] = 0
        for hero_id in data.heroes_data['id']:
            hero_id = str(hero_id)
            ### identify matches where hero apear in either both or radiant/dire teams
            if team == 'both':
                heroe_matches_id = list(data.hbym_data.loc[data.hbym_data[hero_id] != 0, 'match_id'])
            else:
                heroe_matches_id = list(data.hbym_data.loc[data.hbym_data[hero_id] == team, 'match_id'])
            ### extract data from matches with the heroe in each team
            heroe_matches_data = data.match_data[data.match_data['match_id'].isin(heroe_matches_id)]
            ### iterate by rank levels
            for rank in data.dota_ranks.keys():
                if heroe_matches_data.loc[heroe_matches_data['dota rank'] == rank].shape[0] > 0:
                    hero_count = heroe_matches_data.loc[heroe_matches_data['dota rank'] == rank].shape[0]/total_matches[rank]*100
                else:
                    hero_count = None
                df.at[int(hero_id), rank] = hero_count
        return df
            
    def heroes_wlr_by_rank(data):
        df = data.heroes_data[['id', 'localized_name']]
        df = df.set_index('id')
        for rank in data.dota_ranks.keys():
            ### empty column by rank
            df[rank] = 0
        for hero_id in data.heroes_data['id']:
            hero_id = str(hero_id)
            ### identify matches where hero apear in either both or radiant/dire teams
            heroe_matches_id = data.hbym_data.loc[data.hbym_data[hero_id] != 0, ['match_id', hero_id]]
            ### extract data from matches with the heroe in any team
            heroe_matches_data = data.match_data.loc[data.match_data['match_id'].isin(list(heroe_matches_id['match_id']))]
            heroe_matches_data = heroe_matches_data.merge(heroe_matches_id, how='left', on='match_id')
            ### add column to indicate if the heroe team wins
            heroe_matches_data['team_with_hero_win'] = 0
            heroe_matches_data.loc[(heroe_matches_data['radiant_win'] == 1) & (heroe_matches_data[hero_id] == 1), 'team_with_hero_win'] = 1
            heroe_matches_data.loc[(heroe_matches_data['radiant_win'] == 0) & (heroe_matches_data[hero_id] == -1), 'team_with_hero_win'] = 1
            # print(f'Total matches with hero {hero_id}: {heroe_matches_data.shape[0]}')
            ### iterate by rank levels
            for rank in data.dota_ranks.keys():
                matches_data_rank = heroe_matches_data.loc[heroe_matches_data['dota rank'] == rank]
                # print(f'matches with hero {hero_id} in rank {rank}: {matches_data_rank.shape[0]}')
                # print(f'matches with hero {hero_id} in rank {rank} which are wins: {matches_data_rank.loc[matches_data_rank["team_with_hero_win"] == 1].shape[0]}')
                ### compute the win/lose rate
                ### with a small dataset some ranks could be empty
                if matches_data_rank.loc[matches_data_rank['team_with_hero_win'] == 1].shape[0] > 0:
                    wlr = matches_data_rank.loc[matches_data_rank['team_with_hero_win'] == 1].shape[0]/matches_data_rank.shape[0]*100
                else: 
                    wlr = None
                ### add rate to dataframe
                df.at[int(hero_id), rank] = wlr
                # print(f'the wlr of the hero {hero_id} for the rank {rank} is: {wlr}')
        return df


