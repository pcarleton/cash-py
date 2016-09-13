import pandas as pd
import unittest
import datetime

from cashcoach.spending import transactions


def _make_transactions(trans_tupes):
    rows = []
    for date_str, amount in trans_tupes:
        rows.append({'date': date_str, 'adjusted': amount})

    df = pd.DataFrame(rows)
    df['date'] = pd.to_datetime(df.date)

    return df


class TestTargets(unittest.TestCase):

    def test_weekly(self):
        trans = [
            ('8/2/2016', 10),
            ('8/8/2016', 10),
            ('8/9/2016', 10)
        ]

        dateinfo = transactions.DateInfo(datetime.date(2016, 8, 10))
        flex = 310
        df = _make_transactions(trans)

        target = transactions._get_week_target(df, flex, dateinfo)

        self.assertEqual(70, target.goal)
        self.assertEqual(20, target.spent)
        self.assertEqual(50, target.left)
        self.assertEqual(0, target.over)

    def test_adjusted(self):
        trans = [
            ('8/2/2016', 112.5),
            ('8/8/2016', 112.5),
            ('8/15/2016', 10)
        ]

        dateinfo = transactions.DateInfo(datetime.date(2016, 8, 18))
        flex = 310
        df = _make_transactions(trans)

        target = transactions._get_adjusted_targets(df, flex, dateinfo)

        self.assertEqual(35, target.goal)
        self.assertEqual(10, target.spent)
        self.assertEqual(25, target.left)
        self.assertEqual(0, target.over)

    def test_last_week(self):
        trans = [
            ('8/2/2016', 105),
            ('8/8/2016', 105),
            ('8/15/2016', 10)
        ]

        dateinfo = transactions.DateInfo(datetime.date(2016, 8, 18))
        flex = 310
        df = _make_transactions(trans)

        target = transactions._get_last_week(df, flex, dateinfo)

        self.assertEqual(56, target.goal)
        self.assertEqual(105, target.spent)
        self.assertEqual(0, target.left)
        self.assertEqual(49, target.over)

    def test_last_month(self):
        trans = [
            ('8/2/2016', 105),
            ('8/8/2016', 105),
            ('8/15/2016', 10)
        ]

        dateinfo = transactions.DateInfo(datetime.date(2016, 9, 5))
        flex = 310
        df = _make_transactions(trans)
        target = transactions._get_last_month(df, flex, dateinfo)

        self.assertEqual(310, target.goal)
        self.assertEqual(220, target.spent)
        self.assertEqual(90, target.left)
        self.assertEqual(0, target.over)

    def test_summary(self):
        expected = ["Wk 1 (4d): $30.00 / 40.00 (+10.00)",
                    "Wk 2 (7d): $80.00 / 72.69 (-7.31)",
                    "Total (11d): $110.00 / 110.00 (+0.00)"]

        trans = [
            ('9/2/2016', 30),
            ('9/6/2016', 80),
        ]
        dateinfo = transactions.DateInfo(datetime.date(2016, 9, 12))
        flex = 300

        df = _make_transactions(trans)

        lines = transactions.summary_data(dateinfo, df, flex)

        self.assertEqual(expected, lines)


class TestDateInfo(unittest.TestCase):

    def test_month_days(self):
        date = datetime.date(2016, 9, 12)
        dateinfo = transactions.DateInfo(date)

        self.assertEqual(11, dateinfo.days_before_this_week)
        self.assertEqual(19, dateinfo.days_after_week_start)