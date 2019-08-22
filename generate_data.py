import pandas as pd
import json
import logging
import datetime
import numpy as np
import requests
import requests_ftp
import os
import re
import csv
import logging


def setup_logging(logpath):
    if os.path.exists(logpath) is False:
        os.makedirs(logpath)
    logger = logging.getLogger('diversity_logger')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler((os.path.abspath(
        os.path.join(logpath, 'diversity_logger.log'))))
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def create_summarystats(data_path):
    Cat_Stud = pd.read_csv(os.path.join(data_path, 'catalog',
                                        'raw', 'Cat_Stud.tsv'),
                           sep='\t', low_memory=False)
    Cat_Full = pd.read_csv(os.path.join(data_path, 'catalog',
                                        'raw', 'Cat_Full.tsv'),
                           sep='\t', low_memory=False)
    Cat_Anc_withBroader = pd.read_csv(os.path.join(data_path, 'catalog',
                                                   'synthetic',
                                                   'Cat_Anc_withBroader.tsv'),
                                      '\t', index_col=False, low_memory=False)
    sumstats = {}
    sumstats['number_studies'] = int(len(Cat_Stud['PUBMEDID'].unique()))
    sumstats['first_study_date'] = str(Cat_Stud['DATE'].min())
    dateminauth = Cat_Stud.loc[Cat_Stud['DATE'] == Cat_Stud['DATE'].min(),
                               'FIRST AUTHOR']
    sumstats['first_study_firstauthor'] = str(dateminauth.iloc[0])
    dateminpubmed = Cat_Stud.loc[Cat_Stud['DATE'] == Cat_Stud['DATE'].min(),
                                 'PUBMEDID']
    sumstats['first_study_pubmedid'] = int(dateminpubmed.iloc[0])
    sumstats['last_study_date'] = str(Cat_Stud['DATE'].max())
    datemaxauth = Cat_Stud.loc[Cat_Stud['DATE'] == Cat_Stud['DATE'].max(),
                               'FIRST AUTHOR']
    sumstats['last_study_firstauthor'] = str(datemaxauth.iloc[0])
    datemaxpubmed = Cat_Stud.loc[Cat_Stud['DATE'] == Cat_Stud['DATE'].max(),
                                 'PUBMEDID']
    sumstats['last_study_pubmedid'] = int(datemaxpubmed.iloc[0])
    sumstats['number_accessions'] = int(len(Cat_Stud['STUDY ACCESSION'].
                                            unique()))
    sumstats['number_diseasestraits'] = int(len(Cat_Stud['DISEASE/TRAIT'].
                                                unique()))
    sumstats['number_mappedtrait'] = int(len(Cat_Stud['MAPPED_TRAIT'].
                                             unique()))
    sumstats['found_associations'] = int(Cat_Stud['ASSOCIATION COUNT'].
                                         sum())
    sumstats['average_associations'] = float(Cat_Stud['ASSOCIATION COUNT'].
                                             mean())
    sumstats['average_pval'] = int(round(Cat_Full['P-VALUE'].astype(float).
                                         mean(), 10))
    sumstats['threshold_pvals'] = int(len(Cat_Full[Cat_Full['P-VALUE'].
                                          astype(float) < 5.000000e-8]))
    sumstats['mostcommon_journal'] = str(Cat_Stud['JOURNAL'].mode()[0])
    sumstats['unique_journals'] = int(len(Cat_Stud['JOURNAL'].unique()))
    Cat_Anc_byN = Cat_Anc_withBroader[['STUDY ACCESSION', 'N']].\
        groupby(by='STUDY ACCESSION').sum()
    Cat_Anc_byN = Cat_Anc_byN.reset_index()
    Cat_Anc_withBroader = Cat_Anc_withBroader.\
        drop_duplicates('STUDY ACCESSION')[['PUBMEDID', 'FIRST AUTHOR',
                                            'STUDY ACCESSION']]
    Cat_Anc_byN = pd.merge(Cat_Anc_byN, Cat_Anc_withBroader, how='left',
                           left_on='STUDY ACCESSION',
                           right_on='STUDY ACCESSION')
    sumstats['large_accesion_N'] = int(Cat_Anc_byN.
                                       sort_values(by='N',
                                                   ascending=False)['N'].
                                       iloc[0])
    biggestauth = Cat_Anc_byN.loc[Cat_Anc_byN['N'] ==
                                  sumstats['large_accesion_N'],
                                  'FIRST AUTHOR']
    sumstats['large_accesion_firstauthor'] = str(biggestauth.iloc[0])
    biggestpubmed = Cat_Anc_byN.loc[Cat_Anc_byN['N'] ==
                                    sumstats['large_accesion_N'],
                                    'PUBMEDID']
    sumstats['large_accesion_pubmed'] = int(biggestpubmed.iloc[0])
    json_path = os.path.join(data_path, 'summary', 'summary.json')
    with open(json_path, 'w') as outfile:
        json.dump(sumstats, outfile)
    return sumstats


def update_summarystats(sumstats, summaryfile):
    with open(summaryfile, 'r') as file:
        summary = file.readlines()
    summary[-15] = '<li> There are a total of ' + \
                   str(sumstats['number_studies']) +\
                   ' studies in the Catalog.</li>\n'
    summary[-14] = '<li> Earliest study in catalogued was PubMedID ' +\
                   str(sumstats['first_study_pubmedid']) + ' on ' +\
                   str(sumstats['first_study_date']) + ' by ' +\
                   str(sumstats['first_study_firstauthor']) +\
                   ' et al.</li>\n'
    summary[-13] = '<li> Most recent study in catalogued was PubMedID ' +\
                   str(sumstats['last_study_pubmedid']) + ' on ' +\
                   str(sumstats['last_study_date']) + ' by ' +\
                   str(sumstats['last_study_firstauthor']) +\
                   ' et al.</li>\n'
    summary[-12] = '<li> Accession with biggest sample is PubMedID ' +\
                   str(sumstats['large_accesion_pubmed']) + ' (N=' +\
                   str(sumstats['large_accesion_N']) + ') by ' +\
                   str(sumstats['large_accesion_firstauthor']) +\
                   ' et al.</li>\n'
    summary[-11] = '<li> There are a total of ' +\
                   str(sumstats['number_accessions']) +\
                   ' unique study accessions.</li>\n'
    summary[-10] = '<li> There are a total of ' +\
                   str(sumstats['number_diseasestraits']) +\
                   ' unique diseases\traits studied.</li>\n'
    summary[-9] = '<li> There are a total of ' +\
                  str(sumstats['number_mappedtrait']) +\
                  ' unique EBI "Mapped Traits".</li>\n'
    summary[-8] = '<li> The total number of associations found is ' +\
                  str(sumstats['found_associations']) +\
                  '.</li>\n'
    summary[-7] = '<li> The average number of associations found is ' +\
                  str(round(sumstats['average_associations'], 2)) + '.</li>\n'
    summary[-6] = '<li> Mean P-Value for the strongest SNP risk allele is: ' +\
                  str(round(sumstats['average_pval'], 8)) + '.</li>\n'
    summary[-5] = '<li> The number of associations reaching the 5e-8 threshold: ' +\
                  str(sumstats['threshold_pvals']) + '.</li>\n'
    summary[-4] = '<li> The journal to feature the most GWAS studies is: ' +\
                  str(sumstats['mostcommon_journal']) + '.</li>\n'
    summary[-3] = '<li> Total number of different journals publishing GWAS is: ' +\
                  str(sumstats['unique_journals']) + '.</li>\n'
    with open(summaryfile, 'w') as file:
        file.writelines(summary)


