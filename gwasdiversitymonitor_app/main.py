from bokeh.layouts import row, column
from bokeh.models import (HoverTool, GeoJSONDataSource, ColumnDataSource,
                          LinearColorMapper, NumeralTickFormatter, Span)
from bokeh.palettes import brewer
from bokeh.plotting import curdoc, figure
from bokeh.transform import cumsum
import datetime as dt
import os
from colorcet import blues
import json
from math import pi
from support_functions import (widgets, import_data, create_width_dict)


def update():
    ''' Initlize the data to the default settings'''
    update_hbar_source()
    update_hbar_axis()
    update_choro()
    update_ts1()
    update_ts2()
    update_bubble()
    update_doughnut()


def update_hbar_source():
    '''
    Update horizontal bargraph plot.
    Appropriate widgets: stage -- initial or replication
                         metric -- number of studies or sum of particpants
                         yaer -- the year of study conducted
    '''
    freetext_yr = freetext_df[freetext_df['Year'] == slider.value]
    if 'number of studies' in str(metric.value).lower():
        if str(stage.value) == 'Discovery':
            sorted_df = freetext_yr.\
                        sort_values(by='Initial_Ancestry_Count_%',
                                    ascending=False)
            hbar_source.data = dict(
             Cleaned_Ancestry=sorted_df['Cleaned_Ancestry'][0:10].to_list(),
             toplot=sorted_df['Initial_Ancestry_Count_%'][0:10]/100,
             indexval=sorted_df.index[0:10],
             offsetval=[0.01]*10,  # @TODO colours embedded into ancestry dict
             hbar_color=["#d7191c"]*10,
             hbar_legendval=['Initial Stage (%)']*10)
        elif str(stage.value) == 'Replication':
            sorted_df = freetext_yr.\
                        sort_values(by='Replication_Ancestry_Count_%',
                                    ascending=False)
            hbar_source.data = dict(
                Cleaned_Ancestry=sorted_df['Cleaned_Ancestry'][0:10].to_list(),
                toplot=sorted_df['Replication_Ancestry_Count_%'][0:10]/100,
                hbar_color=["#2b83ba"]*10,
                indexval=sorted_df.index[0:10],
                offsetval=[0.01]*10,
                hbar_legendval=['Replication Stage (%)']*10)
        hbar_plot.xaxis.axis_label = 'Percent of all Studies (%)'
        titletext = 'Fig 5: Free Text: ' + str(stage.value)
    elif 'number of participants' in str(metric.value).lower():
        if str(stage.value) == 'Discovery':
            sorted_df = freetext_yr.\
                        sort_values(by='Initial_Ancestry_Sum_%',
                                    ascending=False)
            hbar_source.data = dict(
                Cleaned_Ancestry=sorted_df['Cleaned_Ancestry'][0:10].to_list(),
                toplot=sorted_df['Initial_Ancestry_Sum_%'][0:10]/100,
                hbar_color=["#d7191c"]*10,
                indexval=sorted_df.index[0:10],
                offsetval=[0.01]*10,
                hbar_legendval=['Discovery Stage (%)']*10)
        elif str(stage.value) == 'Replication':
            sorted_df = freetext_yr.\
                        sort_values(by='Replication_Ancestry_Sum_%',
                                    ascending=False)
            hbar_source.data = dict(
               Cleaned_Ancestry=sorted_df['Cleaned_Ancestry'][0:10].to_list(),
               toplot=sorted_df['Replication_Ancestry_Sum_%'][0:10]/100,
               hbar_color=["#2b83ba"]*10,
               indexval=sorted_df.index[0:10],
               offsetval=[0.01]*10,
               hbar_legendval=['Replication Stage (%)']*10)
        hbar_plot.xaxis.axis_label = 'Percent of all Participants (%)'
        titletext = 'Fig 5: Free Text'
    hbar_plot.title.text = titletext + ': ' + str(slider.value) + \
        ', all Parent Categories'
    hbar_plot.title.align = "center"


def update_hbar_axis():
    '''
    Update the range (tick labels) for horizontal bar plot
    This is presently extremely hacky because the
    major_label_text_align method seems to be broken in bokeh.
    This will need rewriting in the long run
    '''
    hbar_plot.y_range.factors = hbar_source.data['Cleaned_Ancestry']
    hbar_plot.yaxis.major_label_standoff = -405
    hbar_plot.yaxis.axis_line_color = None


