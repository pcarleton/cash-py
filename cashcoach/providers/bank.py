import pandas as pd

from plaid import Client
import logging
from cashcoach.secrets import CLIENT_ID, CLIENT_SECRET, PAUL_TOKEN, TAYLOR_TOKEN, NICKNAMES


Client.config({
    'url': 'https://tartan.plaid.com'
})


logger = logging.getLogger(__name__)

def fetch_transactions(token, start_date):
    client = Client(client_id=CLIENT_ID,
                    secret=CLIENT_SECRET,
                    access_token=token)

    response = client.connect_get(opts={'gte': start_date})
    trans = response.json()
    df = pd.DataFrame(trans['transactions'])

    return df


def get_new_spending():
    start_date = '2016-02-01'
    logging.info("Fetching Paul...")
    paul_spending = fetch_transactions(PAUL_TOKEN, start_date)
    logging.info("Fetching Taylor...")
    taylor_spending = fetch_transactions(TAYLOR_TOKEN, start_date)

    all_df = pd.concat([paul_spending, taylor_spending]).sort('date', ascending=False)

    all_df['account'] = all_df._account.apply(lambda account_id: NICKNAMES[account_id])
    # Categories is a list which can't be sent as JSON to a google sheet
    all_df['categories'] = all_df.category.apply(lambda cs: ", ".join(cs) if type(cs) == list else '')

    return all_df


