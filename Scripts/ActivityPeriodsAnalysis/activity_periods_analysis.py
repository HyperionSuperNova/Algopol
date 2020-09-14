from datetime import *
from typing import List, Any
from Bridge import *

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

    def append_period(self, skip_month, field):
        period = {
            'date_begin': self.date_begin, 'date_end': self.date_end,
            'months': self.months,
            'nb_total': self.total_value,
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
                diff = 0
            else:
                diff = self.diff_month(prev_month, row_month, prev_year, row_year)

            field_value = self.mk_int(row[field])
            if field_value >= self.thresold:
                if diff <= 1:
                    self.months += 1
                    prev_month, prev_year = row_month, row_year
                    self.total_value += field_value
            else:
                if self.months >= self.duration:
                    self.date_begin = datetime(first_year, first_month, 1)
                    self.date_end = self.get_last_day_of_month(datetime(prev_year, prev_month, 1))
                    self.append_period(skip_months, field)
                self.months = 0

            try:
                row = next(self.ego_dico)
            except StopIteration:
                return

    def get_results(self):
        self.compute_periods()
        return self.results


if __name__ == "__main__":
    bridge = Bridge()
    bridge.process_egos()
