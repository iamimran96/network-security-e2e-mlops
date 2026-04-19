from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataIngestionConfig, TrainingPipelineConfig, DataValidationConfig, DataTransformationConfig, ModelTrainerConfig

import sys

if __name__ == "__main__":
    try:
        logging.info("Starting Data Ingestion")
        training_pipeline_config = TrainingPipelineConfig()
        data_ingestion_config = DataIngestionConfig(training_pipeline_config=training_pipeline_config)
        logging.info("Initiating the Data Ingestion")
        data_ingestion = DataIngestion(data_ingestion_config=data_ingestion_config)
        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        logging.info("Data Ingestion Completed")
        print(data_ingestion_artifact)
        data_validation_config = DataValidationConfig(training_pipeline_config=training_pipeline_config)
        data_validation = DataValidation(data_validation_config, data_ingestion_artifact)
        logging.info("Initiate the Data Validation")
        data_validation_artifact = data_validation.initiate_data_validation()
        logging.info("Data Validation Completed")
        print(data_validation_config)
        data_transformation_config = DataTransformationConfig(training_pipeline_config=training_pipeline_config)
        data_transformation = DataTransformation(data_validation_artifact, data_transformation_config)
        logging.info("Initiate the Data Transformation")
        data_transformation_artifact = data_transformation.initiate_data_transformation()
        logging.info("Data Transformation Completed")
        print(data_ingestion_artifact)

        logging.info("Model training initiated")
        model_trainer_config = ModelTrainerConfig(training_pipeline_config=training_pipeline_config)
        model_trainer = ModelTrainer(model_trainer_config=model_trainer_config, data_transformation_artifact=data_transformation_artifact)
        model_trainer_artifact = model_trainer.initiate_model_trainer()
        logging.info("Model training completed")
        

    except Exception as e:
        raise NetworkSecurityException(e, sys)