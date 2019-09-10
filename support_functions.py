import pandas as pd
import geopandas as gpd
from bokeh.models import Select, Slider
import os
from bokeh.models import Div


def create_width_dict():
    width_dict = {'hbar_height': 430, 'hbar_width': 575,
                  'choro_height': 430, 'choro_width': 775,
                  'ts_height': 430, 'ts_width': 575,
                  'bubble_height': 430, 'bubble_width': 825,
                  'doughnut_height': 305, 'doughnut_width': 425,
                  'headerbox_height': 400, 'headerbox_width': 375,
                  'control_height': 390, 'control_width': 325,
                  'slider_height': 350, 'slider_width': 30,
                  'twocolumn_width': 910, 'div_width': 20,
                  'div_height': 900}
    return width_dict


def load_divs(width_dict):
    header = Div(text=open(os.path.join(os.path.dirname(__file__),
                                        'html_pages',"header.html")).read(),
                width=int(0.5*width_dict['twocolumn_width']),
                height=int(0.12*width_dict['div_height']))
    downloaddata = Div(text=open(os.path.join(os.path.dirname(__file__),
                                        'html_pages',"downloaddata.html")).read(),
                width=int(0.5*width_dict['twocolumn_width']),
                height=int(0.225*width_dict['div_height']))
    about = Div(text=open(os.path.join(os.path.dirname(__file__),
                                       'html_pages', "about.html")).read(),
                width=width_dict['twocolumn_width'],
                height=int(0.7*width_dict['div_height']))
    footer = Div(text=open(os.path.join(os.path.dirname(__file__),
                                        'html_pages', "footer.html")).read(),
                width=width_dict['twocolumn_width'],
                height=int(0.3*width_dict['div_height']))
    dumdiv = Div(text='',
                 width=width_dict['div_width'],
                 height=int(0.001*width_dict['div_height']))
    summary = Div(text=open(os.path.join(os.path.dirname(__file__),
                            'html_pages', "summary_stats.html")).read(),
                  width=width_dict['twocolumn_width'],
                  height=int(0.475*width_dict['div_height']))
    return header, about, dumdiv, summary, footer, downloaddata


def import_data(data_path):
    bubble_df = pd.read_csv(os.path.join(data_path, 'toplot',
                                         'bubble_df.csv'),
                            parse_dates=['DATE'])
    bubble_df['STAGE'] = bubble_df['STAGE'].str.replace('initial', 'Discovery')
    bubble_df = bubble_df[bubble_df['Broader'].notnull()]
    bubble_df = bubble_df[bubble_df['N'].notnull()]
    bubble_df = bubble_df.drop_duplicates(subset=['Broader', 'DATE',
                                                  'PUBMEDID', 'STAGE',
                                                  'AUTHOR', 'parentterm',
                                                  'STUDY ACCESSION'])
    freetext_df = pd.read_csv(os.path.join(data_path, 'toplot',
                                           'freetext_merged.csv'))
    ts_init_count = pd.read_csv(os.path.join(data_path, 'toplot',
                                             'ts_initial_count.csv'))
    ts_init_sum = pd.read_csv(os.path.join(data_path, 'toplot',
                                           'ts_initial_sum.csv'))
    ts_rep_count = pd.read_csv(os.path.join(data_path, 'toplot',
                                            'ts_replication_count.csv'))
    ts_rep_sum = pd.read_csv(os.path.join(data_path, 'toplot',
                                          'ts_replication_sum.csv'))
    choro_df, gdf = prepare_geo_data(os.path.join(data_path, 'toplot',
                                                  'choro_df.csv'),
                                     os.path.join(data_path, 'shapefiles',
                                                  'ne_110m_admin_0_countries.shp'))
    doughnut_df = pd.read_csv(os.path.join(data_path, 'toplot', 'doughnut_df.csv'))
    return bubble_df, freetext_df, ts_init_count, ts_init_sum,\
        ts_rep_count, ts_rep_sum, choro_df, gdf, doughnut_df


def widgets(control_width, slider_height,
            slider_width, bubble_df, ts_init_count, maxyear):
    stage = Select(title="Research Stage", value="Discovery",
                   options=['Discovery', 'Replication'],
                   width=control_width)
    parent = Select(title="Parent Term", value="Cancer",
                    options=bubble_df['parentterm'].unique().tolist(),
                    width=control_width)
    ancestry = Select(title="Broader Ancestry", value="European",
                      options=ts_init_count.columns.tolist()[1:],
                      width=control_width)
    metric = Select(title="Evaluation Metric",
                    value="Number of Participants (%)",
                    options=["Number of Studies (%)",
                             "Number of Participants (%)"],
                    width=control_width)
    slider = Slider(title='', start=2008, end=maxyear-1, step=1,
                    orientation="vertical", width=slider_width,
                    height=slider_height, value=maxyear-1)
    return stage, parent, ancestry, metric, slider


def prepare_geo_data(df_path, shapefile_path):
    choro_df = pd.read_csv(df_path, index_col='index')
    choro_df['Year'] = pd.to_numeric(choro_df['Year'])
    gdf = gpd.read_file(shapefile_path)[['ADMIN', 'ADM0_A3', 'geometry']]
    gdf.columns = ['country', 'country_code', 'geometry']
    gdf = gdf[gdf['country'] != 'Antarctica']
    gdf['country'] = gdf['country'].str.replace('United States of America',
                                                'United States')
    gdf['country'] = gdf['country'].str.replace('South Korea',
                                                'Korea, South')
    gdf['country'] = gdf['country'].str.replace('United Republic of Tanzania',
                                                'Tanzania')
    gdf['country'] = gdf['country'].str.replace('Gambia', 'Gambia, The')
    gdf['country'] = gdf['country'].str.\
        replace('Federated States of Micronesia',
                'Micronesia, Federated States of')
    gdf['country'] = gdf['country'].str.replace('Republic of Serbia',
                                                'Serbia')
    choro_df['N'] = choro_df['N']/1000000
    return choro_df, gdf
