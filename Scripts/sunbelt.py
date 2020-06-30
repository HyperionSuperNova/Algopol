import dask.dataframe as dd
import pandas as pd
import numpy as np

cluster_order_path = '../../Sunbelt/Cluster_order/CSV/*'

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


def egos_list_consecutive_months(dataframe, ratio, consecutive_months):
    all_egos = dataframe.egos.unique()
    filtered_egos = np.array([])
    for ego in all_egos:
        filter = dataframe[(
            dataframe.egos == ego) & (dataframe.ratio_over_second >= ratio)].sort_values('month_year')
        if filter['month'].diff().cumsum().max() >= consecutive_months:
            filtered_egos = np.append(filtered_egos, ego)
    print(filtered_egos)
    print(len(filtered_egos))


if __name__ == "__main__":
    dataframe = dask_load_csv()
    egos_list_consecutive_months(dataframe, 2, 6)
