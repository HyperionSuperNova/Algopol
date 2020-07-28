import csv
import os
from pathlib import Path
from datetime import *

csv_path = Path('../Alter-count-csv-plots/')
output_path = Path('../output/')


def diff_month(month1, month2, year1, year2):
    return ((year2 - year1) * 12) + (month2 - month1)


def skip_first_months(dicoreader, months):
    first_row = next(dicoreader)
    tmp = next(dicoreader)
    first_month, first_year = int(first_row['Month']), int(first_row['Year'])
    tmp_month, tmp_year = int(tmp['Month']), int(tmp['Year'])
    while diff_month(first_month, tmp_month, first_year, tmp_year) <= months:
        tmp = next(dicoreader)
        tmp_month, tmp_year = int(tmp['Month']), int(tmp['Year'])
    return tmp

def plus_one_year(dicoreader):
    return skip_first_months(dicoreader, 12)


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
        fieldnames=['ego_id',
            'date_begin', 'date_end', 'months', 'nb_total',
            'type',
            'skip_months', 'threshold', 'duration', 'smoothing'],
        delimiter=',')
    dicowriter.writeheader()
    return dicowriter, csvf

def compute_periods(dicoreader,
                    threshold, duration, smoothing,
                    skip_months = 12, field = 'approved_friends'):
    res = []
    row = skip_first_months(dicoreader, skip_months)
    months = 0
    while True:
        row_month, row_year = int(row['Month']), int(row['Year'])
        if months == 0:
            first_month, first_year = int(row['Month']), int(row['Year'])
            total_value = 0
            diff = 0
        else:
            diff = diff_month(prev_month, row_month, prev_year, row_year)

        field_value = mk_int(row[field])
        if field_value >= threshold:
            if diff <= 1:
                months += 1
                prev_month, prev_year = row_month, row_year
                total_value += field_value
        else:
            if months >= duration:
#                delta_month = diff_month(first_month, prev_month,
#                                         first_year, prev_year)
                date_begin = datetime(first_year, first_month, 1)
                date_end = datetime(prev_year, prev_month, 1)
                date_end = get_last_day_of_month(date_end)
                period = {
                    'date_begin': date_begin, 'date_end': date_end,
                    'months': months,
                    'nb_total': total_value,
                    'type': field,
                    'skip_months': skip_months,
                    'threshold': threshold,
                    'duration': duration,
                    'smoothing': smoothing
                }
                res.append(period)

            months = 0

        try:
            row = next(dicoreader)
        except StopIteration:
            return res


def write_periods(writer, periods, ego_id):
    for period in periods:
        period['ego_id'] = ego_id
        writer.writerow(period)


def process_ego(ego_path, duration, thresold, smoothing):
    ego_id = ego_path.name.split('_')[0]
    dicowriter, file = get_csvwriter(ego_id)
    dicoreader = csv.DictReader(ego_path.open('r', encoding='utf-8'))
    periods = compute_periods(dicoreader,
                              duration, thresold, smoothing)
    write_periods(dicowriter, periods, ego_id)

    file.close()


def process_egos(filespath, thresold, smoothing, duration):
    for file in filespath:
        process_ego(file, thresold, smoothing, duration)


def process_files():
    files_path = csv_path.glob('*/csv/*.csv')
    return files_path


if __name__ == '__main__':
    files_path = process_files()
    process_egos(files_path, 2, 2, 2)