def update_header(headerfile):
    ''' update the 'last updated' part of the header on both tabs '''
    today = datetime.date.today()
    with open(headerfile, 'r') as file:
        header = file.readlines()
    header[-1] = 'Last updated: ' +\
                 datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +\
                 ' GMT <br>'
    with open(headerfile, 'w') as file:
        file.writelines(header)


def ancestry_cleaner(row, field):
    """ clean up the ancestry fields in GWASCatalogue_Ancestry.

    Keyword arguments:
    row: the row of the ancestry DataFrame
    field: the field of the ancestry dataframe ('initial' or 'replication')
    """
    free_text = re.sub(r'(\d+),?([\d+]?)', r'\1\2', str(row[field]))
    free_text = re.sub(r'(\d+)', r'; \1', str(free_text))
    free_text = punctuation_cleaner(free_text)
    free_text = remove_lower(free_text)
    free_text = remove_lower(free_text)
    free_text = free_text.replace('  ', ' ')
    free_text = free_text.replace('  ', ' ')
    free_text = list_remover(free_text)
    free_text = dict_replace(free_text)
    try:
        if free_text[-1] == ';':
            free_text = free_text[:-1]
    except ValueError:
        pass
    cleaned = []
    for ancestry in free_text[1:].split(';'):
        if " and" in ancestry.strip()[-4:]:
            cleaned.append(ancestry.replace(' and', '').strip())
        elif " or" in ancestry.strip()[-4:]:
            cleaned.append(ancestry.replace(' or', '').strip())
        else:
            cleaned.append(ancestry.strip())
    cleaned = ';'.join(cleaned)
    cleaned = cleaned.replace(';', ' ; ')
    for word in cleaned.split(' '):
        if (word.isalpha()) and (len(word) < 3) and word != "or":
            cleaned = cleaned.replace(word, '')
    cleaned = re.sub(r';\s+;', ';', cleaned)
    return cleaned


def make_heatmatrix(merged, stage, out_path):
    merged = merged[merged['STAGE'] == stage]
    ancestry_ranking = pd.DataFrame(merged.groupby(['Broader'])['Broader'].
                                    count()).rename({'Broader': 'Count'},
                                                    axis=1).\
        sort_values(ascending=False, by='Count')
    parent_ranking = pd.DataFrame(merged.groupby(['parentterm'])['parentterm'].
                                  count()).rename({'parentterm': 'Count'}, axis=1).\
        sort_values(ascending=False, by='Count')
    df_count = pd.DataFrame(index=ancestry_ranking.index.tolist(),
                            columns=parent_ranking.index.tolist())
    for index in df_count.index:
        for column in df_count.columns:
            df_count.at[index,
                        column] = len(merged[(merged['Broader'] == index) &
                                             (merged['parentterm'] == column)])

    df_count.to_csv(os.path.join(out_path, 'heatmap_count_'+stage+'.csv'))
    ancestry_ranking = pd.DataFrame(merged.groupby(['Broader'])['N'].
                                    sum()).\
        sort_values(ascending=False, by='N')
    parent_ranking = pd.DataFrame(merged.groupby(['parentterm'])['N'].
                                  sum()).sort_values(ascending=False, by='N')
    df_sum = pd.DataFrame(index=ancestry_ranking.index.tolist(),
                          columns=parent_ranking.index.tolist())
    for index in df_sum.index:
        for column in df_sum.columns:
            df_sum.at[index,
                      column] = merged[(merged['Broader'] == index) &
                                       (merged['parentterm'] == column)]['N'].\
                                       sum()
    df_sum.to_csv(os.path.join(out_path, 'heatmap_sum_'+stage+'.csv'))


def make_heatmap_dfs(data_path):
    Cat_Stud = pd.read_csv(os.path.join(data_path, 'catalog',
                                        'raw', 'Cat_Stud.tsv'), sep='\t')
    Cat_Stud = Cat_Stud[Cat_Stud['MAPPED_TRAIT_URI'].notnull()]
    with open(os.path.join(data_path,
                           'catalog',
                           'synthetic',
                           'Mapped_EFO.csv'), 'w') as fileout:
        efo_out = csv.writer(fileout, delimiter=',', lineterminator='\n')
        efo_out.writerow(['EFO URI', 'STUDY ACCESSION',
                          'PUBMEDID', 'ASSOCIATION COUNT'])
        for index, row in Cat_Stud.iterrows():
            listoftraits = row['MAPPED_TRAIT_URI'].split(',')
            for trait in listoftraits:
                efo_out.writerow([trait.lower().strip(),
                                  row['STUDY ACCESSION'],
                                  str(row['PUBMEDID']),
                                  str(row['ASSOCIATION COUNT'])])
    EFOsPerPaper = pd.read_csv(os.path.join(data_path,
                                            'catalog',
                                            'synthetic',
                                            'Mapped_EFO.csv'), sep=',')
    EFO_Parent_Map = pd.read_csv(os.path.join(data_path,
                                              'catalog',
                                              'raw',
                                              'Cat_Map.tsv'), sep='\t')
    EFO_Parent_Map = EFO_Parent_Map.rename(columns={"Parent term":
                                                    "parentterm"})
    EFO_Parent_Map['EFO URI'] = EFO_Parent_Map['EFO URI'].str.lower(
    ).str.strip()
    EFO_Parent_Map = EFO_Parent_Map[[
        'EFO URI', 'parentterm', 'EFO term']].drop_duplicates()
    EFO_Parent_Paper_Merged = pd.merge(
        EFOsPerPaper, EFO_Parent_Map, on='EFO URI', how='left')
    Cat_Anc_withBroader = pd.read_csv(os.path.join(data_path,
                                                   'catalog',
                                                   'synthetic',
                                                   'Cat_Anc_withBroader.tsv'),
                                      '\t', index_col=False)
    merged = pd.merge(EFO_Parent_Paper_Merged[['STUDY ACCESSION',
                                               'parentterm']],
                      Cat_Anc_withBroader[['STUDY ACCESSION',
                                           'Broader', 'N', 'STAGE']],
                      how='left', on='STUDY ACCESSION')
    make_heatmatrix(merged, 'initial', os.path.join(data_path,
                                                    'toplot'))
    make_heatmatrix(merged, 'replication', os.path.join(data_path,
                                                        'toplot'))


