import pandas as pd
import os
import csv
import matplotlib.pyplot as plt
import seaborn as sns
import dask.dataframe as dd
from alters_count import get_ego_id, add_value_to_dict

egos_recent_alter_count_path = '../../results/Alter-count-csv-plots/*/csv/*'
egos_sociocat_path = '../../results/egos-age-gender-profession.csv'
plot_output = '../../results/link_dynamics_plot/'

############################################################ Loading ##########################################################


def load_alters_count():
    df_dask = dd.read_csv(egos_recent_alter_count_path,
                          include_path_column=True)
    df_dask['egos'] = df_dask['path'].str.split('/').str[-1]
    df_dask['egos'] = df_dask['egos'].str.split('_').str[0]
    df_dask = df_dask.drop('path', axis=1)
    return df_dask.compute()


def load_egos_sociocat():
    return dd.read_csv(egos_sociocat_path).compute()


def sociocat_altercount_merged(alters_count, sociocat):
    df_merged = sociocat.merge(alters_count, on='egos')
    df_merged['age_range'] = pd.cut(
        x=df_merged['age'], bins=[0, 18, 30, 59, 75, 100])
    return df_merged


############################################################ Computations ##########################################################

def avg_alters_distribution(alters_count):
    alters_count['MeanAlterCount'] = alters_count['AlterCount']
    avg_df = alters_count.groupby('egos', as_index=False).agg({
        'MeanAlterCount': 'mean'})
    avg_df['RoundedMean'] = avg_df.MeanAlterCount.apply(lambda x: round(x))
    avg_df = avg_df.groupby(
        'RoundedMean', as_index=False).agg({'egos': 'count'})
    avg_df.rename(columns={'MeanAlterCount': 'Average_Recent_Ties',
                           'egos': 'Frequency'}, inplace=True)
    avg_df['Percentage'] = avg_df.Frequency.apply(
        lambda x: x/avg_df['Frequency'].sum() * 100)
    return avg_df


def median_alters_distribution(alters_count):
    alters_count['MedianAlterCount'] = alters_count['AlterCount']
    median_df = alters_count.groupby('egos', as_index=False).agg(
        {'MedianAlterCount': 'median'})
    median_df = median_df.groupby(
        'MedianAlterCount', as_index=False).agg({'egos': 'count'})
    median_df.rename(columns={'MedianAlterCount': 'Median_Recent_Ties',
                              'egos': 'Frequency'}, inplace=True)
    median_df['Percentage'] = median_df.Frequency.apply(
        lambda x: x/median_df['Frequency'].sum() * 100)
    return median_df


def median_ego_bin_age_distribution(df_merged):
    df_median = df_merged[df_merged.age.notna()].groupby(
        ['egos', 'age_range'], as_index=False).AlterCount.median()
    df_median.rename(
        columns={'AlterCount': 'Median_Alter_Count'}, inplace=True)
    df_median = df_median[df_median.Median_Alter_Count.notna()]\
        .groupby(['age_range'], as_index=False)\
        .agg({'Median_Alter_Count': 'median', 'egos': 'count'})
    df_median['age_range_str'] = df_median['age_range'].astype(str)
    return df_median


def mean_ego_bin_age_distribution(df_merged):
    df_mean = df_merged[df_merged.age.notna()].groupby(
        ['egos', 'age_range'], as_index=False).AlterCount.mean()
    df_mean.rename(columns={'AlterCount': 'Mean_Alter_Count'}, inplace=True)
    df_mean = df_mean[df_mean.Mean_Alter_Count.notna()]\
        .groupby(['age_range'], as_index=False)\
        .agg({'Mean_Alter_Count': 'mean', 'egos': 'count'})
    df_mean['age_range_str'] = df_mean['age_range'].astype(str)
    return df_mean


def mean_ego_age_distribution(df_merged):
    df_mean = df_merged[df_merged.age.notna()]\
        .groupby(['egos', 'age'], as_index=False)\
        .AlterCount\
        .mean()
    df_mean.rename(columns={'AlterCount': 'Mean_Alter_Count'}, inplace=True)
    return df_mean


def median_ego_age_distribution(df_merged):
    df_median = df_merged[df_merged.age.notna()]\
        .groupby(['egos', 'age'], as_index=False)\
        .AlterCount\
        .median()
    df_median.rename(
        columns={'AlterCount': 'Median_Alter_Count'}, inplace=True)
    return df_median


def mean_ego_gender_distribution(df_merged):
    df_mean = df_merged[df_merged.gender.notna()].groupby(
        ['egos', 'gender'], as_index=False).AlterCount.mean()
    df_mean.rename(columns={'AlterCount': 'Mean_Alter_Count'}, inplace=True)
    df_mean = df_mean[df_mean.Mean_Alter_Count.notna()].groupby(['gender'], as_index=False)\
        .agg({'Mean_Alter_Count': 'mean', 'egos': 'count'})
    return df_mean


def median_ego_gender_distribution(df_merged):
    df_median = df_merged[df_merged.gender.notna()].groupby(
        ['egos', 'gender'], as_index=False).AlterCount.median()
    df_median.rename(
        columns={'AlterCount': 'Median_Alter_Count'}, inplace=True)
    df_median = df_median[df_median.Median_Alter_Count.notna()].groupby(['gender'], as_index=False)\
        .agg({'Median_Alter_Count': 'median', 'egos': 'count'})
    return df_median


