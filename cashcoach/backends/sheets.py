import gsheets
import logging
import pandas as pd

from cashcoach import secrets
from . import common

logger = logging.getLogger("sheets")


def _to_num(val):
    return float(val.replace("$", "").replace(",", ""))


class SheetsBackend(common.Backend):
    TRANSACTIONS_SHEET = "all-together"

    def __init__(self, spreadsheet_name):
        self._ss = gsheets.get_spreadsheet(spreadsheet_name)

    def _get_monthly_expenses(self):
        expenses = self._ss.get_sheet("Expenses")
        expenses['amount'] = expenses['My Share'].apply(_to_num)
        return expenses.amount.sum()

    def get_flex(self):
        expenses = self._get_monthly_expenses()
        flex = common.calculate_flex(secrets.GROSS, secrets.NET,
                                     expenses, secrets.SAVINGS_RATE)

        return flex

    def get_transactions(self):
        df = self._ss.get_sheet(self.TRANSACTIONS_SHEET)
        return common.prepare_transactions(df)

    def save_transactions(self, spend_df):
        logging.info("Saving spreadsheet...")
        self._ss.save_sheet(self.TRANSACTIONS_SHEET, spend_df)
        logging.info("Success!")
