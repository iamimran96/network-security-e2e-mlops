from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

# Config
from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact

# Regular Library
import os
import sys
import numpy as np
import pandas as pd
import pymongo
from typing import List
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv

load_dotenv()

# Database URL
MONGO_DB_URL=os.getenv("MONGO_DB_URL")

class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def export_collection_as_dataframe(self) -> pd.DataFrame:
        """
        Method Name :   export_collection_as_dataframe
        Description :   This method exports the data from mongodb and returns the pandas dataframe.

        Output      :   pandas dataframe
        On Failure  :   Raise Exception
        """
        try:
            logging.info("Exporting data from Mongodb")
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            database = self.mongo_client[self.data_ingestion_config.database_name]
            collection = database[self.data_ingestion_config.collection_name]
            df = pd.DataFrame(list(collection.find()))
            logging.info(f"Dataframe shape : {df.shape}")
            if "_id" in df.columns:
                df = df.drop(columns=["_id"], axis=1)
            df.replace({"na":np.nan},inplace=True)
            logging.info("Successfully exported data from Mongodb")
            return df
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def export_data_to_feature_store(self, dataframe: pd.DataFrame) -> None:
        """
        Method Name :   export_data_to_feature_store
        Description :   This method exports the dataframe to feature store.
        Output      :   Dataframe
        On Failure  :   Raise Exception
        """
        try:
            logging.info("Exporting data to feature store")
            feature_store_dir = os.path.dirname(self.data_ingestion_config.feature_store_file_path)
            os.makedirs(feature_store_dir, exist_ok=True)
            dataframe.to_csv(self.data_ingestion_config.feature_store_file_path, index=False, header=True)
            logging.info("Data successfully exported to feature store")
            return dataframe
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def split_data_as_train_test(self, dataframe: pd.DataFrame) -> None:
        """
        Method Name :   split_data_as_train_test
        Description :   This method splits the dataframe into train and test file.
        Output      :   None
        On Failure  :   Raise Exception
        """
        try:
            train, test = train_test_split(dataframe, test_size=self.data_ingestion_config.train_test_split_ratio)
            logging.info("Performed train test split")

            dir_name = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_name, exist_ok=True)

            logging.info("Exporting train data")
            train.to_csv(self.data_ingestion_config.training_file_path, index=False, header=True)
            logging.info("Exporting test data")
            test.to_csv(self.data_ingestion_config.testing_file_path, index=False, header=True)

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_ingestion(self) -> None:
        try:
            logging.info("Starting data ingestion")
            dataframe = self.export_collection_as_dataframe()
            dataframe = self.export_data_to_feature_store(dataframe)
            self.split_data_as_train_test(dataframe)
            data_ingestion_artifact = DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path
            )
            logging.info("Data ingestion completed successfully")
            return data_ingestion_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)