#!/usr/bin/env python3
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import gzip
import csv
from datetime import datetime, timedelta, date
from pathlib import Path
import pandas as pd
import seaborn as sns
import os
import argparse
import logging
import json
from dateutil.relativedelta import *

sns.set()

json_path = '/home/data/algopol/algopolapp/dataset03/'
#json_path = '../sample_json/'


def dict_to_csvdict(dico_csv, dico_json):
    if len(dico_json) == 0:
        return [{'Month': k[0], 'Year':k[1], 'recent_active':dico_csv[k], 'recent_friends':'', 'approved_friends':''} for k in dico_csv]
    L = []
    for k in dico_csv:
        if k in dico_json:
            L.append({'Month': k[0], 'Year': k[1], 'recent_active': dico_csv[k],
                      'recent_friends': dico_json[k][0], 'approved_friends': dico_json[k][1]})
        else:
            L.append({'Month': k[0], 'Year': k[1], 'recent_active': dico_csv[k],
                      'recent_friends': '', 'approved_friends': ''})
    return L


def write_to_csv(id_ego, dicocsv, dicojson, output_path):
    final_path = os.path.join(output_path, 'csv')
    if not os.path.exists(final_path):
        os.makedirs(final_path)
    csv_file = os.path.join(final_path, id_ego + '_alter-count.csv')
    csv_columns = ['Month', 'Year', 'recent_active',
                   'recent_friends', 'approved_friends']
    dict_data = dict_to_csvdict(dicocsv, dicojson)
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


def get_first_approval(jsons):
    first_json = jsons.pop()
    while(first_json['guessed_type'] != 'EapprouveAmi'):
        first_json = jsons.pop(0)
    return first_json


def get_jsons_as_list(id_ego):
    path = json_path + id_ego + '/statuses.jsons.gz'
    file = gzip.open(path, 'rt', encoding='utf-8')
    return [json.loads(line) for line in file]


def approved_friend_per_month(id_ego):
    jsons = get_jsons_as_list(id_ego)
    if len(jsons) == 0:
        return {}
    first_json = get_first_approval(jsons)
    nb_new = 0
    nb_new_per_month = 0
    by_month = {}
    alters = {}
    old_alters = {}
    dt_before = last_day_of_month(
        datetime.fromtimestamp(int(first_json['created'])))
    for alter in first_json['tags']:
        if alter not in alters and alter != id_ego:
            nb_new += 1
            add_value_to_dict(
                old_alters, (dt_before.month, dt_before.year + 1), 1)

    for jsonf in jsons:
        timestamp = int(jsonf['created'])
        if 'guessed_type' in jsonf:
            if(jsonf['guessed_type'] == 'EapprouveAmi'):
                dt_timestamp = datetime.fromtimestamp(timestamp)
                month_next_year = (dt_timestamp.month, dt_timestamp.year + 1)
                dt_last_of_next_month = last_day_of_month(dt_timestamp)
                month_year = (dt_timestamp.month, dt_timestamp.year)
                if 'tags' in jsonf:
                    for alter in jsonf['tags']:
                        if alter not in alters and alter != id_ego:
                            add_value_to_dict(old_alters, month_next_year, 1)
                            nb_new_per_month += 1
                    if int((dt_last_of_next_month - dt_before).days) >= 28:
                        while dt_before < dt_timestamp:
                            month_year = (dt_before.month, dt_before.year)
                            if month_year in old_alters:
                                nb_new -= old_alters[month_year]
                            by_month[month_year] = (nb_new, nb_new_per_month)
                            dt_before = dt_before + relativedelta(months=+1)
                            nb_new_per_month = 0
                    nb_new += 1
    return by_month


def get_ego_id(ego_path):
    return os.path.splitext(os.path.basename(ego_path))[0][:8]


def next_year(timestamp):
    return timestamp + 365*24*3600


def next_month(timestamp):
    return timestamp + 30*24*3600


def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)


def new_alters_by_month_bis(ego, csvobj):
    nb_new = 0
    by_month = {}
    alters = {}
    old_alters = {}
    first_row = next(csvobj)
    dt_before = last_day_of_month(
        datetime.fromtimestamp(int(first_row['timestamp'])))
    # l'id présent sur la première ligne n'est pas nécéssairement un égo il faut donc le vérifier
    if first_row['author'] != ego:
        nb_new += 1
        alters[first_row['author']] = first_row['timestamp']
        add_value_to_dict(old_alters, (dt_before.month, dt_before.year + 1), 1)
    for row in csvobj:
        idr, timestamp = row['author'], int(row['timestamp'])
        if idr not in alters and idr != ego:
            alters[idr] = timestamp
            dt_timestamp = datetime.fromtimestamp(timestamp)
            month_next_year = (dt_timestamp.month, dt_timestamp.year + 1)
            dt_last_of_next_month = last_day_of_month(dt_timestamp)
            month_year = (dt_timestamp.month, dt_timestamp.year)
            add_value_to_dict(old_alters, month_next_year, 1)
            # step months if needed
            if int((dt_last_of_next_month - dt_before).days) >= 28:
                while dt_before < dt_timestamp:
                    month_year = (dt_before.month, dt_before.year)
                    if month_year in old_alters:
                        nb_new -= old_alters[month_year]
                    by_month[month_year] = nb_new
                    dt_before = dt_before + relativedelta(months=+1)
            nb_new += 1

    return by_month


def generate_plot_from_dict(id_ego, dico, dico_json, output_path):
    final_path = os.path.join(output_path, 'plots')
    if not os.path.exists(final_path):
        os.makedirs(final_path)
    dico = dict_to_csvdict(dico, dico_json)
    if(len(dico) == 0):
        return
    dico_df = pd.DataFrame.from_records(dico)
    dico_df['date'] = dico_df['Month'].map(
        str) + '-' + dico_df['Year'].map(str)
    dico_df['date'] = pd.to_datetime(dico_df['date'])
    fig, ax = plt.subplots(figsize=(12, 12))
    date_form = DateFormatter("%m-%Y")
    ax.plot('date',
            'recent_active',
            color='purple', data=dico_df)
    ax.set(xlabel="Date",
           ylabel="Nombre d'Alter récents", title=id_ego)
    ax.xaxis.set_major_formatter(date_form)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax.format_xdata = mdates.DateFormatter('%m-%Y')
    plt.savefig(os.path.join(final_path, id_ego+'.png'))
    plt.cla()
    plt.close('all')


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
    log_name = 'logs/alter_count_UntreatedFile.log'
    logging.basicConfig(filename=log_name, level=logging.WARNING)
    try:
        dico_by_month = new_alters_by_month_bis(id_ego, csvobj)
        json_by_month = approved_friend_per_month(id_ego)
        write_to_csv(id_ego, dico_by_month, json_by_month, output_path)
        generate_plot_from_dict(id_ego, dico_by_month,
                                json_by_month, output_path)
    except Exception as excp:
        print(excp)
        logging.warning('%s', filename)
        pass
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
