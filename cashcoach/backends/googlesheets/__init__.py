import pandas as pd

from oauth2client.service_account import ServiceAccountCredentials

import httplib2

from apiclient import discovery

SCOPES = 'https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive'

DISCOVERY_URL = 'https://sheets.googleapis.com/$discovery/rest?version=v4'

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def get_arange_col(col_index):
    if col_index >= len(ALPHABET):
        first_let = ALPHABET[int(col_index / len(ALPHABET)) - 1]
        second_let = ALPHABET[col_index % len(ALPHABET)]
        return first_let + second_let
    
    return ALPHABET[col_index]

def _get_credentials(creds_file_name):
    return ServiceAccountCredentials.from_json_keyfile_name(creds_file_name, SCOPES)

def get_sheets_service(creds_file_name):
    creds = _get_credentials(creds_file_name)
    http = creds.authorize(httplib2.Http())
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=DISCOVERY_URL)
    return service



class Spreadsheet(object):
    
    def __init__(self, properties, service):
        self.properties = properties
        self.service = service
        
    @staticmethod
    def get(spreadsheet_id, service=None, creds_file_name=None):
        if service is None:
            service = get_sheets_service(creds_file_name)
        ss_props = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        
        return Spreadsheet(ss_props, service)
    
    def get_sheet(self, sheet_name):
        sheets_by_title = {s['properties']['title']: s for s in self.properties['sheets']}
    
        sheet_props = sheets_by_title.get(sheet_name)

        if not sheet_props:
            # TODO: Maybe throw an error
            return None

        num_cols = sheet_props['properties']['gridProperties']['columnCount']
        last_col_index = num_cols - 1

        arange = "'%s'!A1:%s" % (sheet_name, get_arange_col(last_col_index))

        ss_id = self.properties['spreadsheetId']

        response = self.service.spreadsheets().values().get(spreadsheetId=ss_id, range=arange).execute()

        values = response['values']

        column_names = values[0]
        data_rows = values[1:]

        df = pd.DataFrame(data_rows, columns=column_names)

        return df
    
    def save_sheet(self, sheet_name, df):
        ss_id = self.properties['spreadsheetId']

        last_col_index = len(df.columns) - 1
        num_rows = len(df)

        # TODO: Create new sheet if it doesn't exist
        arange = "'%s'!A1:%s%d" % (sheet_name, get_arange_col(last_col_index),
                                   num_rows + 1)

        col_names = list(df.columns)
        values = [col_names] + [r[1:] for r in df.itertuples()]
        body = {"values": values}
        
        print(body)

        return self.service.spreadsheets().values().update(
            spreadsheetId=ss_id,range=arange, body=body, valueInputOption='USER_ENTERED').execute()
