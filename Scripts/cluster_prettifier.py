import json
import gzip
import argparse
import os
import csv
from datetime import datetime
from collections import OrderedDict
from colorama import Fore, Back, Style, init
import sys


class cluster_prettifier:

    def __init__(self, id_ego, cluster_nb1, cluster_nb2):
        self.id_ego = id_ego
        self.cluster_nb1 = cluster_nb1
        self.cluster_nb2 = cluster_nb2

    def get_jsons(self):
        path = '/home/data/algopol/algopolapp/dataset03/' + \
            self.id_ego + '/statuses.jsons.gz'
        file = gzip.open(path, 'rt', encoding='utf-8')
        return [json.loads(line) for line in file]

    def get_csv(self):
        path = '/home/data/algopol/user/nabil/Alter-cluster-timestamp-sorted/' + \
            self.id_ego[0] + '/'
        files = [os.path.join(path, i) for i in os.listdir(path) if os.path.isfile(
            os.path.join(path, i)) and i.startswith(self.id_ego)]
        file = gzip.open(files[0], 'rt')
        return csv.DictReader(file)

    def get_color(self, dico, key):
        c1_color = Fore.RED
        c2_color = Fore.LIGHTBLUE_EX
        other_color = Fore.LIGHTBLACK_EX
        color = ''
        if(key in dico.keys() and dico[key] == self.cluster_nb1):
            color = c1_color
        elif(key in dico.keys() and dico[key] == self.cluster_nb2):
            color = c2_color
        elif(key not in dico.keys() or key != self.id_ego):
            color = other_color
        return color

    def process_comments(self, jsonf, dico):
        print(f"\tcomments:")
        for comment in jsonf['comments']:
            print('\t\t' + ('-'*10))
            cfrom = comment["from"]
            time = int(comment["time"])
            comment_time = str(datetime.fromtimestamp(
                time).strftime('%d-%B-%Y %H:%M:%S'))
            color = self.get_color(dico, cfrom)
            print(f"\t\ttime: {color}{comment_time}")
            print(f"\t\tfrom: {color}{cfrom}")
            if "keywords" in jsonf.keys():
                keys = ''
                for key in jsonf['keywords'].keys():
                    keys += ', ' + key
                print(f"\t\tkeywords: {color}{keys[1:len(keys)]}")

    def process_likes(self, jsonf, dico):
        likes = ''
        for like in jsonf['likes']:
            color = self.get_color(dico, like)
            likes += f', {color}{like}'
        print(f"\tlikes: {color}{likes[1:len(likes)]}")

    def process_tags(self, jsonf, dico):
        tags = ''
        for tag in jsonf['tags']:
            color = self.get_color(dico, tag)
            tags += f', {color}{tag}'
        print(f"\ttags: {color}{tags[1:len(tags)]}")

    def process_keywords(self, jsonf, color):
        keys = ''
        for key in jsonf['keywords'].keys():
            keys += ', ' + key
        print(f"\tkeywords: {color}{keys[1:len(keys)]}")

    def process_from(self, jsonf, efrom, color):
        if jsonf[efrom] == self.id_ego:
            print(f"\tfrom: {color}{ego}")
        else:
            print(f"\tfrom: {color}{efrom}")

    def prettify_json(self, jsonf, dict_auth_clust):
        created_timestamp = int(jsonf["created"])
        created_date = str(datetime.fromtimestamp(
            created_timestamp).strftime('%d-%B-%Y %H:%M:%S'))
        updated_timestamp = int(jsonf["updated"])
        updated_date = str(datetime.fromtimestamp(
            updated_timestamp).strftime('%d-%B-%Y %H:%M:%S'))
        guessed_type = jsonf["guessed_type"]
        efrom = jsonf["from"]
        eid = jsonf["id"]
        color = self.get_color(dict_auth_clust, efrom)
        print(f"\tcreated: {color}{created_date}")
        if created_timestamp != updated_timestamp:
            print(f"\tupdated: {color}{updated_date}")
        print(f"\tguessed_type: {color}{guessed_type}")

        print(f"\tid: {color}{eid}")
        if "keywords" in jsonf:
            self.process_keywords(jsonf, color)
        if "link" in jsonf.keys():
            link_site = jsonf["link"]['site']
            print(f"\tlink.site: {color}{link_site}")
        if "tags" in jsonf:
            self.process_tags(jsonf, dict_auth_clust)
        if "comments" in jsonf:
            self.process_comments(jsonf, dict_auth_clust)
            print('\t\t' + ('-'*10))
        if "likes" in jsonf:
            self.process_likes(jsonf, dict_auth_clust)

    def get_author_cluster_dict(self):
        auth_clust_dict = dict()
        csv_dict = self.get_csv()
        for line in csv_dict:
            auth_clust_dict[line['author']] = line['cluster']
        return auth_clust_dict

    '''def prettify(self):
        json_list = self.get_jsons()
        auth_clu_dict = self.get_author_cluster_dict()
        pretty_jsons = []
        for jsonf in json_list:
            print("_"*40)
            pretty_json = self.prettify_json(jsonf, auth_clu_dict)
        print("_"*40)
        return pretty_jsons'''

    def prettify(self):
        path = '/home/data/algopol/algopolapp/dataset03/' + \
            self.id_ego + '/statuses.jsons.gz'
        file = gzip.open(path, 'rt', encoding='utf-8')
        auth_clu_dict = self.get_author_cluster_dict()
        for line in file:
            print("_"*40)
            self.prettify_json(json.loads(line), auth_clu_dict)
        print("_"*40)


def get_arg_parser():
    parser = argparse.ArgumentParser()
    parser._actions.pop()
    parser.add_argument("-e", '--ego', action='store', required=False)
    parser.add_argument('-c1', '--cluster1',
                        action="store", required=False)
    parser.add_argument('-c2', '--cluster2',
                        action='store', required=False)
    return parser.parse_known_args()


if __name__ == "__main__":
    args, unknown = get_arg_parser()
    init(autoreset=True, strip=False)
    if args.ego is not None and args.cluster1 is not None and args.cluster2 is not None:
        pretty = cluster_prettifier(args.ego, args.cluster1, args.cluster2)
    elif len(sys.argv) == 4:
        pretty = cluster_prettifier(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print('Not Enough Arguments')
        exit(0)
    try:
        pretty.prettify()
    except IOError:
        try:
            sys.stdout.close()
        except IOError:
            pass
        try:
            sys.stderr.close()
        except IOError:
            pass
