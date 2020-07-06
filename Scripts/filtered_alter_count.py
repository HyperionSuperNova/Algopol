import csv
import os
#alter_count_path = '../Alter-count-csv-plots/'
#ego_date_cluster_path = '../output/sunbelt/filtered_egos_month_year_cluster.csv'
#output_csv_path = '../output/sunbelt/filtered_egos_month_year_cluster_alter_count.csv'
alter_count_path = '/home/data/algopol/user/nabil/Alter-count-csv-plots/'
ego_date_cluster_path = '/home/data/algopol/user/nabil/Sunbelt/filtered_egos_month_year_cluster.csv'
output_csv_path = '/home/data/algopol/user/nabil/Sunbelt/filtered_egos_month_year_cluster_altercount.csv'


def filtered_file(ego_date_cluster_dico):
    alter_count_filtered_list = dict()
    for row in ego_date_cluster_dico:
        first_char = row['ego'][0]
        alter_count_path_sub = alter_count_path + first_char + '/csv'
        for file in os.listdir(alter_count_path_sub):
            if file.startswith(row['ego']):
                alter_count_dico = csv.DictReader(
                    open(os.path.join(alter_count_path_sub, file)))
                alter_count_dico2 = csv.DictReader(
                    open(os.path.join(alter_count_path_sub, file)))
                alter_count_filtered_list[row['ego']] = (
                    alter_count_dico, alter_count_dico2)
    return alter_count_filtered_list


def join_files(csv1, csv_dico):
    result = []
    ego_id = -1
    for row in csv1:
        cmp = 0
        if ego_id == row['ego']:
            cmp = 1
        else:
            cmp = 0
        ego_id = row['ego']
        try:
            for row2 in csv_dico[row['ego']][cmp]:
                if row['month'] == row2['Month'] and row['year'] == row2['Year']:
                    result.append({'ego': row['ego'], 'cluster': row['cluster'],
                                   'month': row['month'], 'year': row['year'], 'alter_count': row2['AlterCount']})
        except KeyError as ke:
            continue

    return result


if __name__ == "__main__":
    ego_date_cluster_dico = csv.DictReader(open(ego_date_cluster_path))
    alter_count_filtered_list = filtered_file(ego_date_cluster_dico)
    ego_date_cluster_dico = csv.DictReader(open(ego_date_cluster_path))
    join_result = join_files(ego_date_cluster_dico, alter_count_filtered_list)
    with open(output_csv_path, 'a') as csvf:
        dicowriter = csv.DictWriter(
            csvf, fieldnames=['ego', 'cluster', 'month', 'year', 'alter_count'], delimiter=',')
        dicowriter.writeheader()
        for row in join_result:
            dicowriter.writerow(row)
