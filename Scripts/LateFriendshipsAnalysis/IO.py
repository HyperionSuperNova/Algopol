import argparse
from pathlib import Path
import json
import gzip
import re

from Scripts.LateFriendshipsAnalysis.Friends import Friends
from Scripts.LateFriendshipsAnalysis.Qualify import Qualify


class IO:

    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-i', '--input', required=True)
        self.parser.add_argument('-o', '--output', required=True)
        self.parser.add_argument('-cl', '--close', required=True, type=int)
        self.parser.add_argument('-si', '--since', required=True, type=int)
        self.args = self.parser.parse_args()

    def get_qualify_path(self):
        return Path(self.args.input) / 'qualify.json.gz'

    def get_friends_path(self):
        return Path(self.args.input) / 'friends.jsons.gz'

    def get_statuses_path(self):
        return Path(self.args.input) / 'statuses.jsons.gz'

    def get_output_path(self):
        return Path(self.args.output)

    def get_closeness(self):
        return self.args.close

    def get_since(self):
        return self.args.since

    def get_ego_id(self):
        return Path(self.args.input).name[0:8]


if __name__ == '__main__':
    ioyo = IO()
    qualify_set = {}
    try:
        with gzip.open(ioyo.get_qualify_path(), 'rt', encoding='utf-8') as qualify_json:
            quali = Qualify(qualify_json, ioyo.get_closeness(), ioyo.get_since())
            quali.process_file()
            qualify_set = quali.get_alters_set()

    except FileNotFoundError as fnfr:
        print(f'{ioyo.get_ego_id()} doesn\'t have a qualify file')

    '''with gzip.open(ioyo.get_friends_path(), 'rt', encoding='utf-8') as friends_json:
        friends = Friends(friends_json, qualify_set)
        print(friends.generate_json())'''
