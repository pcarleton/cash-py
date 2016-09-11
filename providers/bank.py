import pandas as pd

import gsheets
from plaid import Client
import logging
from cashcoach.secrets import CLIENT_ID, CLIENT_SECRET, PAUL_TOKEN, TAYLOR_TOKEN, NICKNAMES


Client.config({
    'url': 'https://tartan.plaid.com'
})


logger = logging.getLogger("bank")



SPENDING_COLS = ['_id', 'account', 'date', 'name', 'amount', 'categories']

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
    spending_columns = ['_id', 'account', 'date', 'name', 'amount', 'categories']

    return all_df[SPENDING_COLS]

def get_current_spending(spreadsheet, sheet_name):
    cur_df = spreadsheet.get_sheet(sheet_name)

    return cur_df

def get_budget_spreadsheet():
    spreadsheet_name = "Summer 2016 Budget"
    spreadsheet = gsheets.get_spreadsheet(spreadsheet_name)

    return spreadsheet

def update_spending():
    new_df = get_new_spending()

    ss = get_budget_spreadsheet()
    logging.info("Getting current spending...")
    old_df = get_current_spending(ss, "all-together")

    logging.info("Merging old and new.")
    both_df = pd.concat([old_df, new_df])

    dedup_df = both_df.drop_duplicates("_id")

    excluded = old_df[['_id', 'exclude']]

    spend_df = dedup_df[SPENDING_COLS].merge(excluded, on='_id', how='left')

    logging.info("Saving spreadsheet...")
    sheet_name = "all-together"
    ss.save_sheet(sheet_name, spend_df)

    logging.info("Success!")


def new_spending_df():
    new_df = get_new_spending()

    ss = get_budget_spreadsheet()
    logging.info("Getting current spending...")
    old_df = get_current_spending(ss, "all-together")

    logging.info("Merging old and new.")
    both_df = pd.concat([old_df, new_df])

    dedup_df = both_df.drop_duplicates("_id")

    excluded = old_df[['_id', 'exclude']]

    spend_df = dedup_df[SPENDING_COLS].merge(excluded, on='_id', how='left')

    return spend_df