def dict_replace(text):
    """ sanitize the free text strings from the initial/replication fields.

    Keyword arguements:
    text: the free text string prior to splitting
    """
    replacedict = {'Arabian': 'Arab', 'HIspanic': 'Hispanic',
                   'Korculan': 'Korcula', 'Hispaic': 'Hispanic',
                   'Hispanics': 'Hispanic', 'Chineses': 'Chinese',
                   'Europea ': 'European ', 'Finish': 'Finnish',
                   'Val Bbera': 'Val Borbera', 'Chinese Han': 'Han Chinese',
                   'Erasmus Rchen': 'Erasmus Rucphen', 'Cilen ': 'Cilento',
                   'Erasmus Rupchen': 'Erasmus Rucphen', 'Clien': 'Cilento',
                   'Erasmus Ruchpen': 'Erasmus Rucphen', 'Geman': 'German',
                   'Old Amish': 'Old Order Amish', 'Americans': 'American',
                   'Japnese': 'Japanese', 'Finland': 'Finnish',
                   'Eat Aian': 'East Asian', 'Hipanic': 'Hispanic',
                   'Sub African': 'Sub-saharan African', 'Israeli': 'Isreali',
                   'Erasmus Rucphen Family': 'Erasmus Rucphen',
                   'Nfolk Island': 'Norfolk Island', 'Sh Asian': 'Asian',
                   'Hispanic Latino': 'Hispanic/Latino', 'Uighur': 'Uyghur',
                   'Hispanic Latin ': 'Hispanic/Latino',
                   'European ad': 'European', 'Val Bbera': 'Val Borbera',
                   'European End': 'European', 'Oceanian': 'Oceania',
                   'LatinoAmerican': 'Latino American', 'Giuli': 'Giulia',
                   'Cilentoto': 'Cilento', 'Friuli': 'Fruili',
                   'Giuliaa': 'Giulia', 'Rupchen': 'Rucphen', '≥': '',
                   'Korcula': 'Korkulan', 'Ruchpen': 'Rucphen',
                   'Brazillian': 'Brazilian', 'Sub-saharan': 'Sub Saharan',
                   'Tyrolian': 'Tyrolean', 'Seychelles': 'Seychellois',
                   'South Tyrolean': 'South Tyrol', 'Europen': 'European'}
    for key in replacedict:
        if key in text:
            text = text.replace(key, replacedict[key])
    return text


def list_remover(text):
    """ titlecase/capitalised words to remove from the strings which
    are not associated with countries, races or ancestries.

    Keyword arguements:
    text: the free text string prior to splitting
    """
    removelist = ['AIS', 'APOE', 'HIV', 'Â', 'HER2-', '1000 Genomes',
                  'MYCN-amplification', 'Alzheimer', 'ASD', 'OCB', 'BD',
                  'Genetically', 'Homogenous', 'BRCA', 'ALL', 'Coronary',
                  'Amyotrophic', 'Large', 'anti-dsDNA', 'Up ', 'Biracial',
                  'Follicular', 'Hodgkin', 'Lymphoma', 'GI', 'Abstinent',
                  'Schizophrenia', 'Îµ', 'JAK', 'ADHD', 'Diabetes',
                  'Allogenic', 'BGPI', 'Ischemic', 'Chronic', 'Major',
                  'Diabetic', 'Microalbuminuria', 'Asthma', 'Individuals',
                  'At ', "Barrett's", 'Crohn', 'Bipolar', 'MMR', 'HBV', 'RA',
                  'Elated', 'Escitalpram', 'Irritable', 'Lymphoblastoid',
                  'ACPA', 'HCC', 'pPhe508del', 'Anti', 'B2GPI', 'Kashin Beck',
                  '(LDL-cholesterol)', 'TPO', 'OCD', 'CCT', 'FTD', 'CAPOX B',
                  'LAC', 'LOAD', ' So ', 'MYCN-amplification', 'Yang', 'Tae',
                  'Eum', 'Non-abstinent', 'EBWL', 'Semantic', 'General',
                  'Cluster', 'Frontremporal', 'Frontotremporal',
                  'Frontotemporal', 'Graves', 'Attention', 'Autism', 'Liu',
                  'High', 'Low', 'HCV', 'Citalopram', 'Haemophilia', ' III ',
                  ' II ', ' I ', 'NFT', 'Progressive', 'Ancestry', 'Parkinson',
                  'Lin', 'BMD', 'GBA', 'Traylor', 'Consortium', ' Torgerson',
                  'EVE', 'Germain', 'Boraska', 'Cases', 'HapMap', 'vWF', 'HDL',
                  'LDL', ' Mild', 'Cognitive', 'Impairment', 'Sarcoidosis',
                  'Yu Zhi', 'Lymphoma', 'Impairment', 'Type', 'Kuru',
                  'Frontemporal', 'Erasmus', 'Barrett', 'Lofgren', 'Hashimoto',
                  'Family', 'Multiple', 'Richardson', 'Metropolitan']
    for word in removelist:
        text = text.replace(word, '')
    return text


