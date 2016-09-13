from cashcoach.spending import messages, transactions


def create_report(backend):
    flex = backend.get_flex()
    df = backend.get_transactions()
    targets = transactions.get_targets(df, flex)

    msgs = messages.make_messages(targets)

    return msgs


def create_summary(backend):
    flex = backend.get_flex()
    df = backend.get_transactions()

    dateinfo = transactions.DateInfo()
    msgs = transactions.summary_data(dateinfo, df, flex)

    return msgs