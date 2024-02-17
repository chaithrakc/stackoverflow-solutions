import logging
import os
from datetime import datetime

import pandas as pd
import yfinance as yf
from sqlalchemy import create_engine, text


class DataDownloader:

    def __init__(self, ASSET='TSLA'):
        self.ASSET = ASSET

    def download_and_save_data(self, interval='1d'):

        period = '10y'
        if interval[-1] == 'h':
            period = '719d'

        logging.info("Data download in progress")

        file_dir = os.path.dirname(os.path.abspath(__file__))
        data_folder = 'staging1_download'
        file_path = os.path.join(file_dir, data_folder, f'data_ASSET_{self.ASSET}_interval_{interval}.txt')

        data = yf.download(tickers=self.ASSET, period=period, interval=interval)
        data.sort_index(ascending=True)

        if interval[-1] == 'h':
            data = data.reset_index()
            data['Date'] = data['Datetime']
            data['Date'] = data['Date'].astype(str)
            data['Date'] = data['Date'].str[:-6]
            data = data.set_index('Date')
            cols_to_delete = [
                'Adj Close',
                'Datetime',
            ]
        else:
            cols_to_delete = [
                'Adj Close',
            ]
        data = data.drop(columns=cols_to_delete)

        # managing last available date. We want candles when markets has generated them.
        last_date_available = data.index[-1]
        current_date = datetime.now()

        if interval[-1] == 'd':
            current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
            if isinstance(last_date_available, str):
                last_date_available = datetime.strptime(last_date_available, '%Y-%m-%d')


        elif interval[-1] == 'h':
            current_date = current_date.replace(minute=0, second=0, microsecond=0)
            if isinstance(last_date_available, str):
                last_date_available = datetime.strptime(last_date_available, '%Y-%m-%d %H:%M:%S')

        # logging.info(f"data downloder last date available {last_date_available} and current {current_date}")
        # logging.info(f"Cond verifiaction {str(current_date) == last_date_available}")

        if current_date == last_date_available:
            data = data[:-1]
        elif current_date < last_date_available:
            raise Exception("Something is wrong with dates during download. Please verify with data provider.")

        data.to_csv(file_path, header=True, index=True, sep=";")

        # when we switch to db

        file_dir = os.path.dirname(os.path.abspath(__file__))
        data_folder = 'staging1_download\\'
        database_path = os.path.join(file_dir, data_folder)
        databasePathName = database_path + 'staging1_download_DailyData.sqlite'
        print(databasePathName)

        # data["interval"] = interval
        data["Asset"] = self.ASSET
        data["INTERVAL"] = interval

        if not os.path.isfile(databasePathName):

            if interval[-1] == 'd':
                engine = create_engine(f'sqlite:///{databasePathName}', echo=True)
                data.to_sql("staging1_download_DailyData", con=engine, index=True)


        else:
            engine = create_engine(f'sqlite:///{databasePathName}', echo=True)
            con = engine.connect()
            query = text(f""" 
            SELECT * 
            FROM staging1_download_DailyData
            WHERE ASSET='{self.ASSET}' AND INTERVAL='{interval}'
            """)

            df = pd.read_sql(query, con)
            print(df.shape)

        logging.info("Data download executed")