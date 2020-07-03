import dask.dataframe as dd
import pandas as pd
import numpy as np

cluster_order_path = '/home/data/algopol/algopolapp/results/Imera/Cluster_order/Egos/*'


def prepare_dataframe(dataframe):
    dataframe['egos'] = dataframe['path'].str.split('/').str[-1]
    dataframe['egos'] = dataframe['egos'].str.split(
        '_').str[0].str.split('.').str[0]
    dataframe['month_year'] = dataframe['month']
    dataframe['year'] = dataframe['month_year'].str.split('_').str[0]
    dataframe['month'] = dataframe['month_year'].str.split('_').str[1]
    dataframe = dataframe.drop('path', axis=1)
    df_pandas = dataframe.compute()
    df_pandas['month_year'] = pd.to_datetime(
        df_pandas.month_year, format='%Y_%m')
    df_pandas['month'] = pd.to_datetime(df_pandas.month, format='%m').dt.month
    return df_pandas


def dask_load_csv():
    df_dask = dd.read_csv(cluster_order_path,
                          include_path_column=True)

    return prepare_dataframe(df_dask)


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


def egos_list_consecutive_months(dataframe, ratio, consecutive_months, val_brute):
    all_egos = dataframe.egos.unique()
    filtered_egos = np.array([])
    for ego in all_egos:
        count_clust = 0
        filter = dataframe[(dataframe.egos == ego) & (
            dataframe.ratio_over_second >= ratio) & (dataframe.nb_posts >= val_brute)]
        ego_clusters = filter.first_cluster.unique()
        for cluster in ego_clusters:
            filter2 = filter[(filter.first_cluster == cluster)
                             ].sort_values('month_year')
            filter2['monthdiff'] = filter.groupby(
                'first_cluster').month.diff().fillna(1).astype(int)
            if(is_cons_month(filter2.monthdiff.to_list(), consecutive_months)):
                count_clust += 1
            if count_clust >= 2:
                filtered_egos = np.append(filtered_egos, ego)
                break
    return filtered_egos


if __name__ == "__main__":
    dataframe = dask_load_csv()
    egos_arr = egos_list_consecutive_months(dataframe, 2, 6, 10)
    np.savetxt(
        '/home/data/algopol/algopolapp/results/Imera/Cluster_order/Egos/results.txt', egos_arr, fmt='%s')
