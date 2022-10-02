from __future__ import print_function

import os.path
import requests
import xmltodict
import time
from datetime import datetime
from datetime import date
import schedule
import telegram

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from db_queries import PGWriter

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SAMPLE_SPREADSHEET_ID = '1WoYtgVd16FnhkGPAapsN3hFRZyXrosfOkJpn-meeKTc'
DATA_ROWS = 'Лист1!B2:E'


def format_delivery_time(delivery_time):
    
    delivery_time_pg = datetime.strptime(delivery_time, "%d.%m.%Y").strftime("%Y-%m-%d")

    return delivery_time_pg


def get_dollar_rate():
    
    '''
        Переводим доллары в рубли по курчу ЦБР
    '''

    cbr_url = 'https://www.cbr.ru/scripts/XML_dynamic.asp?date_req1=01/10/2022&date_req2=01/10/2022&VAL_NM_RQ=R01235'
    resp = requests.get(cbr_url)
    val_curs = xmltodict.parse(resp.content)
    rubles = float(val_curs['ValCurs']['Record']['Value'].replace(',', '.'))
    return rubles


def main():

    creds = None

    # Авторизация в Google API

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        
        # Читаем данные из Google Sheet

        service = build('sheets', 'v4', credentials=creds)

        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=DATA_ROWS).execute()
        values = result.get('values', [])

        to_db = [{'id': count,
                        'order_num': row[0],
                        'dollar_value': int(row[1]),
                        'ruble_value': int(row[1])*get_dollar_rate(),
                        'delivery_time': format_delivery_time(row[2])} for count, row in enumerate(values, start=1)]
        
        # Передаем данные на запись в базу
        PGWriter().upload_data_to_db(to_db)

        if not values:
            return


    except HttpError as err:
        print(err)


if __name__ == '__main__':

    # Создаем таблицу для последующей записи данных
    PGWriter().create_table()

    # Создаем шедулер, по которому скрипт будет запускаться раз в 2 минуты
    schedule.every(2).minutes.do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)



