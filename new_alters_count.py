import matplotlib.pyplot as plt
import gzip
import csv
from datetime import datetime, timedelta
import pandas as pd
import seaborn as sns
import os
sns.set()


def dict_to_csvdict(dico):
    return [{'Month': k[0], 'Year':k[1], 'AlterCount':v} for k, v in dico.items()]


def write_to_csv(id_ego, dico):
    csv_file = id_ego + '_alter-count.csv'
    csv_columns = ['Month', 'Year', 'AlterCount']
    dict_data = dict_to_csvdict(dico)
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
    except IOError:
        print("I/O error")


def add_value_to_dict(dico, key, val):
    if key in dico.keys():
        dico[key] = dico[key] + val
    else:
        dico[key] = val


def get_ego_id(ego_path):
    return os.path.splitext(ego_path)[0].split('/')[1][:8]


def next_year(timestamp):
    return timestamp + 365*24*3600


def next_month(timestamp):
    return timestamp + 30*24*3600


def step_months_if_needed(before, now, old_alters, by_month):
    pass


def new_alters_by_month(ego, csvobj):
    header = next(csvobj)
    first_row = next(csvobj)
    before = int(first_row['timestamp'])
    nb_new = 0
    by_month = {}
    alters = {}
    old_alters = {}
    for row in csvobj:
        idr, timestamp = row['author'], int(row['timestamp'])
        if idr not in alters and idr != ego:
            alters[idr] = timestamp
            nb_new += 1
            dt = datetime.fromtimestamp(timestamp)
            month_year = (dt.month, dt.year)
            month_next_year = (dt.month, dt.year + 1)
            add_value_to_dict(old_alters, month_next_year, 1)

            # step months if needed
            while before < timestamp:
                dt = datetime.fromtimestamp(before)
                month_year = (dt.month, dt.year)
                if month_year in old_alters:
                    nb_new -= old_alters[month_year]
                by_month[month_year] = nb_new
                before = next_month(before)
    return by_month


if __name__ == "__main__":
    file_path = 'sample_data/0a1efab4976c1c7487da95d444e553fe.csv.gz'
    filegz = gzip.open(file_path, 'rt')
    csvobj = csv.DictReader(filegz)
    id_ego = get_ego_id(file_path)
    dico_by_month = new_alters_by_month(id_ego, csvobj)
    write_to_csv(id_ego, dico_by_month)