def create_hbar_plot():
    '''
    Creates the horizontal barplot
    Returns: hbar_hover -- the hovertool for the hbar plot
             hbar_plot -- the plot itself
             hbar_source -- for updating upon interaction
    '''
    freetext_yr = freetext_df[freetext_df['Year'] == 2018]
    sorted_df = freetext_yr.sort_values(by='Initial_Ancestry_Count_%',
                                        ascending=False)
    hbar_source = ColumnDataSource(data=dict(Cleaned_Ancestry=[], toplot=[],
                                             hbar_color=[], hbar_legendval=[]))
    hbar_source.data = dict(
     Cleaned_Ancestry=sorted_df['Cleaned_Ancestry'][0:10].to_list(),
     toplot=sorted_df['Initial_Ancestry_Count_%'][0:10]/100,
     hbar_color=["#d7191c"]*10,
     hbar_legendval=['Initial Stage (%)']*10)
    yrange = sorted_df['Cleaned_Ancestry'][0:10].to_list()
    hbar_plot = figure(y_range=yrange, x_range=(-.01, 1),
                       plot_height=width_dict['hbar_height'],
                       plot_width=width_dict['hbar_width'],
                       title="Fig 5: Free Text",
                       tools=TOOLS, toolbar_location=None,
                       y_axis_location='right')
    hbar_plot.hbar(y='Cleaned_Ancestry', right='toplot', height=0.6,
                   source=hbar_source, color='hbar_color', alpha=.6,
                   line_color="black", legend='hbar_legendval')
    hbar_hover = hbar_plot.select(dict(type=HoverTool))
    hbar_hover.tooltips = [('Ancestry Term: ', '@Cleaned_Ancestry'),
                           ('$Percent Value: ', '@toplot{0.000%}')]
    hbar_plot.xaxis.formatter = NumeralTickFormatter(format='0 %')
    hbar_plot.legend.border_line_width = 1
    vline = Span(location=-.001, dimension='height',
                 line_color='black', line_width=0.75)
    hbar_plot.renderers.extend([vline])
    hbar_plot.legend.border_line_color = "black"
    hbar_plot.outline_line_color = 'white'
    hbar_plot.yaxis.major_tick_line_color = None
    hbar_plot.yaxis.minor_tick_line_color = None
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
    ''' updates the slider and some features of the choropleth '''
    yr = slider.value
    new_data = json_data(yr)
    geosource.geojson = new_data
    choro_plot.title.text = 'Fig 4: Recruitment Over Time, ' +\
                            'All Parent Categories and Both ' +\
                            'Research Stages: %d' % yr
    choro_plot.title.align = "center"


def update_choro():
    ''' generates a new geosoruce based on slider (year) value'''
    new_data = json_data(slider.value)
    geosource.geojson = new_data


