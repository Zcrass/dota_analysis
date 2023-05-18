import plotly.express as px  

from dota_utils import utils

def duration_hist(data):
    data = data.match_data[['duration', 'dota rank']]
    data = data.copy()
    data['duration(min)'] = data['duration']/60
    data = data.sort_values(by='dota rank')
    hist = px.histogram(data, x="duration(min)", color="dota rank")
    return hist

def duration_box(data):
    data = data.match_data[['duration', 'dota rank']]
    data = data.copy()
    data['duration(min)'] = data['duration']/60
    data = data.sort_values(by='dota rank')
    box = px.box(data, x='dota rank', y="duration(min)", color="dota rank")
    box.update_layout(showlegend=False)
    return box

def heroes_heatmap(data):
    heroes_df = utils.heroes_pick_df(data, 'both')
    heroes_df = heroes_df.sort_values(by='localized_name')
    heroes_df = heroes_df.set_index('localized_name')
    heatmap = px.imshow(heroes_df, aspect='auto')
    heatmap.layout.height = 2000
    heatmap.update_layout(showlegend=False)
    heatmap.update_coloraxes(showscale=False)
    return heatmap

def heroes_wlr_heatmap(data):
    heroes_df = utils.heroes_wlr_by_rank(data)
    heroes_df = heroes_df.sort_values(by='localized_name')
    heroes_df = heroes_df.set_index('localized_name')
    heatmap = px.imshow(heroes_df, aspect='auto')
    heatmap.layout.height = 2000
    heatmap.update_layout(showlegend=False)
    heatmap.update_coloraxes(showscale=False)
    return heatmap 