def remove_lower(free_text):
    """ remove lowercase letters (assumed to not be associated with
    countries, races or ancestries.)

    Keyword arguements:
    text: the free text string prior to splitting
    """
    free_text = free_text.replace('up to', '')
    for word in free_text.split(' '):
        if (word.title() != word.strip()):
            try:
                float(word)
            except ValueError:
                if ';' in word:
                    free_text = free_text.replace(word, ';').strip()
                elif (';' not in word) and (word != "and") and (word != "or"):
                    if free_text.find(word) == 0:
                        free_text = free_text.replace(word + ' ', ' ')
                    else:
                        free_text = free_text.replace(' ' + word, ' ')
    return free_text.strip()


def punctuation_cleaner(temp):
    """ remove various punctuation (assumed to not be associated with
    countries, races or ancestries.)

    Keyword arguements:
    text: the free text string prior to splitting
    """
    temp = temp.replace(',', ';')
    for pmark in ['-', '\'', '’', '?', '+']:
        temp = temp.replace(pmark, ' ')
    for pmark in ['(', ')', '.', '*', '~', '<', '>']:
        temp = temp.replace(pmark, '')
    return temp


def ancestry_parser(output_path, input_series, Cat_Studies):
    ''' Parse single individual ancestries from the free text
        based on capitalisations '''
    with open(output_path, 'w', encoding='utf-8') as csv_file:
        fileout = csv.writer(csv_file, delimiter=',', lineterminator='\n')
        fileout.writerow(['STUDY ACCESSION', 'Cleaned_Ancestry',
                          'Cleaned_Ancestry_Size'])
        for index, row in Cat_Studies.iterrows():
            checksum = 0
            for ancestry in row[input_series].split(';'):
                number = re.findall(r'\d+', ancestry.strip())
                if (len(number) == 1):
                    checksum += 1
            if checksum == len(row[input_series].split(';')):
                for ancestry in row[input_series].split(';'):
                    number = re.findall(r'\d+', ancestry.strip())
                    words = ''.join(i for i in ancestry.strip() if not i.isdigit())
                    if (len(number) == 1) and (len(words.strip()) > 3) and \
                       (sum(1 for c in words if c.isupper()) > 0):
                        fileout.writerow([row['STUDY ACCESSION'],
                                          words.strip(), str(number[0])])


def make_choro_df(data_path):
    Cat_Ancestry = pd.read_csv(os.path.join(data_path,
                                            'catalog',
                                            'synthetic',
                                            'Cat_Anc_withBroader.tsv'),
                               sep='\t')
    annual_df = pd.DataFrame(columns=['Year', 'N', 'Count'])
    Clean_CoR = make_clean_CoR(Cat_Ancestry)
    countrylookup = pd.read_csv(os.path.join(data_path,
                                             'shapefiles',
                                             'Country_Lookup.csv'),
                                index_col='Country')
    for year in range(2008, 2020):
        tempdf = Clean_CoR[Clean_CoR['Date'].str.contains(str(year))]
        tempdf_sum = pd.DataFrame(
            tempdf.groupby(['Cleaned Country'])['N'].sum())
        tempdf_count = pd.DataFrame(
            tempdf.groupby(['Cleaned Country'])['N'].count()).\
            rename(columns={'N': 'Count'})
        tempdf_merged = pd.merge(tempdf_sum, tempdf_count,
                                 left_index=True, right_index=True)
        tempdf_merged['Year'] = str(year)
        country_merged = pd.merge(countrylookup, tempdf_merged,
                                  left_index=True,
                                  right_index=True)
        country_merged = country_merged.reset_index()
        country_merged['Count (%)'] = round((pd.to_numeric(
                                             country_merged['Count']) /
                                             pd.to_numeric(
                                             country_merged['Count']).sum())
                                            * 100, 2)
        country_merged['N (%)'] = round((pd.to_numeric(
                                         country_merged['N']) /
                                         pd.to_numeric(
                                         country_merged['N'].sum()))
                                        * 100, 2)
        annual_df = annual_df.append(country_merged, sort=True)
    annual_df = annual_df.reset_index().drop(['level_0'], axis=1)
    del annual_df.index.name
    annual_df.to_csv(os.path.join('data', 'toplot', 'choro_df.csv'))


def make_timeseries_df(Cat_Ancestry):
    Cat_Ancestry = Cat_Ancestry[Cat_Ancestry['Broader'] !=
                                'In Part Not Recorded']
    DateSplit = Cat_Ancestry['DATE'].str.\
        split('-', expand=True).\
        rename({0: 'Year', 1: 'Month', 2: 'Day'}, axis=1)
    Cat_Ancestry = pd.merge(Cat_Ancestry, DateSplit, how='left',
                            left_index=True, right_index=True)
    Cat_Ancestry['Year'] = pd.to_numeric(Cat_Ancestry['Year'])
    Cat_Ancestry['Month'] = pd.to_numeric(Cat_Ancestry['Month'])
    broader_list = Cat_Ancestry['Broader'].unique().tolist()
    ts_initial_sum = pd.DataFrame(index=range(2007, 2020),
                                  columns=broader_list)
    ts_replication_sum = pd.DataFrame(index=range(2007, 2020),
                                      columns=broader_list)
    ts_initial_count = pd.DataFrame(index=range(2007, 2020),
                                    columns=broader_list)
    ts_replication_count = pd.DataFrame(index=range(2007, 2020),
                                        columns=broader_list)
    for ancestry in broader_list:
        for year in range(2007, 2020):
            temp_df = Cat_Ancestry[(Cat_Ancestry['Year'] == year) &
                                   (Cat_Ancestry['Broader'] == ancestry) &
                                   (Cat_Ancestry['STAGE'] == 'initial')]
            ts_initial_sum.at[year, ancestry] = temp_df['N'].sum()
            ts_initial_count.at[year, ancestry] = len(temp_df['N'])
            temp_df = Cat_Ancestry[(Cat_Ancestry['Year'] == year) &
                                   (Cat_Ancestry['Broader'] == ancestry) &
                                   (Cat_Ancestry['STAGE'] == 'replication')]
            ts_replication_sum.at[year, ancestry] = temp_df['N'].sum()
            ts_replication_count.at[year, ancestry] = len(temp_df['N'])
    ts_initial_sum_pc = ((ts_initial_sum.T / ts_initial_sum.T.sum()).T)*100
    ts_initial_sum_pc = ts_initial_sum_pc.reset_index()
    ts_initial_sum_pc.to_csv(os.path.join('data', 'toplot',
                                          'ts_initial_sum.csv'), index=False)
    ts_initial_count_pc = ((ts_initial_count.T /
                            ts_initial_count.T.sum()).T)*100
    ts_initial_count_pc = ts_initial_count_pc.reset_index()
    ts_initial_count_pc.to_csv(os.path.join('data', 'toplot',
                                            'ts_initial_count.csv'),
                               index=False)
    ts_replication_sum_pc = ((ts_replication_sum.T /
                              ts_replication_sum.T.sum()).T)*100
    ts_replication_sum_pc = ts_replication_sum_pc.reset_index()
    ts_replication_sum_pc.to_csv(os.path.join('data', 'toplot',
                                              'ts_replication_sum.csv'),
                                 index=False)
    ts_replication_count_pc = ((ts_replication_count.T /
                                ts_replication_count.T.sum()).T)*100
    ts_replication_count_pc = ts_replication_count_pc.reset_index()
    ts_replication_count_pc.to_csv(os.path.join('data', 'toplot',
                                                'ts_replication_count.csv'),
                                   index=False)


