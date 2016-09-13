import datetime


def get_next_month(date):
    if date.month == 12:
        return datetime.date(date.year + 1, 1, 1)

    return date.replace(month=date.month + 1, day=1)


class DateInfo(object):

    def __init__(self, date=None):
        if date is None:
            date = datetime.date.today()

        self.date = date
        self.week_start = date - datetime.timedelta(days=date.weekday())
        self.next_week_start = self.week_start + datetime.timedelta(days=7)
        self.last_week_end = self.week_start - datetime.timedelta(days=1)

        self.month_start = self.week_start.replace(day=1)
        self.next_month_start = get_next_month(self.month_start)

        if self.next_week_start > self.next_month_start:
            self.week_days_next_month = (self.next_week_start - self.next_month_start).days
        else:
            self.week_days_next_month = 0
        self.week_days_this_month = 7 - self.week_days_next_month

        self.days_this_month = (self.next_month_start - self.month_start).days
        self.days_left_month = (self.next_month_start - self.week_start).days
        self.days_left_week = (self.next_week_start - self.date).days
        self.days_this_week = 7 - self.days_left_week



class Target(object):

    def __init__(self, goal, spent, transactions, start, end):
        self.goal = goal
        self.spent = spent
        self.difference = goal - spent
        self.left = max(self.difference, 0)
        self.over = abs(min(0, self.difference))
        self.transactions = transactions
        self.start = start
        self.end = end

    def __repr__(self):
        return "<Target Goal={} Spent={}>".format(self.goal, self.spent)


def _get_month_target(df, flex, dateinfo):
    this_month = df[(df.date >= dateinfo.month_start) &
                    (df.date <= dateinfo.date) &
                    (df.date < dateinfo.next_month_start)]

    spent_month = this_month.adjusted.sum()
    month_target = Target(flex, spent_month, this_month, dateinfo.month_start, dateinfo.next_month_start)

    return month_target


def _get_week_target(df, flex, dateinfo):
    daily_pace = flex / dateinfo.days_this_month

    this_week = df[(df.date >= dateinfo.week_start) &
                   (df.date < dateinfo.next_week_start)]
    spent_week = this_week.adjusted.sum()

    regular_goal = daily_pace*7
    regular_target = Target(regular_goal, spent_week, this_week, dateinfo.week_start,
                            dateinfo.next_week_start)

    return regular_target


def _get_adjusted_targets(df, flex, dateinfo):
    pre_this_week = df[(df.date >= dateinfo.month_start) &
                       (df.date < dateinfo.week_start)].adjusted.sum()

    this_week = df[(df.date >= dateinfo.week_start) &
                   (df.date < dateinfo.next_week_start)]
    this_week_this_month = this_week[(this_week.date < dateinfo.next_month_start)]

    this_week_month_spent = this_week_this_month.adjusted.sum()

    left_this_month = flex - pre_this_week
    adjusted_pace = left_this_month / dateinfo.days_left_month
    adjusted_goal = adjusted_pace*dateinfo.week_days_this_month

    month_end_target = Target(adjusted_goal, this_week_month_spent, this_week_this_month,
                              dateinfo.week_start, min(dateinfo.next_week_start, dateinfo.next_month_start))

    daily_pace = flex / dateinfo.days_this_month
    split_week_goal = daily_pace * dateinfo.week_days_next_month
    split_week_trans = this_week[(this_week.date >= dateinfo.next_month_start)]
    split_week_spent = split_week_trans.adjusted.sum()
    month_start_target = Target(split_week_goal, split_week_spent, split_week_trans,
                                dateinfo.next_month_start, max(dateinfo.next_month_start,
                                                               dateinfo.next_week_start))

    return month_end_target, month_start_target


def _get_last_week(df, flex, dateinfo):
    old_dateinfo = DateInfo(dateinfo.last_week_end)

    month_end, month_start = _get_adjusted_targets(df, flex, old_dateinfo)

    if month_start.goal > 0:
        return month_start

    return month_end


def _get_last_month(df, flex, dateinfo):
    last_month_end = dateinfo.month_start - datetime.timedelta(days=1)
    old_dateinfo = DateInfo(last_month_end)

    month_end = _get_month_target(df, flex, old_dateinfo)

    return month_end


def get_targets(df, flex, date=None):
    dateinfo = DateInfo(date)

    month_end, month_start = _get_adjusted_targets(df, flex, dateinfo)
    return {
        "month": _get_month_target(df, flex, dateinfo),
        "adjusted": month_end,
        "weekly": _get_week_target(df, flex, dateinfo),
        "split": month_start,
        "lastweek": _get_last_week(df, flex, dateinfo),
        "lastmonth": _get_last_month(df, flex, dateinfo)
    }


def summary_data(dateinfo, df, flex):

    def _match_cur_month(date):
        return date.month == dateinfo.date.month

    # Get the dates for every past week.
    infos = []
    cur_dateinfo = dateinfo
    while _match_cur_month(cur_dateinfo.last_week_end):
        new_date_info = DateInfo(cur_dateinfo.last_week_end)
        infos.append(new_date_info)
        cur_dateinfo = new_date_info

    targets = []
    for info in infos:
        month_end, month_start = _get_adjusted_targets(df, flex, info)

        if _match_cur_month(month_end.end):
            targets.append(month_end)
        else:
            targets.append(month_start)

    sorted_targets = sorted(targets, key=lambda t: t.start)
    lines = []
    for i, target in enumerate(sorted_targets, 1):
        num_days = (target.end - target.start).days + 1
        if num_days < 7:
            short = "(%d days)" % num_days
        else:
            short = ""

        line = "Week {i}{short}: ${spent:.2f} / {goal:.2f} ({diff:+.2f})".format(
            i=i, spent=target.spent, goal=target.goal, short=short, diff=target.difference)

        lines.append(line)

    return lines



