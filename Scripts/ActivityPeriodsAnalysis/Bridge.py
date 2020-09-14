from IO import *
from activity_periods_analysis import *


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
