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
    
# class utils():

    def heroes_pick_df(self, team):
        if team == 'radiant':
                team = 1
        elif team == 'dire':
                team = -1
        ### get total number of matches by rank
        total_matches = {}
        df = self.heroes_data[['id', 'localized_name']]
        df = df.set_index('id')
        for rank in self.dota_ranks.keys():
            ### count total matches
            total_matches[rank] = self.match_data.loc[self.match_data['dota rank'] == rank].shape[0]
            ### empty column by rank
            df[rank] = 0
        for hero_id in self.heroes_data['id']:
            hero_id = str(hero_id)
            ### identify matches where hero apear in either both or radiant/dire teams
            if team == 'both':
                heroe_matches_id = list(self.hbym_data.loc[self.hbym_data[hero_id] != 0, 'match_id'])
            else:
                heroe_matches_id = list(self.hbym_data.loc[self.hbym_data[hero_id] == team, 'match_id'])
            ### extract data from matches with the heroe in each team
            heroe_matches_data = self.match_data[self.match_data['match_id'].isin(heroe_matches_id)]
            ### iterate by rank levels
            for rank in self.dota_ranks.keys():
                if heroe_matches_data.loc[heroe_matches_data['dota rank'] == rank].shape[0] > 0:
                    hero_count = heroe_matches_data.loc[heroe_matches_data['dota rank'] == rank].shape[0]/total_matches[rank]*100
                else:
                    hero_count = None
                df.at[int(hero_id), rank] = hero_count
        return df
            
    def heroes_wlr_by_rank(self):
        df = self.heroes_data[['id', 'localized_name']]
        df = df.set_index('id')
        for rank in self.dota_ranks.keys():
            ### empty column by rank
            df[rank] = 0
        for hero_id in self.heroes_data['id']:
            hero_id = str(hero_id)
            ### identify matches where hero apear in either both or radiant/dire teams
            heroe_matches_id = self.hbym_data.loc[self.hbym_data[hero_id] != 0, ['match_id', hero_id]]
            ### extract data from matches with the heroe in any team
            heroe_matches_data = self.match_data.loc[self.match_data['match_id'].isin(list(heroe_matches_id['match_id']))]
            heroe_matches_data = heroe_matches_data.merge(heroe_matches_id, how='left', on='match_id')
            ### add column to indicate if the heroe team wins
            heroe_matches_data['team_with_hero_win'] = 0
            heroe_matches_data.loc[(heroe_matches_data['radiant_win'] == 1) & (heroe_matches_data[hero_id] == 1), 'team_with_hero_win'] = 1
            heroe_matches_data.loc[(heroe_matches_data['radiant_win'] == 0) & (heroe_matches_data[hero_id] == -1), 'team_with_hero_win'] = 1
            # print(f'Total matches with hero {hero_id}: {heroe_matches_data.shape[0]}')
            ### iterate by rank levels
            for rank in self.dota_ranks.keys():
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
    

    def combine_teams(self, enemy):
        ### extract df's
        radiant_view = self.hbym_data.copy()
        dire_view = self.hbym_data.copy()
        if enemy == True:
            ### for radiant
            ### keep dire in radiant df
            ### keep radiant as main team
            ### for dire
            dire_view.replace(1, -1, inplace=True)   ### change radiant to enemy
            dire_view.replace(-1, 1, inplace=True)   ### change dire -> main team
            
        else:
            ### for radiant
            radiant_view.replace(-1, 0, inplace=True)   ### remove dire from  radiant df
            ### keep radiant as main team
            ### for dire
            dire_view.replace(1, 0, inplace=True)   ### remove radiant from dire df
            dire_view.replace(-1, 1, inplace=True)   ### change dire -> main team
        ### for radiant
        radiant_view = self.match_data.copy().merge(radiant_view, how='left', on='match_id')
        radiant_view['Tean name'] = 'Radiant'
        radiant_view['Team win'] = radiant_view['radiant_win']  ### add new column AND add radiant wins
        ### for dire
        dire_view = self.match_data.copy().merge(dire_view, how='left', on='match_id')
        dire_view['Tean name'] = 'Dire'
        dire_view['Team win'] = 0; dire_view.loc[dire_view['radiant_win'] == 0, 'Team win'] = 1    ### add new column AND add dire wins

        combined = pd.concat([radiant_view, dire_view])
        # combined.drop(columns=['match_seq_num', 'start_time', 'avg_mmr', 'num_mmr', 
        #                         'lobby_type', 'game_mode', 'avg_rank_tier', 'num_rank_tier',
        #                         'cluster', 'radiant_team', 'dire_team',], inplace=True)
        
        return combined

