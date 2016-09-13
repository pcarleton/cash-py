import pandas as pd
import logging

from cashcoach import secrets

logger = logging.getLogger("backend")


def calculate_flex(monthly_gross, monthly_net, monthly_expenses, savings_rate):
    monthly_savings = monthly_gross * savings_rate
    flex = monthly_net - monthly_expenses - monthly_savings
    return flex


def _adjust(row):
    amount = float(row.amount)
    if row.exclude or amount < 0:
        return 0
    mult = secrets.ADJUSTMENTS.get(row.account, 1)
    return amount*mult

def _fix_exclude(val):
    if val == '' or pd.isnull(val):
        return False
    return val == True or val == 'TRUE'

def prepare_transactions(df):
    df.date = pd.to_datetime(df.date)
    df['exclude'] = df.exclude.apply(_fix_exclude)
    df['adjusted'] = df.apply(_adjust, axis=1)


    return df


class Backend(object):
    SPENDING_COLS = ['_id', 'account', 'date', 'name', 'amount', 'categories']
    ALL_COLS = SPENDING_COLS + ['exclude']

    def get_transactions(self):
        raise NotImplementedError()

    def save_transactions(self, transactions):
        raise NotImplementedError()

    def get_flex(self):
        raise NotImplementedError()

    def update_transactions(self, new_transactions):
        old_df = self.get_transactions()
        new_df = new_transactions[self.SPENDING_COLS]
        logger.info("Merging old and new.")
        both_df = pd.concat([old_df, new_df])

        dedup_df = both_df.drop_duplicates("_id")

        excluded = old_df[['_id', 'exclude']]

        spend_df = dedup_df[self.SPENDING_COLS].merge(excluded, on='_id', how='left')

        self.save_transactions(spend_df)