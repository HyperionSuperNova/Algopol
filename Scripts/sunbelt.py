import dask.dataframe as dd
import pandas as pd
import numpy as np
import os
import csv

cluster_order_path = '/home/data/algopol/algopolapp/results/Imera/Cluster_order/Egos/*'
output_egos_path = '/home/data/algopol/user/nabil/Sunbelt/filtered_egos_id.txt'
output_csv_path = '/home/data/algopol/user/nabil/Sunbelt/filtered_egos_month_year_cluster.csv'
#cluster_order_path = '../sunbelt/Cluster_order/sample/*'
#output_egos_path = '../output/sunbelt/filtered_egos_id_test.txt'
#output_csv_path = '../output/sunbelt/filtered_egos_month_year_cluster_test.csv'


def prepare_dataframe(dataframe):
    dataframe['egos'] = dataframe['path'].str.split('/').str[-1]
    dataframe['egos'] = dataframe['egos'].str.split(
        '_').str[0].str.split('.').str[0]
    dataframe['month_year'] = dataframe['month']
    dataframe['year'] = dataframe['month_year'].str.split('_').str[0]
    dataframe['month'] = dataframe['month_year'].str.split('_').str[1]
    dataframe = dataframe.drop('path', axis=1)
    df_pandas = dataframe.compute(scheduler='processes')
    df_pandas['month_year'] = pd.to_datetime(
        df_pandas.month_year, format='%Y_%m')
    df_pandas['month'] = pd.to_datetime(df_pandas.month, format='%m').dt.month
    return df_pandas


def dask_load_csv():
    df_dask = dd.read_csv(cluster_order_path,
                          include_path_column=True, blocksize=1000000)

    return prepare_dataframe(df_dask)


def prepare_csv():
    if os.path.exists(output_csv_path):
        os.remove(output_csv_path)


def prepare_txt():
    if os.path.exists(output_egos_path):
        os.remove(output_egos_path)


def is_cons_month(monthdiff, val):
    count = 0
    for x in monthdiff:
        if count == val:
            return True
        if x == 1 or x == -11:
            count += 1
        else:
            count = 0
    return False


def dom_clust_date(dataframe, consecutive_months):
    count = 0
    for index, row in dataframe.iterrows():
        if count == consecutive_months:
            return (row['month'], row['year'], True)
        if row['monthdiff'] == 1 or row['monthdiff'] == -11:
            count += 1
        else:
            count = 0
    return('', '', False)


def write_to_csv(csv_list, dicowriter):
    for row in csv_list:
        dicowriter.writerow(row)


def write_to_txt(txt_writer, ego):
    txt_writer.write(ego+"\n")


def process_cluster(ego_clusters, filter, consecutive_months, ego, dicowriter):
    count_clust = 0
    csv_candidate = []
    txt_writer = open(output_egos_path, 'a+')
    for cluster in ego_clusters:
        dico_tmp = {}
        filter2 = filter[(filter.first_cluster == cluster)
                         ].sort_values('month_year')
        filter2['monthdiff'] = filter.groupby(
            'first_cluster').month.diff().fillna(1).astype(int)
        month, year, is_cons_month = dom_clust_date(
            filter2, consecutive_months)
        if is_cons_month:
            count_clust += 1
            dico_tmp['ego'] = ego
            dico_tmp['cluster'] = cluster
            dico_tmp['month'] = month
            dico_tmp['year'] = year
            csv_candidate.append(dico_tmp)
        if count_clust >= 2:
            write_to_txt(txt_writer, ego)
            write_to_csv(csv_candidate, dicowriter)
            break


def egos_list_consecutive_months(dataframe, ratio, consecutive_months, val_brute):
    all_egos = dataframe.egos.unique()
    filtered_egos = np.array([])
    csv_list = []
    csvf = open(output_csv_path, 'a')
    dicowriter = csv.DictWriter(
        csvf, fieldnames=['ego', 'cluster', 'month', 'year'], delimiter=',')
    dicowriter.writeheader()
    for ego in all_egos:
        count_clust = 0
        csv_candidate = []
        filter = dataframe[(dataframe.egos == ego) & (
            dataframe.ratio_over_second >= ratio) & (dataframe.nb_posts >= val_brute)]
        ego_clusters = filter.first_cluster.unique()
        process_cluster(ego_clusters, filter,
                        consecutive_months, ego, dicowriter)


if __name__ == "__main__":
    dataframe = dask_load_csv()
    prepare_csv()
    prepare_txt()
    egos_list_consecutive_months(dataframe, 2, 6, 10)
