import os
import sys

from networksecurity.constant.traning_pipeline import TRAINING_BUCKET_NAME
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.cloud.s3_syncer import S3Sync

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer

from networksecurity.entity.config_entity import (
    DataIngestionConfig, 
    TrainingPipelineConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig
)

from networksecurity.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact,
    DataTransformationArtifact,
    ModelTrainerArtifact
)

class TrainingPipeline:
    def __init__(self):
        try:
            self.training_pipeline_config = TrainingPipelineConfig()
            self.s3_sync = S3Sync()
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def start_data_ingestion(self) -> DataIngestionArtifact:
        try:
            logging.info("Starting Data Ingestion")
            data_ingestion_config = DataIngestionConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Initiating the Data Ingestion")
            data_ingestion = DataIngestion(data_ingestion_config=data_ingestion_config)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            logging.info("Data Ingestion Completed")
            return data_ingestion_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    def start_data_validation(self, data_ingestion_artifact: DataIngestionArtifact) -> DataValidationArtifact:
        try:
            data_validation_config = DataValidationConfig(training_pipeline_config=self.training_pipeline_config)
            data_validation = DataValidation(data_validation_config, data_ingestion_artifact)
            logging.info("Initiate the Data Validation")
            data_validation_artifact = data_validation.initiate_data_validation()
            logging.info("Data Validation Completed")
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def start_data_transformation(self, data_validation_artifact: DataValidationArtifact) -> DataTransformationArtifact:
        try:
            data_transformation_config = DataTransformationConfig(training_pipeline_config=self.training_pipeline_config)
            data_transformation = DataTransformation(data_validation_artifact, data_transformation_config)
            logging.info("Initiate the Data Transformation")
            data_transformation_artifact = data_transformation.initiate_data_transformation()
            logging.info("Data Transformation Completed")
            return data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def start_model_trainer(self, data_transformation_artifact: DataTransformationArtifact) -> ModelTrainerArtifact:
        try:
            model_trainer_config = ModelTrainerConfig(training_pipeline_config=self.training_pipeline_config)
            model_trainer = ModelTrainer(model_trainer_config, data_transformation_artifact)
            logging.info("Initiate the Model Trainer")
            model_trainer_artifact = model_trainer.initiate_model_trainer()
            logging.info("Model Trainer Completed")
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    def sync_artifact_dir_to_s3(self):
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/artifact/{self.training_pipeline_config.timestamp}"
            # self.s3_sync.sync_folder_to_s3(folder=self.training_pipeline_config.artifact_dir, aws_bucket_url=aws_bucket_url)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def sync_saved_model_dir_to_s3(self):
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/final_model/{self.training_pipeline_config.timestamp}"
            # self.s3_sync.sync_folder_to_s3(folder="final_model", aws_bucket_url=aws_bucket_url)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    

    def run_pipeline(self):
        try:
            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
            data_transformation_artifact = self.start_data_transformation(data_validation_artifact=data_validation_artifact)
            model_trainer_artifact = self.start_model_trainer(data_transformation_artifact=data_transformation_artifact)
            self.sync_artifact_dir_to_s3()
            self.sync_saved_model_dir_to_s3()

            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e