def make_freetext_dfs(data_path):
    Cat_Studies = pd.read_csv(os.path.join(data_path,
                                           'catalog',
                                           'raw',
                                           'Cat_Stud.tsv'),
                              sep='\t')
    Cat_Studies['InitialClean'] = Cat_Studies.apply(
        lambda row: ancestry_cleaner(row, 'INITIAL SAMPLE SIZE'), axis=1)
    output_path = os.path.abspath(
                  os.path.join(data_path,
                               'catalog',
                               'synthetic',
                               'new_initial_sample.csv'))
    ancestry_parser(output_path, 'InitialClean', Cat_Studies)
    Cat_Studies['ReplicationClean'] = Cat_Studies.apply(
        lambda row: ancestry_cleaner(row, 'REPLICATION SAMPLE SIZE'), axis=1)
    output_path = os.path.abspath(
                  os.path.join(data_path,
                               'catalog',
                               'synthetic',
                               'new_replication_sample.csv'))
    ancestry_parser(output_path, 'ReplicationClean', Cat_Studies)
    clean_intial = pd.read_csv(os.path.abspath(
                               os.path.join(data_path,
                                            'catalog', 'synthetic',
                                            'new_initial_sample.csv')),
                               encoding='utf-8')
    clean_initial_sum = pd.DataFrame(
        clean_intial.groupby(['Cleaned_Ancestry']).sum())
    clean_initial_sum.rename(
        columns={'Cleaned_Ancestry_Size': 'Initial_Ancestry_Sum'},
        inplace=True)
    clean_initial_count = clean_intial.groupby(['Cleaned_Ancestry']).count()
    clean_initial_count.rename(
        columns={'Cleaned_Ancestry_Size': 'Initial_Ancestry_Count'},
        inplace=True)
    clean_initial_merged = clean_initial_sum.merge(pd.DataFrame(
        clean_initial_count['Initial_Ancestry_Count']),
        how='outer', left_index=True, right_index=True)
    clean_initial_merged = clean_initial_merged.sort_values(
        by='Initial_Ancestry_Sum', ascending=False)
    clean_initial_merged['Initial_Ancestry_Sum_%'] =\
        (clean_initial_merged['Initial_Ancestry_Sum'] /
         clean_initial_merged['Initial_Ancestry_Sum'].sum())*100
    clean_initial_merged['Initial_Ancestry_Count_%'] =\
        (clean_initial_merged['Initial_Ancestry_Count'] /
         clean_initial_merged['Initial_Ancestry_Count'].sum())*100
    clean_replication = pd.read_csv(os.path.abspath(
                                    os.path.join(
                                        data_path, 'catalog', 'synthetic',
                                        'new_replication_sample.csv')),
                                    encoding='utf-8')
    clean_replication_sum = pd.DataFrame(
        clean_replication.groupby(['Cleaned_Ancestry']).sum())
    clean_replication_sum.rename(
        columns={'Cleaned_Ancestry_Size': 'Replication_Ancestry_Sum'},
        inplace=True)
    clean_replication_count = clean_replication.groupby(
        ['Cleaned_Ancestry']).count()
    clean_replication_count.rename(
        columns={'Cleaned_Ancestry_Size': 'Replication_Ancestry_Count'},
        inplace=True)
    clean_replication_merged = clean_replication_sum.merge(
        pd.DataFrame(clean_replication_count['Replication_Ancestry_Count']),
        how='outer', left_index=True, right_index=True)
    clean_replication_merged = clean_replication_merged.sort_values(
        by='Replication_Ancestry_Sum', ascending=False)
    clean_initial_merged = clean_initial_merged.sort_values(
        by='Initial_Ancestry_Sum', ascending=False)
    clean_replication_merged['Replication_Ancestry_Sum_%'] =\
        (clean_replication_merged['Replication_Ancestry_Sum'] /
         clean_replication_merged['Replication_Ancestry_Sum'].sum())*100
    clean_replication_merged['Replication_Ancestry_Count_%'] =\
        (clean_replication_merged['Replication_Ancestry_Count'] /
         clean_replication_merged['Replication_Ancestry_Count'].sum())*100
    merged = pd.merge(clean_initial_merged,
                      clean_replication_merged,
                      left_on='Cleaned_Ancestry',
                      right_on='Cleaned_Ancestry',
                      how='outer')
    merged.to_csv(os.path.join(data_path, 'toplot', 'freetext_merged.csv'))


