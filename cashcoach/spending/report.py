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


def last_n(backend, n=5):
    odf = backend.get_transactions()

    df = odf[odf.adjusted > 0].sort("date", ascending=False).reset_index(drop=True)

    lines = []
    for idx, row in df[:n].iterrows():
        lines.append("{idx}. {name:30} {amount:.2f}".format(
            idx=idx, name=row['name'], amount=row.adjusted))

    return "\n".join(lines)