import pandas as pd
import os

from . import common


class CsvBackend(common.Backend):

    def __init__(self, filename, flex):
        self.flex = flex
        self.filename = filename

    def get_flex(self):
        return self.flex

    def get_transactions(self):
        if os.path.isfile(self.filename):
            df = pd.read_csv(self.filename)
        else:
            df = pd.DataFrame([], columns=self.ALL_COLS)

        return common.prepare_transactions(df)

    def save_transactions(self, transactions):
        transactions.to_csv(self.filename, index=False, encoding='utf8')
