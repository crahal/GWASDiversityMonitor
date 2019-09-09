from bokeh.layouts import row, column, layout
from bokeh.models import (Panel, HoverTool, GeoJSONDataSource, ColumnDataSource,
                          LinearColorMapper, ColorBar, NumeralTickFormatter)
from bokeh.palettes import brewer
from bokeh.plotting import curdoc, figure
from bokeh.models.widgets import Tabs
from bokeh.transform import cumsum
from bokeh.palettes import Category10
import datetime as dt
import os
from colorcet import blues
import json
from math import pi
from support_functions import (widgets, import_data,
                               load_divs, create_width_dict)


def update():
    ''' Initlize the data'''
    update_hbar_source()
    update_hbar_axis()
    update_choro()
    update_ts()
    update_bubble()
    update_doughnut()


def update_hbar_source():
    '''
    Update horizontal bargraph plot.
    Appropriate widgets: stage -- initial or replication
                         metric -- number of studies or sum of particpants
    '''

    if 'number of studies' in str(metric.value).lower():
        if str(stage.value) == 'Discovery':
            sorted_df = freetext_df.\
                        sort_values(by='Initial_Ancestry_Count_%',
                                    ascending=False)
            hbar_source.data = dict(
             Cleaned_Ancestry=sorted_df['Cleaned_Ancestry'][0:10].to_list(),
             toplot=sorted_df['Initial_Ancestry_Count_%'][0:10]/100,
             hbar_color=["#d7191c"]*10,
             hbar_legendval=['Initial Stage (%)']*10)
        elif str(stage.value) == 'Replication':
            sorted_df = freetext_df.\
                        sort_values(by='Replication_Ancestry_Count_%',
                                    ascending=False)
            hbar_source.data = dict(
                Cleaned_Ancestry=sorted_df['Cleaned_Ancestry'][0:10].to_list(),
                toplot=sorted_df['Replication_Ancestry_Count_%'][0:10]/100,
                hbar_color=["#2b83ba"]*10,
                hbar_legendval=['Replication Stage (%)']*10)
        hbar_plot.xaxis.axis_label = 'Percent of all Studies (%)'
        titletext = 'Fig 2: Ancestries in Free Text: ' + str(stage.value)
    elif 'number of participants' in str(metric.value).lower():
        if str(stage.value) == 'Discovery':
            sorted_df = freetext_df.\
                        sort_values(by='Initial_Ancestry_Sum_%',
                                    ascending=False)
            hbar_source.data = dict(
                Cleaned_Ancestry=sorted_df['Cleaned_Ancestry'][0:10].to_list(),
                toplot=sorted_df['Initial_Ancestry_Sum_%'][0:10]/100,
                hbar_color=["#d7191c"]*10,
                hbar_legendval=['Discovery Stage (%)']*10)
        elif str(stage.value) == 'Replication':
            sorted_df = freetext_df.\
                        sort_values(by='Replication_Ancestry_Sum_%',
                                    ascending=False)
            hbar_source.data = dict(
               Cleaned_Ancestry=sorted_df['Cleaned_Ancestry'][0:10].to_list(),
               toplot=sorted_df['Replication_Ancestry_Sum_%'][0:10]/100,
               hbar_color=["#2b83ba"]*10,
               hbar_legendval=['Replication Stage (%)']*10)
        hbar_plot.xaxis.axis_label = 'Percent of all Participants (%)'
        titletext = 'Fig 2: Free Text Anlaysis: ' + str(stage.value)
    hbar_plot.title.text = titletext + ' Stage: All Years and Parent Categories'


def update_hbar_axis():
    ''' Update the range (tick labels) for horizontal bar plot'''
    hbar_plot.y_range.factors = hbar_source.data['Cleaned_Ancestry']


