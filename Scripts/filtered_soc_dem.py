import pandas as pd

ego_date_cluster_path = '/home/data/algopol/user/nabil/Sunbelt/filtered_egos_month_year_cluster.csv'
egos_sociocat_path = '/home/data/algopol/user/nabil/egos-age-gender-profession.csv'
output_path = '/home/data/algopol/user/nabil/Sunbelt/filtered_soc_dem.csv'
#ego_date_cluster_path = '../output/sunbelt/filtered_egos_month_year_cluster.csv'
#egos_sociocat_path = '../sample_data_egos_age/egos-age-gender-profession.csv'


def get_unique_egos(dataframe):
    return pd.DataFrame(dataframe.ego.unique(), columns=['egos'])


def join_df(df1, df2):
    df_merged = df1.merge(df2, on='egos')
    df_merged['age_range'] = pd.cut(
        x=df_merged['age'], bins=[0, 18, 30, 59, 75, 100])
    return df_merged


def main_process():
    ego_dc = pd.read_csv(ego_date_cluster_path)
    unique_egos = get_unique_egos(ego_dc)
    ego_sociocat = pd.read_csv(egos_sociocat_path)
    joined_filtered_sociocat = join_df(unique_egos, ego_sociocat)
    joined_filtered_sociocat.to_csv(
        output_path, sep=',', encoding='utf-8', index=False)


if __name__ == "__main__":
    main_process()
