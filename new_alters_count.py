#!/usr/bin/env python3
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import gzip
import csv
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import seaborn as sns
import os
import argparse
sns.set()


def dict_to_csvdict(dico):
    return [{'Month': k[0], 'Year':k[1], 'AlterCount':v} for k, v in dico.items()]


def write_to_csv(id_ego, dico, output_path):
    csv_file = os.path.join(output_path, id_ego + '_alter-count.csv')
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
    return os.path.splitext(os.path.basename(ego_path))[0][:8]


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


def generate_plot_from_dict(id_ego, dico, output_path):
    dico = dict_to_csvdict(dico)
    dico_df = pd.DataFrame.from_records(dico)
    dico_df['date'] = dico_df['Month'].map(
        str) + '-' + dico_df['Year'].map(str)
    dico_df['date'] = pd.to_datetime(dico_df['date'])
    fig, ax = plt.subplots(figsize=(12, 12))
    date_form = DateFormatter("%m-%Y")
    ax.plot('date',
            'AlterCount',
            color='purple', data=dico_df)
    ax.set(xlabel="Date",
           ylabel="AlterCount")
    ax.xaxis.set_major_formatter(date_form)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax.format_xdata = mdates.DateFormatter('%m-%Y')
    plt.savefig(os.path.join(output_path, id_ego+'.png'))


def get_args_parser():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", '--file', dest="file", metavar="FILE")
    group.add_argument('-d', '--directory', action="store")
    parser.add_argument('-o', '--output', required=True)

    return parser.parse_args()


def execution(filename, output_path):
    filegz = gzip.open(filename, 'rt')
    csvobj = csv.DictReader(filegz)
    id_ego = get_ego_id(filename)
    dico_by_month = new_alters_by_month(id_ego, csvobj)
    write_to_csv(id_ego, dico_by_month, output_path)
    generate_plot_from_dict(id_ego, dico_by_month, output_path)
    filegz.close()


if __name__ == "__main__":
    args = get_args_parser()
    if args.file is not None:
        file_path = Path(args.file)
        output_path = Path(args.output)
        execution(file_path, output_path)
    elif args.directory is not None:
        directory_path = os.fsencode(args.directory)
        output_path = Path(args.output)
        for file in os.listdir(directory_path):
            filename = os.fsdecode(file)
            if filename.endswith(".csv.gz"):
                execution(os.path.join(args.directory, filename), output_path)
                continue
            else:
                continue
