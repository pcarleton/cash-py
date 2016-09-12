import gsheets
import logging
import pandas as pd

from cashcoach import secrets

logger = logging.getLogger("sheets")


def _adjust(row):
    amount = float(row.amount)
    if row.exclude or amount < 0:
        return 0
    mult = secrets.ADJUSTMENTS.get(row.account, 1)
    return amount*mult


def _to_num(val):
    return float(val.replace("$", "").replace(",", ""))


def _calculate_flex(monthly_gross, monthly_net, monthly_expenses, savings_rate):
    monthly_savings = monthly_gross * savings_rate
    flex = monthly_net - monthly_expenses - monthly_savings
    return flex


class SheetsBackend(object):
    SPENDING_COLS = ['_id', 'account', 'date', 'name', 'amount', 'categories']
    TRANSACTIONS_SHEET = "all-together"

    def __init__(self, spreadsheet_name):
        self._ss = gsheets.get_spreadsheet(spreadsheet_name)

    def _get_monthly_expenses(self):
        expenses = self._ss.get_sheet("Expenses")
        expenses['amount'] = expenses['My Share'].apply(_to_num)
        return expenses.amount.sum()

    def get_flex(self):
        expenses = self._get_monthly_expenses()
        flex = _calculate_flex(secrets.GROSS, secrets.NET, expenses, secrets.SAVINGS_RATE)

        return flex

    def get_transactions(self):
        df = self._ss.get_sheet(self.TRANSACTIONS_SHEET)
        df.date = pd.to_datetime(df.date)
        df['adjusted'] = df.apply(_adjust, axis=1)

        return df

    def update_transactions(self, new_transactions):
        old_df = self.get_transactions()
        new_df = new_transactions[self.SPENDING_COLS]
        logging.info("Merging old and new.")
        both_df = pd.concat([old_df, new_df])

        dedup_df = both_df.drop_duplicates("_id")

        excluded = old_df[['_id', 'exclude']]

        spend_df = dedup_df[self.SPENDING_COLS].merge(excluded, on='_id', how='left')

        logging.info("Saving spreadsheet...")
        self._ss.save_sheet(self.TRANSACTIONS_SHEET, spend_df)
        logging.info("Success!")