def create_hbar_plot():
    '''
    Creates the horizontal barplot
    Returns: hbar_hover -- the hovertool for the hbar plot
             hbar_plot -- the plot itself
             hbar_source -- for updating upon interaction
    '''
    hbar_source = ColumnDataSource(data=dict(Cleaned_Ancestry=[], toplot=[],
                                             hbar_color=[], hbar_legendval=[]))
    yrange = freetext_df.\
        sort_values(by='Initial_Ancestry_Count_%',
                    ascending=False)['Cleaned_Ancestry'][0:10].to_list()
    hbar_plot = figure(y_range=yrange,
                       plot_height=width_dict['hbar_height'],
                       plot_width=width_dict['hbar_width'],
                       title="Fig 2: Ancestral Terms in Free Text Field",
                       tools=TOOLS, toolbar_location=None)
    hbar_plot.hbar(y='Cleaned_Ancestry', right='toplot', height=0.6,
                   source=hbar_source, color='hbar_color', alpha=.6,
                   line_color="black", legend='hbar_legendval')
    hbar_hover = hbar_plot.select(dict(type=HoverTool))
    hbar_hover.tooltips = [('Ancestry Term: ', '@Cleaned_Ancestry'),
                           ('$Percent Value: ', '@toplot{0.000%}')]
    hbar_plot.xaxis.formatter = NumeralTickFormatter(format='0 %')
    hbar_plot.legend.border_line_width = 1
    hbar_plot.legend.border_line_color = "black"
    hbar_plot.xgrid.grid_line_dash = 'dashed'
    hbar_plot.ygrid.grid_line_dash = 'dashed'
    hbar_plot.outline_line_color = None
    return hbar_source, hbar_hover, hbar_plot


def json_data(selectedYear):
    ''' sets the year for the slider and filters data'''
    yr = selectedYear
    df_yr = choro_df[choro_df['Year'] == yr].copy()
    if metric.value == 'Number of Studies (%)':
        df_yr.loc[:, 'ToPlot'] = df_yr['Count (%)']
    else:
        df_yr.loc[:, 'ToPlot'] = df_yr['N (%)']
    merged = gdf.merge(df_yr, left_on='country', right_index=True, how='left')
    merged.fillna('No data', inplace=True)
    merged_json = json.loads(merged.to_json())
    json_data = json.dumps(merged_json)
    return json_data


def update_choro_slider(attr, old, new):
    ''' updates the slider'''
    yr = slider.value
    new_data = json_data(yr)
    geosource.geojson = new_data
    choro_plot.title.text = 'Fig 5: Participant Recruitment Over Time, ' +\
                            'All Parent Categories and Both Stages: %d' % yr


def update_choro():
    ''' generates new data based on slider value'''
    new_data = json_data(slider.value)
    geosource.geojson = new_data


def create_choro_plot(year):
    '''
    Creates the choropleth plot. Returns:
        geosource -- the choropleth source
        choro_plot -- the choropleth map itself
        choro_hover -- the hovertool for the choropleth map
    '''
    geosource = GeoJSONDataSource(geojson=json_data(year))
    palette = brewer['Blues'][6]
    palette = palette[::-1][1:-1]
    palette[0] = '#eef2ff'
    color_map = LinearColorMapper(palette=blues[25:], low=0, high=25,
                                  nan_color='white')
    tick_labels = {'0': '0%', '5': '5%', '10': '10%',
                   '15': '15%', '20': '20%', '25': '>25%'}
    color_bar = ColorBar(color_mapper=color_map, location=(0, 0),
                         label_standoff=8, major_label_overrides=tick_labels,
                         height=int(width_dict['choro_height']*.84),
                         border_line_color=None, orientation='vertical',
                         width=int(width_dict['choro_width']/40))
    choro_plot = figure(title='Fig 5: Participant Recruitment Over Time, All ' +\
                              'Parent Categories and Both Stages: ' + str(year),
                        plot_height=width_dict['choro_height'], tools=TOOLS,
                        plot_width=width_dict['choro_width'],
                        toolbar_location=None)
    choro_plot.patches('xs', 'ys', source=geosource, fill_alpha=1,
                       fill_color={'field': 'ToPlot', 'transform': color_map},
                       line_color='black', line_width=0.25)
    choro_plot.yaxis.axis_label = 'Latitude'
    choro_plot.xaxis.axis_label = 'Longitude'
    choro_hover = choro_plot.select(dict(type=HoverTool))
    choro_hover.tooltips = [('Country/region', '@country'),
                            ('Participants (m)', '@N'),
                            ('Number of Studies Used', '@Count')]
    choro_plot.add_layout(color_bar, 'right')
    choro_plot.outline_line_color = None
    choro_plot.xgrid.grid_line_color = None
    choro_plot.ygrid.grid_line_color = None
    return geosource, choro_hover, choro_plot