def create_choro_plot(year):
    '''
    Creates the choropleth plot.
        Inputs:
            year -- the year of the slider.
        Returns:
            geosource -- the choropleth source
            choro_plot -- the choropleth map itself
            choro_hover -- the hovertool for the choropleth map
    '''
    geosource = GeoJSONDataSource(geojson=json_data(year))
    palette = brewer['Blues'][6]   # @TODO hacky adjustment of the colourmap
    palette = palette[::-1][1:-1]
    palette[0] = '#eef2ff'
    color_map = LinearColorMapper(palette=blues[25:], low=0, high=25,
                                  nan_color='white')
    choro_plot = figure(title='Fig 4: Recruitment Over Time, All ' +
                              'Parent Categories and Both Research Stages: ' +
                              str(year),
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
    choro_plot.outline_line_color = None
    choro_plot.xgrid.grid_line_color = None
    choro_plot.ygrid.grid_line_color = None
    choro_plot.min_border_left = 80
    choro_plot.min_border_right = 0
    choro_plot.title.text = 'Fig 4: Recruitment Over Time, ' +\
                            'All Parent Categories and Both ' +\
                            'Research Stages: 2008'
    choro_plot.title.align = "center"
    return geosource, choro_hover, choro_plot


def update_ts1():
    '''
    Updates ts1_source. This needs refactoring in conjunction with update_ts2
    '''
    if str(ancestry.value) == 'All':
        ancestry_value = 'European'
    else:
        ancestry_value = str(ancestry.value)
    if 'number of studies' in str(metric.value).lower():
        if str(stage.value) == 'Discovery':
            ts1_source.data = dict(
                Year=[ts1_init_count['index']],
                ts1_toplot=[ts1_init_count[ancestry_value]/100],
                ts1_color=[["#2b83ba"]])
            ts1_plot.title.text = 'Fig 2a: Discovery Stage,' +\
                                  ' all Parent Categories: ' +\
                                  str(ancestry_value)
        elif str(stage.value) == 'Replication':
            ts1_source.data = dict(
                Year=[ts1_rep_count['index']],
                ts1_toplot=[ts1_rep_count[ancestry_value]/100],
                ts1_color=[["#d7191c"]])
            ts1_plot.title.text = 'Fig 2a: Replication Stage,' +\
                                  ' all Parent Categories: ' +\
                                  str(ancestry_value)
        ts1_plot.yaxis.axis_label = 'Percent of all Studies (%)'
    elif 'number of participants' in str(metric.value).lower():
        if str(stage.value) == 'Discovery':
            ts1_source.data = dict(
                 Year=[ts1_init_sum['index']],
                 ts1_toplot=[ts1_init_sum[ancestry_value]/100],
                 ts1_color=[["#2b83ba"]],
                 # ts_legendval=[['Discovery Stage (%)']]
                 )
            ts1_plot.title.text = 'Fig 2a: Discovery Stage,' +\
                                  ' all Parent Categories: ' +\
                                  str(ancestry_value)
        elif str(stage.value) == 'Replication':
            ts1_source.data = dict(
                 Year=[ts1_rep_sum['index']],
                 ts1_toplot=[ts1_rep_sum[ancestry_value]/100],
                 ts1_color=[["#d7191c"]],
                 # ts1_legendval=[['Replication Stage (%)']]
                 )
            ts1_plot.title.text = 'Fig 2a: Replication Stage,' +\
                                  'all Parent Categories: ' +\
                                  str(ancestry_value)
        ts1_plot.yaxis.axis_label = 'Percent of all Participants (%)'
    ts1_plot.x_range.start = slider.value


def update_ts2():
    '''
    Updates ts2_source. This needs refactoring in conjunction with update_ts1
    '''
    if str(ancestry.value) == 'All':
        ancestry_value = 'European'
    else:
        ancestry_value = str(ancestry.value)
    if 'number of studies' in str(metric.value).lower():
        if str(stage.value) == 'Discovery':
            ts2_source.data = dict(
                Year=[ts2_init_count['index']],
                ts2_toplot=[ts2_init_count[ancestry_value]/100],
                ts2_color=[["#2b83ba"]])  # Legend taken out here
            ts2_plot.title.text = 'Fig 2b: Discovery Stage,' +\
                                  ' all Parent Categories: ' +\
                                  str(ancestry_value)
        elif str(stage.value) == 'Replication':
            ts2_source.data = dict(
                Year=[ts2_rep_count['index']],
                ts2_toplot=[ts2_rep_count[ancestry_value]/100],
                ts2_color=[["#d7191c"]])  # Legend taken out here
            ts2_plot.title.text = 'Fig 2b: Replication Stage,' +\
                                  ' all Parent Categories: ' +\
                                  str(ancestry_value)
        ts2_plot.yaxis.axis_label = 'Percent of all Studies (%)'
    elif 'number of participants' in str(metric.value).lower():
        if str(stage.value) == 'Discovery':
            ts2_source.data = dict(
                 Year=[ts2_init_sum['index']],
                 ts2_toplot=[ts2_init_sum[ancestry_value]/100],
                 ts2_color=[["#2b83ba"]])  # Legend taken out here
            ts2_plot.title.text = 'Fig 2b: Discovery Stage,' +\
                                  ' all Parent Categories: ' +\
                                  str(ancestry_value)
        elif str(stage.value) == 'Replication':
            ts2_source.data = dict(
                 Year=[ts2_rep_sum['index']],
                 ts2_toplot=[ts2_rep_sum[ancestry_value]/100],
                 ts2_color=[["#d7191c"]])  # Legend taken out here
            ts2_plot.title.text = 'Fig 2b: Replication Stage,' +\
                                  'all Parent Categories: ' +\
                                  str(ancestry_value)
        ts2_plot.yaxis.axis_label = 'Percent of all Participants (%)'
    ts2_plot.x_range.start = slider.value


def create_ts1_plot(maxyear):
    '''
    Creates the first time series plot.
        Input: the year of the most recently published gwas
        Returns:
            ts1_source -- the source data which gets updated
            ts1_source -- the hovertool
            ts1_plot -- the actual time series plot
    Needs refactoring in conjunction with create_ts2_plot
    '''
    ts1_source = ColumnDataSource(data=dict(index=[], Year=[], ts1_toplot=[],
                                            ts1_color=[], ts1_legendval=[]))
    ts1_plot = figure(x_range=(2008, maxyear),
                      plot_height=width_dict['ts_height'],
                      plot_width=width_dict['ts_width'], tools=TOOLS,
                      toolbar_location=None,
                      y_axis_label='Percent of all Studies (%)',
                      title="Fig 2a: Percent of Studies Conducted (%)")
    ts1_plot.yaxis.formatter = NumeralTickFormatter(format='0 %')
    ts1_hover = ts1_plot.select(dict(type=HoverTool))
    ts1_hover.tooltips = [("Year: ", "$x{int}"),
                          ("Ancestry: ", ancestry.value),
                          ("Percentage Value: ", "$y{0.000%}")]
    ts1_plot.multi_line(xs='Year', ys='ts1_toplot', source=ts1_source,
                        alpha=0.8, line_width=2, color='ts1_color')
    ts1_plot.xgrid.grid_line_dash = 'dashed'
    ts1_plot.ygrid.grid_line_dash = 'dashed'
    ts1_plot.yaxis.formatter = NumeralTickFormatter(format='0.0 %')
    ts1_plot.outline_line_color = None
    ts1_plot.min_border_left = 100
    return ts1_source, ts1_hover, ts1_plot


def create_ts2_plot(maxyear):
    '''
    Creates the second time series plot.
        Input: the year of the most recently published gwas
        Returns:
            ts2_source -- the source data which gets updated
            ts2_source -- the hovertool
            ts2_plot -- the actual time series plot
    Needs refactoring in conjunction with create_ts1_plot
    '''
    ts2_source = ColumnDataSource(data=dict(index=[], Year=[], ts2_toplot=[],
                                            ts2_color=[], ts2_legendval=[]))
    ts2_plot = figure(x_range=(2008, maxyear),
                      plot_height=width_dict['ts_height'],
                      plot_width=width_dict['ts_width'], tools=TOOLS,
                      toolbar_location=None,
                      y_axis_label='Percent of all Studies (%)',
                      title="Fig 2b: Percent of Studies Conducted (%)")
    ts2_plot.yaxis.formatter = NumeralTickFormatter(format='0 %')
    ts2_hover = ts2_plot.select(dict(type=HoverTool))
    ts2_hover.tooltips = [("Year: ", "$x{int}"),
                          ("Ancestry: ", ancestry.value),
                          ("Percentage Value: ", "$y{0.000%}")]
    ts2_plot.multi_line(xs='Year', ys='ts2_toplot', source=ts2_source,
                        alpha=0.8, line_width=2, color='ts2_color')
    ts2_plot.xgrid.grid_line_dash = 'dashed'
    ts2_plot.ygrid.grid_line_dash = 'dashed'
    ts2_plot.yaxis.formatter = NumeralTickFormatter(format='0.0 %')
    ts2_plot.outline_line_color = None
    ts2_plot.min_border_left = 100
    return ts2_source, ts2_hover, ts2_plot


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
                         x_range=(dt.date(2008, 1, 1),
                                  bubble_df['DATE'].max()),
                         tools=TOOLS, toolbar_location=None)
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
    bubble_plot.yaxis.formatter = NumeralTickFormatter(format="0")
    return bubble_source, bubble_hover, bubble_plot