def make_dohnut_df(data_path):
    Cat_Stud = pd.read_csv(os.path.join(data_path, 'catalog',
                                        'raw', 'Cat_Stud.tsv'),
                           sep='\t')
    Cat_Stud = Cat_Stud[Cat_Stud['MAPPED_TRAIT_URI'].notnull()]
    with open(os.path.join(data_path,  'catalog', 'synthetic',
                           'Mapped_EFO.csv'), 'w') as fileout:
        efo_out = csv.writer(fileout, delimiter=',', lineterminator='\n')
        efo_out.writerow(['EFO URI', 'STUDY ACCESSION',
                          'PUBMEDID', 'ASSOCIATION COUNT'])
        for index, row in Cat_Stud.iterrows():
            listoftraits = row['MAPPED_TRAIT_URI'].split(',')
            for trait in listoftraits:
                efo_out.writerow([trait.lower().strip(),
                                  row['STUDY ACCESSION'],
                                  str(row['PUBMEDID']),
                                  str(row['ASSOCIATION COUNT'])])
    EFOsPerPaper = pd.read_csv(os.path.join(data_path, 'catalog', 'synthetic',
                                            'Mapped_EFO.csv'), sep=',')
    EFO_Parent_Map = pd.read_csv(os.path.join(data_path, 'catalog', 'raw',
                                              'Cat_Map.tsv'), sep='\t')
    EFO_Parent_Map = EFO_Parent_Map.rename(columns={"Parent term":
                                                    "parentterm"})
    EFO_Parent_Map['EFO URI'] = EFO_Parent_Map['EFO URI'].str.\
        lower().str.strip()
    EFO_Parent_Map = EFO_Parent_Map[[
        'EFO URI', 'parentterm', 'EFO term']].drop_duplicates()
    EFO_Parent_Paper_Merged = pd.merge(
        EFOsPerPaper, EFO_Parent_Map, on='EFO URI', how='left')
    Cat_Anc_withBroader = pd.read_csv(os.path.join(data_path,
                                                   'catalog', 'synthetic',
                                                   'Cat_Anc_withBroader.tsv'),
                                      '\t', index_col=False)
    merged = pd.merge(EFO_Parent_Paper_Merged[['STUDY ACCESSION',
                                               'parentterm']],
                      Cat_Anc_withBroader[['STUDY ACCESSION',
                                           'Broader', 'N', 'STAGE']],
                      how='left', on='STUDY ACCESSION')
    dohnut_df = pd.DataFrame(index=[], columns=['Broader', 'parentterm',
                                                'InitialN', 'ReplicationN',
                                                'InitialCount',
                                                'ReplicationCount'])
    merged = merged[merged['Broader'].notnull()]
    merged = merged[merged['parentterm'].notnull()]
    counter = 0
    for ancestry in merged['Broader'].unique().tolist():
        dohnut_df.at[counter, 'Broader'] = ancestry
        dohnut_df.at[counter, 'parentterm'] = 'All'
        dohnut_df.at[counter,
                     'ReplicationN'] = (merged[(
                                        merged['STAGE'] == 'replication') &
                                        (merged['Broader'] == ancestry)]['N'].
                                        sum() /
                                        merged[merged['STAGE'] ==
                                        'replication']['N'].sum())*100
        dohnut_df.at[counter, 'InitialN'] = (merged[(merged['STAGE'] ==
                                                     'initial') &
                                                    (merged['Broader'] ==
                                                     ancestry)]['N'].sum() /
                                             merged[merged['STAGE'] ==
                                                    'initial']['N'].sum())*100
        dohnut_df.at[counter, 'ReplicationCount'] = (len(merged[
                                                         (merged['Broader'] ==
                                                          ancestry)]) /
                                                     len(merged[
                                                          merged['STAGE'] ==
                                                         'replication']))*100
        dohnut_df.at[counter, 'InitialCount'] = (len(merged[
                                                     (merged['STAGE'] ==
                                                      'initial') &
                                                     (merged['Broader'] ==
                                                      ancestry)]) /
                                                 len(merged[merged['STAGE'] ==
                                                            'initial']))*100
        counter = counter + 1
        for parent in merged['parentterm'].unique().tolist():
            dohnut_df.at[counter, 'Broader'] = ancestry
            dohnut_df.at[counter, 'parentterm'] = parent
            dohnut_df.at[counter,
                         'ReplicationN'] = (merged[
                                            (merged['STAGE'] == 'replication') &
                                            (merged['parentterm'] == parent) &
                                            (merged['Broader'] == ancestry)]['N'].sum() /
                                            merged[(merged['STAGE'] == 'replication') &
                                            (merged['parentterm'] == parent)]['N'].sum())*100
            dohnut_df.at[counter,
                         'InitialN'] = (merged[(merged['STAGE'] == 'initial') &
                                               (merged['Broader'] == ancestry) &
                                               (merged['parentterm'] == parent)]['N'].sum() /
                                        merged[(merged['STAGE'] == 'initial') &
                                               (merged['parentterm'] == parent)]['N'].sum())*100
            dohnut_df.at[counter,
                         'ReplicationCount'] = (len(merged[
                                                   (merged['STAGE'] == 'replication') &
                                                   (merged['parentterm'] == parent) &
                                                   (merged['Broader'] == ancestry)]) /
                                                len(merged[
                                                   (merged['STAGE'] == 'replication') &
                                                   (merged['parentterm'] == parent)])) * 100
            dohnut_df.at[counter,
                         'InitialCount'] = (len(merged[
                                               (merged['STAGE'] == 'initial') &
                                               (merged['parentterm'] == parent) &
                                               (merged['Broader'] == ancestry)]) /
                                            len(merged[
                                               (merged['STAGE'] == 'initial') &
                                               (merged['parentterm'] == parent)])) * 100
            counter = counter + 1
    dohnut_df['Broader'] = dohnut_df['Broader'].str.\
        replace('African Am./Caribbean', 'Af. Am./Carib.')
    dohnut_df['Broader'] = dohnut_df['Broader'].str.\
        replace('Hispanic/Latin American', 'Hispanic/L.A.')
    dohnut_df.to_csv(os.path.join('data', 'toplot', 'dohnut_df.csv'))


