import argparse
from pathlib import Path
import csv
from datetime import *
from typing import List, Any
import os
from statistics import mean


class IO:

    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser()
        self.group = self.parser.add_mutually_exclusive_group(required=True)
        self.group.add_argument("-f", '--file', dest="file", metavar="FILE")
        self.group.add_argument('-d', '--directory', action="store")
        self.parser.add_argument('-o', '--output', required=True)
        self.parser.add_argument('-du', '--duration', required=True, type=int)
        self.parser.add_argument('-th', '--thresold', required=True, type=int)
        self.parser.add_argument('-s', '--smoothing', required=True, type=int)
        self.args = self.parser.parse_args()

    def get_input_path(self):
        if self.args.file is not None:
            return [Path(self.args.file)]
        return Path(self.args.directory).glob('*.csv')

    def get_output_path(self):
        return Path(self.args.output)

    def get_duration(self):
        return self.args.duration

    def get_thresold(self):
        return self.args.thresold

    def get_smoothing(self):
        return self.args.smoothing

    def write_results(self, results, ego_id):
        result_path = self.get_output_path() / f'{ego_id}.csv'
        file_exists = os.path.isfile(result_path)
        with open(result_path, 'a') as csvfile:
            dicowriter = csv.DictWriter(
                csvfile,
                fieldnames=['ego_id',
                            'date_begin', 'date_end', 'months',
                            'nb_total', 'total_smoothed',
                            'type',
                            'skip_months', 'threshold', 'duration', 'smoothing'],
                delimiter=',')
            if not file_exists:
                dicowriter.writeheader()  # file doesn't exist yet, write a header
            for period in results:
                period['ego_id'] = ego_id
                dicowriter.writerow(period)


class Bridge:
    def __init__(self):
        self.io = IO()

    def process_egos(self):
        for file in self.io.get_input_path():
            self.process_ego(file)

    def process_ego(self, ego):
        ego_id = ego.name.split('_')[0]
        dicoreader = csv.DictReader(ego.open('r', encoding='utf-8'))
        apa = ActivityPeriodsAnalysis(ego_id, dicoreader, self.io.get_thresold(), self.io.get_smoothing(),
                                      self.io.get_duration())
        results = apa.get_results()
        self.io.write_results(results, ego_id)


class ActivityPeriodsAnalysis:
    results: List[Any]

    def __init__(self, ego_id, ego_dico, thresold, smoothing, duration) -> None:
        self.ego_id = ego_id
        self.ego_dico = ego_dico
        self.thresold = thresold
        self.total_value = 0
        self.smoothing = smoothing
        self.duration = duration
        self.date_begin = None
        self.date_end = None
        self.months = None
        self.results = []

    def mk_int(self, s):
        s = s.strip()
        return int(s) if s else 0

    def diff_month(self, month1, month2, year1, year2):
        return ((year2 - year1) * 12) + (month2 - month1)

    def plus_one_year(self, ):
        return self.skip_first_months(12)

    def get_last_day_of_month(self, datep):
        next_month = datep.replace(day=28) + timedelta(days=4)
        last_day_of_month = next_month - timedelta(days=next_month.day)
        return datetime.strftime(last_day_of_month, '%d-%m-%Y')

    def skip_first_months(self, months):
        first_row = next(self.ego_dico)
        tmp = next(self.ego_dico)
        first_month, first_year = int(first_row['Month']), int(first_row['Year'])
        tmp_month, tmp_year = int(tmp['Month']), int(tmp['Year'])
        while self.diff_month(first_month, tmp_month, first_year, tmp_year) < months:
            tmp = next(self.ego_dico)
            tmp_month, tmp_year = int(tmp['Month']), int(tmp['Year'])
        return tmp

    def append_period(self, skip_month, field, smoothed_value):
        period = {
            'date_begin': self.date_begin, 'date_end': self.date_end,
            'months': self.months,
            'nb_total': self.total_value,
            'total_smoothed': smoothed_value,
            'type': field,
            'skip_months': skip_month,
            'threshold': self.thresold,
            'duration': self.duration,
            'smoothing': self.smoothing
        }
        self.results.append(period)

    def compute_periods(self, skip_months=12, field='approved_friends'):
        values_to_smooth = []
        try:
            row = self.skip_first_months(skip_months)
        except StopIteration:
            return

        self.months = 0
        while True:
            row_month, row_year = int(row['Month']), int(row['Year'])
            if self.months == 0:
                first_month, first_year = int(row['Month']), int(row['Year'])
                self.total_value = 0
                values_to_smooth = []
                diff = 0
            else:
                diff = self.diff_month(prev_month, row_month, prev_year, row_year)

            field_value = self.mk_int(row[field])
            if field_value >= self.thresold:
                if diff <= 1:
                    self.months += 1
                    prev_month, prev_year = row_month, row_year
                    self.total_value += field_value
                    values_to_smooth.append(field_value)
            else:
                if self.months >= self.duration:
                    self.date_begin = datetime(first_year, first_month, 1)
                    self.date_end = self.get_last_day_of_month(datetime(prev_year, prev_month, 1))
                    values_to_smooth.append(field_value)
                    smoothed_value = self.compute_smoothed_value(values_to_smooth)
                    self.append_period(skip_months, field, smoothed_value)
                self.months = 0

            try:
                row = next(self.ego_dico)
            except StopIteration:
                return

    def get_results(self):
        self.compute_periods()
        return self.results

    def compute_smoothed_value(self, unsmoothed_values):
        smooth_val = 0
        tmp = []
        if len(unsmoothed_values) < (self.smoothing * 2) + 1:
            return smooth_val
        for i in range(0, len(unsmoothed_values)):
            if (i + (self.smoothing * 2)) >= len(unsmoothed_values):
                tmp.append(sum(unsmoothed_values[i:(i + (self.smoothing * 2))]))
        print(tmp)
        return mean(tmp)


if __name__ == "__main__":
    bridge = Bridge()
    bridge.process_egos()