def mean_ego_professions_distribution(df_merged):
    df_mean = df_merged[df_merged.profession.notna()].groupby(
        ['egos', 'profession'], as_index=False).AlterCount.mean()
    df_mean.rename(columns={'AlterCount': 'Mean_Alter_Count'}, inplace=True)
    df_mean = df_mean[df_mean.Mean_Alter_Count.notna()].groupby(['profession'], as_index=False)\
        .agg({'Mean_Alter_Count': 'mean', 'egos': 'count'})
    return df_mean


def median_ego_professions_distribution(df_merged):
    df_median = df_merged[df_merged.profession.notna()].groupby(
        ['egos', 'profession'], as_index=False).AlterCount.median()
    df_median.rename(
        columns={'AlterCount': 'Median_Alter_Count'}, inplace=True)
    df_median = df_median[df_median.Median_Alter_Count.notna()].groupby(['profession'], as_index=False)\
        .agg({'Median_Alter_Count': 'median', 'egos': 'count'})
    return df_median

############################################################ Plotting ##########################################################


def avg_alters_distribution_plot(dataframe):
    out = plot_output + 'avg_alter_dist_linear.png'
    g = sns.catplot(x="RoundedMean", y="Frequency",
                    data=dataframe, kind="bar", height=20, aspect=40/20)
    g = g.set_xticklabels(g.ax.get_xticklabels(), rotation=45, ha="right")
    g.savefig(out)
    out = plot_output + 'avg_alter_dist_log.png'
    g = sns.catplot(x="RoundedMean", y="Frequency",
                    data=dataframe, kind="bar", height=20, aspect=40/20)
    g = g.set(xscale='log')
    g.savefig(out)


def median_alters_distribution_plot(dataframe):
    out = plot_output + 'median_alter_dist_linear.png'
    g = sns.catplot(x="Median_Recent_Ties", y="Frequency",
                    data=dataframe, kind="bar", height=30, aspect=30/20)
    g = g.set_xticklabels(g.ax.get_xticklabels(), rotation=45, ha="right")
    g.savefig(out)
    out = plot_output + 'median_alter_dist_log.png'
    g = sns.catplot(x="Median_Recent_Ties", y="Frequency",
                    data=dataframe, kind="bar", height=30, aspect=30/20)
    g = g.set(xscale='log')
    g.savefig(out)


def mean_ego_age_distribution_plot(dataframe):
    out = plot_output + 'mean_ego_age_dist.png'
    g = sns.relplot(x='age', y='Mean_Alter_Count', data=dataframe,
                    kind='line', ci=None, height=8, aspect=20/8)
    g.savefig(out)


def median_ego_age_distribution_plot(dataframe):
    out = plot_output + 'median_ego_age_dist.png'
    g = sns.relplot(x='age', y='Median_Alter_Count', data=dataframe,
                    kind='line', ci=None, height=8, aspect=20/8)
    g.savefig(out)


def mean_ego_bin_age_distribution_plot(dataframe):
    out = plot_output + 'mean_ego_bin_age_dist.png'
    g = sns.relplot(x='age_range_str', y='Mean_Alter_Count',
                    data=dataframe, kind='line', height=8)
    g.savefig(out)


def median_ego_bin_age_distribution_plot(dataframe):
    out = plot_output + 'median_ego_bin_age_dist.png'
    g = sns.relplot(x='age_range_str', y='Median_Alter_Count',
                    data=dataframe, kind='line', height=8)
    g.savefig(out)


def mean_ego_gender_distribution_plot(dataframe):
    out = plot_output + 'mean_ego_gender_dist.png'
    g = sns.catplot(x='gender', y='Mean_Alter_Count',
                    data=dataframe, height=8)
    g.savefig(out)


def median_ego_gender_distribution_plot(dataframe):
    out = plot_output + 'median_ego_gender_dist.png'
    g = sns.catplot(x='gender', y='Median_Alter_Count',
                    data=dataframe, height=8)
    g.savefig(out)


def mean_ego_professions_distribution_plot(dataframe):
    out = plot_output + 'mean_ego_professions_dist.png'
    g = sns.catplot(x="profession", y="Mean_Alter_Count",
                    data=dataframe, kind="bar", height=8)
    g.savefig(out)


def median_ego_professions_distribution_plot(dataframe):
    out = plot_output + 'median_ego_professions_dist.png'
    g = sns.catplot(x="profession", y="Median_Alter_Count",
                    data=dataframe, kind="bar", height=8)
    g.savefig(out)


if __name__ == "__main__":
    alters_count = load_alters_count()
    sociocat = load_egos_sociocat()
    altercount_sociocat = sociocat_altercount_merged(alters_count, sociocat)
    avg_alters_distribution_plot(avg_alters_distribution(alters_count))
    median_alters_distribution_plot(median_alters_distribution(alters_count))
    mean_ego_age_distribution_plot(
        mean_ego_age_distribution(altercount_sociocat))
    median_ego_age_distribution_plot(
        median_ego_age_distribution(altercount_sociocat))
    mean_ego_bin_age_distribution_plot(
        mean_ego_bin_age_distribution(altercount_sociocat))
    median_ego_bin_age_distribution_plot(
        median_ego_bin_age_distribution(altercount_sociocat))
    mean_ego_gender_distribution_plot(
        mean_ego_gender_distribution(altercount_sociocat))
    median_ego_gender_distribution_plot(
        median_ego_gender_distribution(altercount_sociocat))
    mean_ego_professions_distribution_plot(
        mean_ego_professions_distribution(altercount_sociocat))
    median_ego_professions_distribution_plot(median_ego_professions_distribution(
        altercount_sociocat))
