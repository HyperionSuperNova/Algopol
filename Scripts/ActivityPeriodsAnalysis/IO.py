import argparse
from pathlib import Path
import os
import csv


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
                            'nb_total',
                            'type',
                            'skip_months', 'threshold', 'duration', 'smoothing'],
                delimiter=',')
            if not file_exists:
                dicowriter.writeheader()  # file doesn't exist yet, write a header
            for period in results:
                period['ego_id'] = ego_id
                dicowriter.writerow(period)
