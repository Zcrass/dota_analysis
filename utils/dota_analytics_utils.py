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


