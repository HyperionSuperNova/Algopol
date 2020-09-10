class Qualify:

    def __init__(self, qualify_json, closeness, since):
        self.qualify_json = qualify_json
        self.closeness = closeness
        self.since = since
        self.alters_set = set()

    def process_file(self):
        jsoon = json.load(self.qualify_json)
        for friends in jsoon['friends']:
            if friends['data']['close'] == self.closeness and friends['data']['since'] == self.since:
                self.alters_set.add(friends['user_id'])

    def get_alters_set(self):
        return self.alters_set