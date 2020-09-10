import json
import re

class Friends:
    def __init__(self, friends_json, qualify_set):
        self.qualify_set = qualify_set
        self.friends_json = friends_json

    def process_jsons(self):
        pos = 0
        decoder = json.JSONDecoder()
        NOT_WHITESPACE = re.compile(r'[^\s]')
        data = self.friends_json.read()
        while True:
            match = NOT_WHITESPACE.search(data, pos)
            if not match:
                return
            pos = match.start()

            try:
                obj, pos = decoder.raw_decode(data, pos)
            except json.JSONDecodeError:
                # do something sensible if there's some error
                raise
            yield obj