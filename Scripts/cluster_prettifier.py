import json
import gzip
import argparse
import os
import csv
from datetime import datetime
from collections import OrderedDict
from colorama import Fore, Back, Style
import sys


class cluster_prettifier:

    def __init__(self, id_ego, cluster_nb1, cluster_nb2):
        self.id_ego = id_ego
        self.cluster_nb1 = cluster_nb1
        self.cluster_nb2 = cluster_nb2

    def get_jsons(self):
        path = '../sample_json/' + self.id_ego + '/statuses.jsons.gz'
        file = gzip.open(path, 'rt', encoding='utf-8')
        return [json.loads(line) for line in file]

    def get_csv(self):
        path = '../sample_data_sorted/' + self.id_ego[0] + '/'
        files = [os.path.join(path, i) for i in os.listdir(path) if os.path.isfile(
            os.path.join(path, i)) and i.startswith(self.id_ego)]
        file = gzip.open(files[0], 'rt')
        return csv.DictReader(file)

    def prettify_json(self, jsonf):
        dict_auth_clust = self.get_author_cluster_dict()
        ego_color = ''
        c1_color = Fore.RED
        c2_color = Fore.LIGHTBLUE_EX
        other_color = Fore.LIGHTBLACK_EX
        color = ''
        created_timestamp = int(jsonf["created"])
        created_date = str(datetime.fromtimestamp(
            created_timestamp).strftime('%d-%B-%Y %H:%M:%S'))
        updated_timestamp = int(jsonf["updated"])
        updated_date = str(datetime.fromtimestamp(
            updated_timestamp).strftime('%d-%B-%Y %H:%M:%S'))
        guessed_type = jsonf["guessed_type"]
        efrom = jsonf["from"]
        eid = jsonf["id"]
        if(dict_auth_clust[efrom] == self.cluster_nb1):
            color = c1_color
        elif(dict_auth_clust[efrom] == self.cluster_nb2):
            color = c2_color
        elif(dict_auth_clust[efrom] != 'ego'):
            color = other_color
        print(f"\tcreated: {color}{created_date}")
        if created_timestamp != updated_timestamp:
            print(f"\tupdated: {color}{updated_date}")
        print(f"\tguessed_type: {color}{guessed_type}")
        print(f"\tfrom: {color}{efrom}")
        print(f"\tid: {color}{eid}")
        if "keywords" in jsonf.keys():
            keys = ''
            for key in jsonf['keywords'].keys():
                keys += ', ' + key
            print(f"\tkeywords: {color}{keys[1:len(keys)]}")
        if "link" in jsonf.keys():
            link_site = jsonf["link"]['site']
            print(f"\tlink.site: {color}{link_site}")
        if "tags" in jsonf.keys():
            tags = ''
            for tag in jsonf['tags']:
                if(tag in dict_auth_clust.keys() and dict_auth_clust[tag] == self.cluster_nb1):
                    color = c1_color
                elif(tag in dict_auth_clust.keys() and dict_auth_clust[tag] == self.cluster_nb2):
                    color = c2_color
                elif(tag not in dict_auth_clust.keys() or tag != self.id_ego):
                    color = other_color
                tags += f', {color}{tag}'
            print(f"\ttags: {color}{tags[1:len(tags)]}")
        if "comments" in jsonf.keys():
            print(f"\tcomments:")
            for comment in jsonf['comments']:
                print('\t\t' + ('-'*10))
                cfrom = comment["from"]
                time = int(comment["time"])
                comment_time = str(datetime.fromtimestamp(
                    created_timestamp).strftime('%d-%B-%Y %H:%M:%S'))
                if(dict_auth_clust[cfrom] == self.cluster_nb1):
                    color = c1_color
                elif(dict_auth_clust[cfrom] == self.cluster_nb2):
                    color = c2_color
                elif(dict_auth_clust[cfrom] != 'ego'):
                    color = other_color
                else:
                    color = ''
                print(f"\t\ttime: {color}{comment_time}")
                print(f"\t\tfrom: {color}{cfrom}")
                if "keywords" in jsonf.keys():
                    keys = ''
                    for key in jsonf['keywords'].keys():
                        keys += ', ' + key
                    print(f"\t\tkeywords: {color}{keys[1:len(keys)]}")
            print('\t\t' + ('-'*10))
        if "likes" in jsonf.keys():
            likes = ''
            for like in jsonf['likes']:
                if(like in dict_auth_clust.keys() and dict_auth_clust[like] == self.cluster_nb1):
                    color = c1_color
                elif(like in dict_auth_clust.keys() and dict_auth_clust[like] == self.cluster_nb2):
                    color = c2_color
                elif(like not in dict_auth_clust.keys() or like != self.id_ego):
                    color = other_color
                likes += f', {color}{like}'
            print(f"\tlikes: {color}{likes[1:len(likes)]}")

    def get_author_cluster_dict(self):
        auth_clust_dict = dict()
        csv_dict = self.get_csv()
        for line in csv_dict:
            auth_clust_dict[line['author']] = line['cluster']
        return auth_clust_dict

    def prettify(self):
        json_list = self.get_jsons()
        auth_clu_dict = self.get_author_cluster_dict()
        pretty_jsons = []
        for jsonf in json_list:
            print("_"*40)
            pretty_json = self.prettify_json(jsonf)
            pretty_jsons.append(json.dumps(pretty_json,  indent=4))
        print("_"*40)
        return pretty_jsons


def get_arg_parser():
    parser = argparse.ArgumentParser()
    parser._actions.pop()
    parser.add_argument("-e", '--ego', action='store', required=False)
    parser.add_argument('-c1', '--cluster1', action="store", required=False)
    parser.add_argument('-c2', '--cluster2', action='store', required=False)
    return parser.parse_known_args()


if __name__ == "__main__":
    args, unknown = get_arg_parser()
    if args.ego is not None and args.cluster1 is not None and args.cluster2 is not None:
        pretty = cluster_prettifier(args.ego, args.cluster1, args.cluster2)
    elif len(sys.argv) == 4:
        pretty = cluster_prettifier(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print('Not Enough Arguments')
        exit(0)
    json_list = pretty.prettify()
    for x in json_list:
        print(x.encode('utf-8').decode('unicode_escape'))