def update_ts():
    ''' updates ts_source'''
    if 'number of studies' in str(metric.value).lower():
        if str(stage.value) == 'Discovery':
            ts_source.data = dict(
                Year=[ts_init_count['index']],
                ts_toplot=[ts_init_count[ancestry.value]/100],
                ts_color=[["#2b83ba"]],
                ts_legendval=[['Discovery Stage (%)']])
            ts_plot.title.text = 'Fig 4: Discovery Stage Across all Parent Categories: ' +\
                                 str(ancestry.value) + ' Ancestry'
        elif str(stage.value) == 'Replication':
            ts_source.data = dict(
                Year=[ts_rep_count['index']],
                ts_toplot=[ts_rep_count[ancestry.value]/100],
                ts_color=[["#d7191c"]],
                ts_legendval=[['Replication Stage (%)']])
            ts_plot.title.text = 'Fig 4: Replication Stage Across all Parent Categories: ' +\
                                 str(ancestry.value) + ' Ancestry'
        ts_plot.yaxis.axis_label = 'Percent of all Studies (%)'
    elif 'number of participants' in str(metric.value).lower():
        if str(stage.value) == 'Discovery':
            ts_source.data = dict(
                Year=[ts_init_sum['index']],
                ts_toplot=[ts_init_sum[ancestry.value]/100],
                ts_color=[["#2b83ba"]],
                ts_legendval=[['Discovery Stage (%)']])
            ts_plot.title.text = 'Fig 4: Discovery Stage Across all Parent Categories: ' +\
                                 str(ancestry.value) + ' Ancestry'
        elif str(stage.value) == 'Replication':
            ts_source.data = dict(
                Year=[ts_rep_sum['index']],
                ts_toplot=[ts_rep_sum[ancestry.value]/100],
                ts_color=[["#d7191c"]],
                ts_legendval=[['Replication Stage (%)']])
            ts_plot.title.text = 'Fig 4: Replication Stage Across all Parent Categories: ' +\
                                 str(ancestry.value) + ' Ancestry'
        ts_plot.yaxis.axis_label = 'Percent of all Participants (%)'


def create_ts_plot(maxyear):
    '''
    Creates the time series plot. Returns:
        ts_source -- the source data which gets updated
        ts_source -- the hovertool
        ts_plot -- the actual time series plot
    '''
    ts_source = ColumnDataSource(data=dict(index=[], Year=[], ts_toplot=[],
                                           ts_color=[], ts_legendval=[]))
    ts_plot = figure(x_range=(2008, maxyear), plot_height=width_dict['ts_height'],
                     plot_width=width_dict['ts_width'], tools=TOOLS,
                     toolbar_location=None,
                     y_axis_label='Percent of all Studies (%)',
                     title="Fig 4: Percent of Studies Conducted (%)")
    ts_plot.yaxis.formatter = NumeralTickFormatter(format='0 %')
    ts_hover = ts_plot.select(dict(type=HoverTool))
    ts_hover.tooltips = [("Year: ", "$x{int}"), ("Ancestry: ", ancestry.value),
                         ("Percentage Value: ", "$y{0.000%}")]
    ts_plot.multi_line(xs='Year', ys='ts_toplot', source=ts_source, alpha=0.8,
                       line_width=2, color='ts_color', legend='ts_legendval')
    ts_plot.legend.border_line_width = 1
    ts_plot.legend.border_line_color = "black"
    ts_plot.legend.location = "top_right"
    ts_plot.legend.orientation = "horizontal"
    ts_plot.xgrid.grid_line_dash = 'dashed'
    ts_plot.ygrid.grid_line_dash = 'dashed'
    ts_plot.yaxis.formatter = NumeralTickFormatter(format='0 %')
    ts_plot.outline_line_color = None
    return ts_source, ts_hover, ts_plot


def create_bubble_plot():
    '''
    Creates the bubble plot. Returns:
        bubble_source -- the source data which gets updated upon interaction
        bubble_hover -- the bubble hovertool
        bubble_plot -- the actual bubble plot itself
    '''
    bubble_source = ColumnDataSource(data=dict(DATE=[], N=[], bubble_color=[],
                                     Broader=[], Size=[], PUBMEDID=[],
                                     Stage=[]))
    bubble_plot = figure(title='Fig 1: Ancestry Across All Samples Over Time',
                         plot_height=width_dict['bubble_height'],
                         plot_width=width_dict['bubble_width'],
                         y_axis_label='Number of Genotyped Participants',
                         x_axis_type='datetime', y_axis_location='left',
                         x_range=(dt.date(2008, 1, 1), bubble_df['DATE'].max()),
                         tools=TOOLS, toolbar_location=None,
                         sizing_mode="scale_both")
    bubble_hover = bubble_plot.select(dict(type=HoverTool))
    bubble_hover.tooltips = [("Size", "@N"),
                             ("PUBMEDID", "@PUBMEDID"),
                             ("First Author", "@AUTHOR"),
                             ("Trait", "@TRAIT")]
    bubble_plot.circle(x='DATE', y='N', source=bubble_source,
                       color='bubble_color', size='size', alpha=0.45,
                       line_color='black', line_width=0.175, legend='Broader')
    bubble_plot.legend.border_line_width = 1
    bubble_plot.legend.border_line_color = "black"
    bubble_plot.legend.location = "top_left"
    bubble_plot.legend.orientation = "vertical"
    bubble_plot.xgrid.grid_line_dash = 'dashed'
    bubble_plot.ygrid.grid_line_dash = 'dashed'
    bubble_plot.outline_line_color = None
    return bubble_source, bubble_hover, bubble_plot