def make_bubbleplot_df(data_path):
    Cat_Stud = pd.read_csv(os.path.join(data_path, 'catalog',
                                        'raw', 'Cat_Stud.tsv'),
                           sep='\t')
    Cat_Stud = Cat_Stud[Cat_Stud['MAPPED_TRAIT_URI'].notnull()]
    with open(os.path.join(data_path, 'catalog', 'synthetic',
                           'Mapped_EFO.csv'), 'w') as fileout:
        efo_out = csv.writer(fileout, delimiter=',', lineterminator='\n')
        efo_out.writerow(['EFO URI', 'STUDY ACCESSION',
                          'PUBMEDID', 'ASSOCIATION COUNT'])
        for index, row in Cat_Stud.iterrows():
            listoftraits = row['MAPPED_TRAIT_URI'].split(',')
            for trait in listoftraits:
                efo_out.writerow([trait.lower().strip(),
                                  row['STUDY ACCESSION'],
                                  str(row['PUBMEDID']),
                                  str(row['ASSOCIATION COUNT'])])
    EFOsPerPaper = pd.read_csv(os.path.join(data_path, 'catalog',
                                            'synthetic', 'Mapped_EFO.csv'),
                               sep=',')
    EFO_Parent_Map = pd.read_csv(os.path.join(data_path, 'catalog',
                                              'raw', 'Cat_Map.tsv'),
                                 sep='\t')
    EFO_Parent_Map = EFO_Parent_Map.rename(columns={"Parent term":
                                                    "parentterm"})
    EFO_Parent_Map['EFO URI'] = EFO_Parent_Map['EFO URI'].str.lower(
    ).str.strip()
    EFO_Parent_Map = EFO_Parent_Map[[
        'EFO URI', 'parentterm', 'EFO term']].drop_duplicates()
    EFO_Parent_Paper_Merged = pd.merge(
        EFOsPerPaper, EFO_Parent_Map, on='EFO URI', how='left')
    Cat_Anc_withBroader = pd.read_csv(os.path.join(data_path,
                                                   'catalog',
                                                   'synthetic',
                                                   'Cat_Anc_withBroader.tsv'),
                                      '\t', index_col=False,
                                      parse_dates=['DATE'])
    merged = pd.merge(EFO_Parent_Paper_Merged[['STUDY ACCESSION',
                                               'parentterm']],
                      Cat_Anc_withBroader, how='left', on='STUDY ACCESSION')
    merged["AUTHOR"] = merged["FIRST AUTHOR"]
    merged = merged[["Broader", "N", "PUBMEDID", "AUTHOR",
                     "STAGE", 'DATE', "STUDY ACCESSION", "parentterm"]]
    merged = merged[merged['Broader'] != 'In Part Not Recorded']
    merged["color"] = 'black'
    merged["color"] = np.where(merged["Broader"] == 'European',
                               "#3288bd", merged["color"])
    merged["color"] = np.where(merged["Broader"] == 'Asian',
                               "#d53e4f", merged["color"])
    merged["color"] = np.where(merged["Broader"] == 'African Am./Caribbean',
                               "#fee08b", merged["color"])
    merged["color"] = np.where(merged["Broader"] == 'Hispanic/Latin American',
                               "#807dba", merged["color"])
    merged["color"] = np.where(merged["Broader"] == 'Other/Mixed',
                               "#99d594", merged["color"])
    merged["color"] = np.where(merged["Broader"] == 'African',
                               "#fc8d59", merged["color"])
    merged.to_csv(os.path.join('data', 'toplot', 'bubble_df.csv'))


def clean_gwas_cat(data_path):
    Cat_Stud = pd.read_csv(os.path.join(data_path, 'catalog',
                                        'raw', 'Cat_Stud.tsv'),
                           header=0, sep='\t', encoding='utf-8',
                           index_col=False)
    Cat_Stud.fillna('N/A', inplace=True)
    Cat_Anc = pd.read_csv(os.path.join(data_path, 'catalog', 'raw',
                                       'Cat_Anc.tsv'),
                          header=0, sep='\t', encoding='utf-8',
                          index_col=False)
    Cat_Anc.rename(columns={'BROAD ANCESTRAL CATEGORY': 'BROAD ANCESTRAL',
                            'NUMBER OF INDIVDUALS': 'N'}, inplace=True)
    Cat_Anc = Cat_Anc[~Cat_Anc['BROAD ANCESTRAL'].isnull()]
    Cat_Anc.columns = Cat_Anc.columns.str.replace('ACCCESSION', 'ACCESSION')
    Cat_Anc_byN = Cat_Anc[['STUDY ACCESSION', 'N',
                           'DATE']].groupby(by='STUDY ACCESSION').sum()
    Cat_Anc_byN = Cat_Anc_byN.reset_index()
    Cat_Anc_byN = pd.merge(Cat_Anc_byN, Cat_Stud[[
        'STUDY ACCESSION', 'DATE']], how='left', on='STUDY ACCESSION')
    cleaner_broad = pd.read_csv(os.path.join(data_path, 'support',
                                             'dict_replacer_broad.tsv'),
                                sep='\t', header=0, index_col=False)
    Cat_Anc = pd.merge(Cat_Anc, cleaner_broad, how='left',
                       on='BROAD ANCESTRAL')
    Cat_Anc['Dates'] = [pd.to_datetime(d) for d in Cat_Anc['DATE']]
    Cat_Anc['N'] = pd.to_numeric(Cat_Anc['N'], errors='coerce')
    Cat_Anc = Cat_Anc[Cat_Anc['N'].notnull()]
    Cat_Anc['N'] = Cat_Anc['N'].astype(int)
    Cat_Anc = Cat_Anc.sort_values(by='Dates')
    Cat_Anc['Broader'] = Cat_Anc['Broader'].str.replace(
        'African American or Afro-Caribbean', 'African Am./Caribbean')
    Cat_Anc['Broader'] = Cat_Anc['Broader'].str.replace(
        'Hispanic or Latin American', 'Hispanic/Latin American')
    Cat_Anc.to_csv(os.path.join(data_path, 'catalog', 'synthetic',
                                'Cat_Anc_withBroader.tsv'),
                   sep='\t', index=False)
    if len(Cat_Anc[Cat_Anc['Broader'].isnull()]) > 0:
        diversity_logger.debug('Wuhoh! Need to update dictionary terms:\n' +
              '\n'.join(Cat_Anc[Cat_Anc['Broader'].
                        isnull()]['BROAD ANCESTRAL'].unique()))


