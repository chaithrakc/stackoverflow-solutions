import logging

from src.sqllite_data_retriever import DataDownloader

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    dataDownload = DataDownloader()
    dataDownload.download_and_save_data()