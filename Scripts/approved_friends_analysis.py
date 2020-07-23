import csv
import os
from pathlib import Path
from datetime import *

csv_path = Path('../Alter-count-csv-plots/')
output_path = Path('../output/')


def plus_one_year(dicoreader):
    first_row = next(dicoreader)
    tmp = next(dicoreader)
    first_month, first_year = int(first_row['Month']), int(first_row['Year'])
    tmp_month, tmp_year = int(tmp['Month']), int(tmp['Year'])
    while tmp_month != first_month and tmp_year != (first_year + 1):
        tmp = next(dicoreader)
        tmp_month, tmp_year = int(tmp['Month']), int(tmp['Year'])
    return tmp


def diff_month(month1, month2, year1, year2):
    return ((year2 - year1) * 12) + (month2 - month1)


def get_last_day_of_month(datep):
    next_month = datep.replace(day=28) + timedelta(days=4)
    last_day_of_month = next_month - timedelta(days=next_month.day)
    return datetime.strftime(last_day_of_month, '%d-%m-%Y')


def mk_int(s):
    s = s.strip()
    return int(s) if s else 0


def get_csvwriter(id_ego):
    out_path = output_path / f'{id_ego}.csv'
    csvf = out_path.open('a', encoding='utf-8')
    dicowriter = csv.DictWriter(
        csvf,
        fieldnames=['id_ego', 'date_begin', 'date_end', 'month_diff', 'nb_total', 'type', 'thresold', 'smoothing'],
        delimiter=',')
    dicowriter.writeheader()
    return dicowriter, csvf


def process_ego(ego_path, thresold, smoothing):
    id_ego = ego_path.name.split('_')[0]
    dicowriter, file = get_csvwriter(id_ego)
    dicoreader = csv.DictReader(ego_path.open('r', encoding='utf-8'))
    try:
        tmp_row = plus_one_year(dicoreader)
        first_month, first_year = int(tmp_row['Month']), int(tmp_row['Year'])
        tmp_month, tmp_year = int(tmp_row['Month']), int(tmp_row['Year'])
        count_thres = 0
        total_in_thres = 0
        for row in dicoreader:
            row_month, row_year = int(row['Month']), int(row['Year'])
            if diff_month(tmp_month, row_month, tmp_year, row_year) == 1 and mk_int(
                    row['approved_friends']) >= smoothing:
                count_thres += 1
                tmp_month, tmp_year = row_month, row_year
                total_in_thres += int(row['approved_friends'])
            else:
                if count_thres >= thresold:
                    delta_month = diff_month(first_month, tmp_month, first_year, tmp_year)
                    date_begin = get_last_day_of_month(datetime(first_year, first_month, 1))
                    date_end = get_last_day_of_month(datetime(tmp_year, tmp_month, 1))
                    dicowriter.writerow(
                        {'id_ego': id_ego, 'date_begin': date_begin, 'date_end': date_end, 'month_diff': delta_month,
                         'nb_total': total_in_thres, 'type': 'approvedfriends', 'thresold': thresold,
                         'smoothing': smoothing})
                count_thres = 0
                total_in_thres = 0
                first_month, first_year = int(row['Month']), int(row['Year'])
                tmp_month, tmp_year = int(row['Month']), int(row['Year'])
    except Exception as excp:
        print(excp)
    file.close()


def process_egos(filespath, thresold, smoothing):
    for file in filespath:
        process_ego(file, thresold, smoothing)


def process_files():
    files_path = csv_path.glob('*/csv/*.csv')
    return files_path


if __name__ == '__main__':
    files_path = process_files()
    process_egos(files_path, 2, 20)
