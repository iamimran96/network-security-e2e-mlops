import os
import sys
import json
from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")
print(MONGO_DB_URL)

import certifi
ca = certifi.where()

import pandas as pd
import numpy as np
import pymongo
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

class NetworkDataExtract():
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def csv_to_json_convertor(self, file_path: str) -> list:
        try:
            df = pd.read_csv(file_path)
            df.reset_index(drop=True, inplace=True)
            records = list(json.loads(df.T.to_json()).values())
            return records
        except Exception as e:
            raise NetworkSecurityException(e, sys)
            
    def push_data_to_mongodb(self, records: list, db_name: str, collection_name: str):
        try:
            self.database = db_name
            self.collection = collection_name
            self.records = records
            
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            self.database = self.mongo_client[self.database]
            self.collection = self.database[self.collection]
            self.collection.insert_many(self.records)
            return (len(self.records))
        except Exception as e:
            raise NetworkSecurityException(e, sys)
            
if __name__ == "__main__":
    FILE_PATH = "./network_data/phisingData.csv"
    DATABASE = "NetworkSecurityDB"
    Collection = "NetworkData"
    network_obj = NetworkDataExtract()
    records = network_obj.csv_to_json_convertor(FILE_PATH)
    print(records)
    no_of_records = network_obj.push_data_to_mongodb(records,DATABASE,Collection)
    print(no_of_records)
        