import datetime

templates = {
    "month": {
        "base": "You've spent {spent:.2f} this month, you've got {left:.2f} to spend.",
        "over": "You've over spent by {over:.2f} this month."
    },
    "weekly": {
        "base": "You've spent {spent:.2f} this week, your goal is {goal:.2f}, so you have {left:.2f}.",
        "over": "You've over spent by {over:.2f} this week."
    },
    "adjusted": {
        "base": ("Based on your spending so far this month, you've got {goal:.2f} to spend this week. "
                 "You've spent {spent:.2f} so far, so you have {left:.2f} left to spend this week."),
        "over": "You've over spent by {over:.2f} this week."

    },
    "split": {
        "month_end": ("A new month is about to start. You have spent {spent:.2f} so far this week. "
                      "You have {left:.2f} to spend before {month_end_weekday}."),
        "month_start": ("A new month just started.  You have spent {spent:.2f} so far this month,"
                        " so you have {left:.2f} to spend the rest of the week.")
    },
    "end": {
        "good": "Great job! You under spent by {left:.2f} last {unit}!",
        "bad": "Oops, you over spent by {over:.2f} last {unit}. It's okay though, new {unit}, new chance!"
    }
}

weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def make_message(target, base, over, **extra):
    tmpls = [base]
    if target.over > 0:
        tmpls.append(over)

    extra.update(target.__dict__)
    msg = " ".join(tmpls).format(**extra)

    return msg


def make_messages(targets, date=None):

    msgs = {}
    for cat in ['month', 'weekly']:
        tmpls = templates[cat]
        msgs[cat] = make_message(targets[cat], tmpls['base'], tmpls['over'])

    split = targets['split']
    if split.goal > 0:
        if date is None:
            date = datetime.date.today()
        extra_args = {"month_end_weekday": weekdays[split.start.weekday()]}
        if date >= split.start:
            tmpl = templates['split']['month_start']
            target = split
        else:
            tmpl = templates['split']['month_end']
            target = targets['adjusted']

        msgs['adjusted'] = make_message(target, tmpl, "", **extra_args)
    else:
        tmpls = templates['adjusted']
        msgs['adjusted'] = make_message(targets['adjusted'], tmpls['base'], tmpls['over'])

    msgs['lastweek'] = end_message(targets['lastweek'], 'week')
    msgs['lastmonth'] = end_message(targets['lastmonth'], 'month')

    return msgs


def end_message(target, unit):
    tmpls = templates["end"]

    if target.over > 0:
        return make_message(target, "", tmpls['bad'], unit=unit)
    else:
        return make_message(target, tmpls['good'], '', unit=unit)