import plotly.express as px  

from dota_utils import plot_utils

# class DotaPlots():
#     def __init__(self):

#         pass

def duration_hist(data):
    df = data.match_data[['duration', 'num_mmr']]
    df['mmr rank'] = df['num_mmr']
    df['duration(min)'] = df['duration']/60
    df = df.sort_values(by='num_mmr')
    hist = px.histogram(df, x="duration(min)", color="mmr rank")
    return hist

def duration_box(data):
    df = data.match_data[['duration', 'num_mmr']]
    df['mmr rank'] = df['num_mmr']
    df['duration(min)'] = df['duration']/60
    df = df.sort_values(by='num_mmr')
    box = px.box(df, x='mmr rank', y="duration(min)", color="mmr rank")
    box.update_layout(showlegend=False)
    return box

def heroes_heatmap(data):
    heroes_df = plot_utils.heroes_df(data, 'both')
    heroes_df = heroes_df.sort_values(by='localized_name')
    heroes_df = heroes_df.set_index('localized_name')
    heatmap = px.imshow(heroes_df, aspect='auto')
    heatmap.layout.height = 2000
    heatmap.update_layout(showlegend=False)
    heatmap.update_coloraxes(showscale=False)

    # heroes_df = data.hbym_data
    # heatmap = px.imshow(heroes_df)
    return heatmap