def select_ancestry_bubble():
    ''' Update the ancestry data into the bubble source'''
    ancestry_val = ancestry.value
    selected = bubble_df
    selected = selected[selected['Broader'] == ancestry_val]
    return selected


def select_stage_bubble(df):
    ''' Update the stage data into the bubble source'''
    stage_val = stage.value
    df = df[df['STAGE'].str.title() == stage_val]
    return df


def select_parent_bubble(df):
    ''' Update the EFO parent data into the bubble source'''
    parent_val = parent.value
    if (parent_val != "All"):
        df = df[df['parentterm'] == parent_val]
    return df


def update_bubble():
    ''' Update the bubble source with interactive choices'''
    df = select_ancestry_bubble()
    df = select_stage_bubble(df)
    df = select_parent_bubble(df)
    df["size"] = (df["N"]/df['N'].max())*100
    bubble_source.data = dict(DATE=df['DATE'], N=df['N'],
                              bubble_color=df["color"],
                              Broader=df['Broader'], size=df['size'],
                              AUTHOR=df['AUTHOR'], PUBMEDID=df['PUBMEDID'],
                              STAGE=df['STAGE'].str.title(),
                              PARENT=df['parentterm'],
                              TRAIT=df['DiseaseOrTrait'])


def create_doughnut_plot():
    '''
        Creates the doughnut chart. Returns:
            doughnut_source -- the doughnut source data
            doughnut_hover -- the doughnut hovertools
            doughnut_plot -- the actual doughnut plot itself
    '''
    doughnut_df['Broader'] = doughnut_df['Broader'].str.\
        replace('In Part Not Recorded', 'In Part No Record')
    doughnut_source = ColumnDataSource(data=dict(Broader=[], doughnut_toplot=[],
                                     doughnut_angle=[], doughnut_color=[],
                                     parentterm=[], doughnut_stage=[]))
    doughnut_plot = figure(plot_height=width_dict['doughnut_height'],
                         plot_width=width_dict['doughnut_width'],
                         tools=TOOLS, toolbar_location=None,
                         title="Fig 3: Doughnut Chart",
                         x_range=(-1, 1), y_range=(-1, 1))
    doughnut_hover = doughnut_plot.select(dict(type=HoverTool))
    doughnut_hover.tooltips = [("Ancestry: ", "@Broader"),
                             ("Stage: ", "@doughnut_stage"),
                             ("Parent Category: ", "@parentterm"),
                             ("Percent: ", "@doughnut_toplot{0.000%}")]
    doughnut_plot.annular_wedge(x=-.35, y=0, inner_radius=0.35,
                              outer_radius=0.65,
                              start_angle=cumsum('doughnut_angle',
                                                 include_zero=True),
                              end_angle=cumsum('doughnut_angle'),
                              line_color="white", source=doughnut_source,
                              fill_color='doughnut_color', legend='Broader',
                              direction='anticlock',
                              fill_alpha=0.8)
    doughnut_plot.axis.axis_label = None
    doughnut_plot.axis.visible = False
    doughnut_plot.grid.grid_line_color = None
    doughnut_plot.legend.border_line_width = 1
    doughnut_plot.legend.border_line_color = "black"
    doughnut_plot.legend.label_text_font_size = '8pt'
    doughnut_plot.legend.location = "top_right"
    doughnut_plot.outline_line_color = None
    return doughnut_source, doughnut_hover, doughnut_plot


