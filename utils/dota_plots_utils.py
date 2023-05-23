import plotly.express as px 
import plotly.graph_objects as go


# from utils.dota_data_utils import utils
# from utils.dota_analytics_utils import utils

def duration_hist(data):
    data = data.match_data[['duration', 'dota rank']]
    data = data.copy()
    data['duration(min)'] = data['duration']/60
    data = data.sort_values(by='dota rank')
    hist = px.histogram(data, x="duration(min)", color="dota rank", histnorm='density')
    return hist

def duration_box(data):
    data = data.match_data[['duration', 'dota rank']]
    data = data.copy()
    data['duration(min)'] = data['duration']/60
    data = data.sort_values(by='dota rank').dropna()
    # box = px.box(data, x='dota rank', y="duration(min)", color="dota rank")
    # box = px.ecdf(data, x="duration(min)", color="dota rank", ecdfnorm=None, marginal="histogram")
    box = px.violin(data, x='dota rank', y="duration(min)", color="dota rank", box=True, points="outliers")
    box.update_layout(showlegend=False)
    return box

def mmr_hist(data):
    data = data.match_data['avg_mmr']
    data = data.copy()
    hist = px.histogram(data, x="avg_mmr", histnorm='density')
    return hist

def heroes_heatmap(data):
    heroes_df = data.heroes_pick_df('both')
    heroes_df = heroes_df.sort_values(by='localized_name')
    heroes_df = heroes_df.set_index('localized_name')
    heatmap = px.imshow(heroes_df, aspect='auto')
    heatmap.layout.height = 2000
    heatmap.update_layout(showlegend=False)
    heatmap.update_coloraxes(showscale=False)
    return heatmap

def heroes_wlr_heatmap(data):
    heroes_df = data.heroes_wlr_by_rank()
    heroes_df = heroes_df.sort_values(by='localized_name')
    heroes_df = heroes_df.set_index('localized_name')
    heatmap = px.imshow(heroes_df, aspect='auto')
    heatmap.layout.height = 2000
    heatmap.update_layout(showlegend=False)
    heatmap.update_coloraxes(showscale=False)
    return heatmap 