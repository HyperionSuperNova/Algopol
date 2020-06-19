import pandas as pd
import os
import csv
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import dask.dataframe as dd


def get_ego_id(ego_path):
    return os.path.splitext(os.path.basename(ego_path))[0][:8]


def add_value_to_dict(dico, key, val):
    if key in dico.keys():
        dico[key] = dico[key] + val
    else:
        dico[key] = val


def mean_recent_alter_ego(csvobj):
    len_recent_alter = 0
    count_recent_alter = 0
    for row in csvobj:
        len_recent_alter += 1
        count_recent_alter += int(row['AlterCount'])
    if len_recent_alter > 0:
        return count_recent_alter / len_recent_alter
    return -1


def read_csv_in_folder(folder_path):
    mean_alter_dict = {}
    nb_ego_treated = 0
    for file in os.listdir(folder_path):
        filename = os.fsdecode(file)
        path_to_file = os.path.join(folder_path, filename)
        if filename.endswith(".csv"):
            with open(path_to_file, newline='') as csvfile:
                csvobj = csv.DictReader(csvfile)
                id_ego = get_ego_id(filename)
                mean_recent_alter = round(mean_recent_alter_ego(csvobj))
                if mean_recent_alter != -1:
                    add_value_to_dict(mean_alter_dict, mean_recent_alter, 1)
    return mean_alter_dict


def recent_alters_freq_perc_df(folder_path):
    mean_alter_dict = read_csv_in_folder(folder_path)
    df = pd.DataFrame(mean_alter_dict.items())
    df = df.rename(columns={0: "Mean", 1: "Nbego"})
    df['Percentage'] = df.Nbego.apply(lambda x: x/df['Nbego'].sum() * 100)
    df.rename(columns={'Mean': 'Average_Recent_Ties',
                       'Nbego': 'Frequency'}, inplace=True)
    df.sort_values(by=['Average_Recent_Ties'], inplace=True)
    return df


def all_recent_alters_csv_to_df(folder_path):
    df_dask = dd.read_csv(folder_path, include_path_column=True)
    df_dask['egos'] = df_dask['path'].str.split('/').str[-1]
    df_dask['egos'] = df_dask['egos'].str.split('_').str[0]
    df_dask = df_dask.drop('path', axis=1)
    return df_dask.compute()


def age_gender_profession_csv_to_df(file_path):
    return dd.read_csv(file_path).compute()


def merged_df(df1, df2):
    df_merged = df2.merge(df1, on='egos')
    df_merged['age_range'] = pd.cut(
        x=df_merged['age'], bins=[0, 18, 30, 59, 75, 100])
    return df_merged


def mean_age_df_binned(df_merged):
    df_mean = df_merged[df_merged.age.notna()].groupby(
        ['egos', 'age_range'], as_index=False).AlterCount.mean()
    df_mean.rename(columns={'AlterCount': 'Mean_Alter_Count'}, inplace=True)
    df_mean = df_mean[df_mean.Mean_Alter_Count.notna()]\
        .groupby(['age_range'], as_index=False)\
        .agg({'Mean_Alter_Count': 'mean', 'egos': 'count'})
    df_mean['age_range_str'] = df_mean['age_range'].astype(str)
    return df_mean


def mean_age_df(df_merged):
    df_mean = df_merged[df_merged.age.notna()]\
        .groupby(['egos', 'age'], as_index=False)\
        .AlterCount\
        .mean()
    df_mean.rename(columns={'AlterCount': 'Mean_Alter_Count'}, inplace=True)
    return df_mean


def mean_gender_df(df_merged):
    df_mean = df_merged[df_merged.gender.notna()].groupby(
        ['egos', 'gender'], as_index=False).AlterCount.mean()
    df_mean.rename(columns={'AlterCount': 'Mean_Alter_Count'}, inplace=True)
    df_mean = df_mean[df_mean.Mean_Alter_Count.notna()].groupby(['gender'], as_index=False)\
        .agg({'Mean_Alter_Count': 'mean', 'egos': 'count'})
    return df_mean


def mean_professions(df_merged):
    df_mean = df_merged[df_merged.profession.notna()].groupby(
        ['egos', 'profession'], as_index=False).AlterCount.mean()
    df_mean.rename(columns={'AlterCount': 'Mean_Alter_Count'}, inplace=True)
    df_mean = df_mean[df_mean.Mean_Alter_Count.notna()].groupby(['profession'], as_index=False)\
        .agg({'Mean_Alter_Count': 'mean', 'egos': 'count'})
    return df_mean