def update_doughnut():
    ''' update the doughnut chart with interactive choices'''
    colorlist = ['#fee08b', '#d53e4f', '#99d594', '#bdbdbd',
                 '#3288bd', '#fc8d59', '#807dba']
    df = select_parent_doughnut()
    if 'number of studies' in str(metric.value).lower():
        if str(stage.value) == 'Discovery':
            doughnut_source.data = dict(Broader=df['Broader'],
                                      parentterm=df['parentterm'],
                                      doughnut_toplot=df['InitialCount']/100,
                                      doughnut_angle=df['InitialCount'] /
                                                   df['InitialCount'].sum()*2*pi,
                                      doughnut_color=colorlist,
                                      doughnut_stage=['Initial']*len(df))
        elif str(stage.value) == 'Replication':
            doughnut_source.data = dict(Broader=df['Broader'],
                                      parentterm=df['parentterm'],
                                      doughnut_toplot=df['ReplicationCount']/100,
                                      doughnut_angle=df['ReplicationCount'] /
                                                   df['ReplicationCount'].sum()*2*pi,
                                      doughnut_color=colorlist,
                                      doughnut_stage=['Replication']*len(df))
        doughnut_plot.title.text = 'Fig 3: # Studies for ' +\
                                    str(parent.value) + ' at ' +\
                                    str(stage.value) + '.'
    elif 'number of participants' in str(metric.value).lower():
        if str(stage.value) == 'Discovery':
            doughnut_source.data = dict(Broader=df['Broader'],
                                      parentterm=df['parentterm'],
                                      doughnut_toplot=df['InitialN']/100,
                                      doughnut_angle=df['InitialN'] /
                                                   df['InitialN'].sum()*2*pi,
                                      doughnut_color=colorlist,
                                      doughnut_stage=['Initial']*len(df))
        elif str(stage.value) == 'Replication':
            doughnut_source.data = dict(Broader=df['Broader'],
                                      parentterm=df['parentterm'],
                                      doughnut_toplot=df['ReplicationN']/100,
                                      doughnut_angle=df['ReplicationN'] /
                                                   df['ReplicationN'].sum()*2*pi,
                                      doughnut_color=colorlist,
                                      doughnut_stage=['Replication']*len(df))
        doughnut_plot.title.text = 'Fig 3: # Participants for ' +\
                                   str(parent.value).title() + ' at ' +\
                                   str(stage.value) + '.'


def select_parent_doughnut():
    ''' select parent data for the doughnut'''
    parent_val = parent.value
    selected = doughnut_df
    selected = selected[selected['parentterm'] == parent_val]
    return selected


width_dict = create_width_dict()
data_path = os.path.abspath(os.path.join('data'))
bubble_df, freetext_df, ts_init_count, ts_init_sum, ts_rep_count,\
    ts_rep_sum, choro_df, gdf, doughnut_df = import_data(data_path)
maxyear = bubble_df['DATE'].max().year
stage, parent, ancestry, metric, slider = widgets(width_dict['control_width'],
                                                  width_dict['slider_height'],
                                                  width_dict['slider_width'],
                                                  bubble_df, ts_init_count,
                                                  maxyear)
slider.on_change('value', update_choro_slider)
TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"

hbar_source, hbar_hover, hbar_plot = create_hbar_plot()
geosource, choro_hover, choro_plot = create_choro_plot(maxyear-1)
ts_source, ts_hover, ts_plot = create_ts_plot(maxyear)
bubble_source, bubble_hover, bubble_plot = create_bubble_plot()
doughnut_source, doughnut_hover, doughnut_plot = create_doughnut_plot()

controls = [metric, ancestry, parent, stage]
for control in controls:
    control.on_change('value', lambda attr, old, new: update_hbar_source())
    control.on_change('value', lambda attr, old, new: update_hbar_axis())
    control.on_change('value', lambda attr, old, new: update_choro())
    control.on_change('value', lambda attr, old, new: update_ts())
    control.on_change('value', lambda attr, old, new: update_bubble())
    control.on_change('value', lambda attr, old, new: update_doughnut())
update()

header, about, dumdiv, summary, footer, downloaddata = load_divs(width_dict['twocolumn_width'],
                                                                 width_dict['div_width'])
interact_fig = column(row(column(header, *controls, downloaddata, doughnut_plot),
                          column(bubble_plot, row(dumdiv, choro_plot, slider)),
                          column(ts_plot, hbar_plot), sizing_mode="fixed"))
interact_tab = Panel(child=interact_fig, title='Interactive Figures')
text = layout(row(column(header, summary, footer), dumdiv, about),
              sizing_mode='stretch_width')
texttab = Panel(child=text, title="Additional Information")
tabs = Tabs(tabs=[interact_tab, texttab])
curdoc().add_root(tabs)
curdoc().title = "GWAS Diversity Monitor"