def make_clean_CoR(Cat_Anc):
    """ clean the country of recruitment field for the geospatial analysis
    """
    with open(os.path.abspath(
              os.path.join('data', 'catalog', 'synthetic',
                           'ancestry_CoR.csv')), 'w') as fileout:
        rec_out = csv.writer(fileout, delimiter=',', lineterminator='\n')
        rec_out .writerow(['Date', 'PUBMEDID', 'N', 'Cleaned Country'])
        for index, row in Cat_Anc.iterrows():
            if len(row['COUNTRY OF RECRUITMENT'].split(',')) == 1:
                rec_out .writerow([row['DATE'],
                                   str(row['PUBMEDID']),
                                   str(row['N']),
                                   row['COUNTRY OF RECRUITMENT']])
    Clean_CoR = pd.read_csv(os.path.abspath(
                            os.path.join('data', 'catalog', 'synthetic',
                                         'ancestry_CoR.csv')))
    Clean_CoR['Cleaned Country'] = Clean_CoR['Cleaned Country'].str.replace(
        'U.S.', 'United States')
    Clean_CoR['Cleaned Country'] = Clean_CoR['Cleaned Country'].str.replace(
        'Gambia', 'Gambia, The')
    Clean_CoR['Cleaned Country'] = Clean_CoR['Cleaned Country'].str.replace(
        'U.K.', 'United Kingdom')
    Clean_CoR['Cleaned Country'] = Clean_CoR['Cleaned Country'].str.replace(
        'Republic of Korea', 'Korea, South')
    Clean_CoR['Cleaned Country'] = Clean_CoR['Cleaned Country'].str.replace(
        'Czech Republic', 'Czechia')
    Clean_CoR['Cleaned Country'] = Clean_CoR['Cleaned Country'].str.replace(
        'Russian Federation', 'Russia')
    Clean_CoR['Cleaned Country'] = Clean_CoR['Cleaned Country'].str.replace(
        'Iran \(Islamic Republic of\)', 'Iran')
    Clean_CoR['Cleaned Country'] = Clean_CoR['Cleaned Country'].str.replace(
        'Viet Nam', 'Vietnam')
    Clean_CoR['Cleaned Country'] = Clean_CoR['Cleaned Country'].str.replace(
        'United Republic of Tanzania', 'Tanzania')
    Clean_CoR['Cleaned Country'] = Clean_CoR['Cleaned Country'].str.replace(
        'Republic of Ireland', 'Ireland')
    Clean_CoR['Cleaned Country'] = Clean_CoR['Cleaned Country'].str.replace(
        'Micronesia \(Federated States of\)',
        'Micronesia, Federated States of')
    Clean_CoR = Clean_CoR[Clean_CoR['Cleaned Country'] != 'NR']
#    print('Cleaning for single country of recruitment:\n' +
#          str(round((len(Clean_CoR) / len(Cat_Anc)) * 100, 2)) +
#          '% of the rows remain.')
#    print(str(round((Clean_CoR['N'].sum() / Cat_Anc['N'].sum()) * 100, 2)) +
#          '% of the N remains.')
    Clean_CoR.to_csv(os.path.abspath(
                     os.path.join('data', 'catalog', 'synthetic',
                                  'GWAScatalogue_CleanedCountry.tsv')),
                     sep='\t', index=False)
    return Clean_CoR


def download_cat(data_path, ebi_download):
    """ download the data from the ebi main site and ftp"""
    try:
        r = requests.get(ebi_download + 'studies_alternative')
        if r.status_code == 200:
            with open(os.path.join(data_path, 'catalog', 'raw',
                                   'Cat_Stud.tsv'), 'wb') as tsvfile:
                tsvfile.write(r.content)
            catstud_name = r.headers['Content-Disposition'].split('=')[1]
            diversity_logger.info('Successfully downloaded ' + catstud_name)
        else:
            diversity_logger.debug('Problem downloading the Cat_Stud file...')
        r = requests.get(ebi_download + 'ancestry')
        if r.status_code == 200:
            with open(os.path.join(data_path, 'catalog', 'raw',
                                   'Cat_Anc.tsv'), 'wb') as tsvfile:
                tsvfile.write(r.content)
            catanc_name = r.headers['Content-Disposition'].split('=')[1]
            diversity_logger.info('Successfully downloaded ' + catanc_name)
        else:
            diversity_logger.debug('Problem downloading the Cat_Anc file...')
        if r.status_code == 200:
            r = requests.get(ebi_download + 'full')
            with open(os.path.join(data_path, 'catalog', 'raw',
                                   'Cat_Full.tsv'), 'wb') as tsvfile:
                tsvfile.write(r.content)
            catfull_name = r.headers['Content-Disposition'].split('=')[1]
            diversity_logger.info('Successfully downloaded ' + catfull_name)
        else:
            diversity_logger.debug('Problem downloading the Cat_full file...')
        requests_ftp.monkeypatch_session()
        s = requests.Session()
        ftpsite = 'ftp://ftp.ebi.ac.uk/'
        subdom = '/pub/databases/gwas/releases/latest/'
        file = 'gwas-efo-trait-mappings.tsv'
        r = s.get(ftpsite+subdom+file)
        if r.status_code == 200:
            with open(os.path.join(data_path, 'catalog', 'raw',
                                   'Cat_Map.tsv'), 'wb') as tsvfile:
                tsvfile.write(r.content)
            diversity_logger.info('Successfully downloaded efo-trait-mappings')
        else:
            diversity_logger.debug('Problem downloading efo-trait-mappings file...')
    except Exception as e:
        diversity_logger.debug('Problem downloading the Catalog data!' + str(e))

if __name__ == "__main__":
    logpath = os.path.abspath(os.path.join(__file__, '..', 'logging'))
    diversity_logger = setup_logging(logpath)
    data_path = os.path.abspath(os.path.join('data'))
    ebi_download = 'https://www.ebi.ac.uk/gwas/api/search/downloads/'
    try:
        download_cat(data_path, ebi_download)
        clean_gwas_cat(data_path)
        make_bubbleplot_df(data_path)
        make_dohnut_df(data_path)
        make_timeseries_df(pd.read_csv(os.path.join(data_path, 'catalog',
                                                    'synthetic',
                                                    'Cat_Anc_withBroader.tsv'),
                                       sep='\t'))
        make_choro_df(data_path)
        make_freetext_dfs(data_path)
        make_heatmap_dfs(data_path)
        update_header(os.path.abspath(
                      os.path.join(__file__, '..',
                                   'html_pages', 'header.html')))
        sumstats = create_summarystats(data_path)
        update_summarystats(sumstats, os.path.abspath(
                                      os.path.join(__file__, '..', 'html_pages',
                                                   'summary_stats.html')))
        diversity_logger.info('generate_data.py ran successfully!')
    except Exception as e:
        diversity_logger.debug('generate_data.py failed, uncaught error: ' +
                               str(e))
    logging.shutdown()
