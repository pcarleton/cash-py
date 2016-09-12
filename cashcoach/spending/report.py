from cashcoach.spending import messages, transactions


def create_report(backend):
    flex = backend.get_flex()
    df = backend.get_transactions()
    targets = transactions.get_targets(df, flex)

    msgs = messages.make_messages(targets)

    return msgs