def select_ancestry_bubble():
    ''' Update the ancestry data for the bubble source'''
    ancestry_val = ancestry.value
    selected = bubble_df
    if str(ancestry_val) != 'All':
        selected = selected[selected['Broader'] == ancestry_val]
    return selected


def select_stage_bubble(df):
    ''' Update the stage data for the bubble source'''
    stage_val = stage.value
    df = df[df['STAGE'].str.title() == stage_val]
    return df


def select_parent_bubble(df):
    ''' Update the EFO parent data for the bubble source'''
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
    bubble_plot.title.text = 'Fig 1: ' + str(ancestry.value) +\
                             ' Ancestry and ' +\
                             str(parent.value) + ', ' + str(slider.value) +\
                             ' to Present Day (' + str(stage.value) + ')'
    bubble_plot.x_range.start = dt.date(slider.value, 1, 1)
    bubble_plot.title.align = "center"


def create_doughnut_plot():
    '''
        Creates the doughnut chart. Returns:
            doughnut_source -- the doughnut source data
            doughnut_hover -- the doughnut hovertools
            doughnut_plot -- the actual doughnut plot itself
    '''
    doughnut_df['Broader'] = doughnut_df['Broader'].str.\
        replace('In Part Not Recorded', 'In Part No Record')
    doughnut_source = ColumnDataSource(data=dict(Broader=[],
                                       doughnut_toplot=[],
                                       doughnut_angle=[],
                                       doughnut_color=[],
                                       parentterm=[],
                                       doughnut_stage=[]))
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
    doughnut_plot.annular_wedge(x=0.1, y=0.1, inner_radius=0.315,
                                outer_radius=0.575,
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
    doughnut_plot.legend.border_line_color = None
    doughnut_plot.legend.label_text_font_size = '8pt'
    doughnut_plot.legend.orientation = "horizontal"
    doughnut_plot.legend.location = "bottom_center"
    doughnut_plot.title.align = "center"
    doughnut_plot.outline_line_color = None
    return doughnut_source, doughnut_hover, doughnut_plot


def update_doughnut():
    '''
        Update the doughnut chart with interactive choices.
        This needs to be an ancestray based color dictionary,
        harmonized with the bubble plot.
        Ideally, this needs to be a better type of annular figure...
    '''
    colorlist = ['#3288bd', '#fee08b', '#d53e4f',
                 '#99d594', '#bdbdbd', '#fc8d59']
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
        doughnut_plot.title.text = 'Fig 3: Number Studies, ' +\
                                   str(parent.value) + ' at ' +\
                                   str(stage.value)
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
        doughnut_plot.title.text = 'Fig 3: Number Participants, ' +\
                                   str(parent.value).title() + ' at ' +\
                                   str(stage.value)


def select_parent_doughnut():
    ''' select parent data for the doughnut'''
    parent_val = parent.value
    selected = doughnut_df
    selected = selected[selected['parentterm'] == parent_val]
    return selected


width_dict = create_width_dict()
data_path = os.path.abspath(os.path.join(__file__, '..', 'data'))
template_path = os.path.abspath(os.path.join(__file__, '..',
                                             'gwasdiversitymonitor_app',
                                             'templates'))
bubble_df, freetext_df, ts1_init_count, ts1_init_sum, ts1_rep_count,\
    ts1_rep_sum, choro_df, gdf, doughnut_df, ts2_init_count,\
    ts2_init_sum, ts2_rep_count, ts2_rep_sum = import_data(data_path)
maxyear = bubble_df['DATE'].max().year
anclist = ts2_init_count.columns.tolist()[1:]  # Make ancestry list
anclist.insert(0, 'All')
parentlist = doughnut_df['parentterm'].unique().tolist() # Make parent list
stage, parent, ancestry, metric, slider = widgets(width_dict['control_width'],
                                                  parentlist, anclist, maxyear)
slider.on_change('value', update_choro_slider)
TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"
hbar_source, hbar_hover, hbar_plot = create_hbar_plot()
geosource, choro_hover, choro_plot = create_choro_plot(maxyear-1)
ts1_source, ts1_hover, ts1_plot = create_ts1_plot(maxyear)
ts2_source, ts2_hover, ts2_plot = create_ts2_plot(maxyear)
bubble_source, bubble_hover, bubble_plot = create_bubble_plot()
doughnut_source, doughnut_hover, doughnut_plot = create_doughnut_plot()

controls = [metric, ancestry, parent, stage, slider]
for control in controls:
    control.on_change('value', lambda attr, old, new: update_hbar_source())
    control.on_change('value', lambda attr, old, new: update_hbar_axis())
    control.on_change('value', lambda attr, old, new: update_choro())
    control.on_change('value', lambda attr, old, new: update_ts1())
    control.on_change('value', lambda attr, old, new: update_ts2())
    control.on_change('value', lambda attr, old, new: update_bubble())
    control.on_change('value', lambda attr, old, new: update_doughnut())
update()
controls = controls[:-1]
doughnut_plot.sizing_mode = "stretch_both"
bubble_plot.sizing_mode = "stretch_both"
choro_plot.sizing_mode = "stretch_both"
ts1_plot.sizing_mode = "stretch_both"
ts2_plot.sizing_mode = "stretch_both"
hbar_plot.sizing_mode = "stretch_both"

#  Add the plots into the jinja2 template
curdoc().add_root(row(bubble_plot, name='bubble'))
curdoc().add_root(row(choro_plot, name='choro'))
curdoc().add_root(row(ts1_plot, name='ts1'))
curdoc().add_root(row(hbar_plot, name='hbar'))
curdoc().add_root(row(doughnut_plot, name='doh'))
curdoc().add_root(row(column(*controls), slider))
curdoc().add_root(row(ts2_plot, name='ts2'))
curdoc().title = "GWAS Diversity Monitor"
