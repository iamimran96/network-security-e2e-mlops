import os
import sys

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.artifact_entity import (
    DataTransformationArtifact,
    ModelTrainerArtifact
)

from networksecurity.entity.config_entity import ModelTrainerConfig

from networksecurity.utils.main_utils.utils import save_object, load_object
from networksecurity.utils.main_utils.utils import load_numpy_array_data, evaluate_models
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_metric

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import r2_score

import mlflow

class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig, data_transformation_artifact: DataTransformationArtifact):
        try:
            logging.info(f"{'>>'*20} Model Trainer {'<<'*20}")
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def track_mlflow(self, best_model, classification_metric, x_train):
        with mlflow.start_run():
            f1_score = classification_metric.f1_score
            precision_score = classification_metric.precision_score
            recall_score = classification_metric.recall_score

            mlflow.log_metric("f1_score", f1_score)
            mlflow.log_metric("precision_score", precision_score)
            mlflow.log_metric("recall_score", recall_score)

            mlflow.sklearn.log_model(best_model, name="model", input_example=x_train[:5])


    def train_model(self, x_train, y_train, x_test, y_test):
        models = {
            "Random Forest": RandomForestClassifier(verbose=1),
            "Decision Tree": DecisionTreeClassifier(),
            "Gradient Boosting": GradientBoostingClassifier(verbose=1),
            "Logistic Regression": LogisticRegression(verbose=1),
            "AdaBoost Classifier": AdaBoostClassifier(),
        }

        params = {
            "Random Forest": {
                # 'criterion':['gini', 'entropy', 'log_loss'],
                
                # 'max_features':['sqrt','log2',None],
                'n_estimators': [8,16,32,128,256]
            },
            "Decision Tree": {
                "criterion": ["gini", "entropy", "log_loss"],
                # 'splitter':['best','random'],
                # 'max_features':['sqrt','log2'],
            },
            "Gradient Boosting": {
                # 'loss':['log_loss', 'exponential'],
                'learning_rate':[.1,.01,.05,.001],
                'subsample':[0.6,0.7,0.75,0.85,0.9],
                # 'criterion':['squared_error', 'friedman_mse'],
                # 'max_features':['auto','sqrt','log2'],
                'n_estimators': [8,16,32,64,128,256]
            },
            "Logistic Regression": {},
            "AdaBoost Classifier": {
                'learning_rate':[.1,.01,.001],
                'n_estimators': [8,16,32,64,128,256]
            },
        }

        model_report: dict = evaluate_models(X_train=x_train, y_train=y_train, X_test=x_test, y_test=y_test, models=models, param=params)

        best_model_score = max(sorted(model_report.values()))

        # to get best model score from dict
        best_model_name = list(model_report.keys())[
            list(model_report.values()).index(best_model_score)
        ]

        best_model = models[best_model_name]
        y_train_pred = best_model.predict(x_train)

        classification_train_metric = get_classification_metric(y_true=y_train, y_pred=y_train_pred)

        y_test_pred = best_model.predict(x_test)

        classification_test_metric = get_classification_metric(y_true=y_test, y_pred=y_test_pred)

        self.track_mlflow(best_model=best_model, classification_metric=classification_test_metric, x_train=x_train)

        preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)

        model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)

        os.makedirs(model_dir_path, exist_ok=True)

        network_model = NetworkModel(preprocessor=preprocessor, model=best_model)
        save_object(file_path=self.model_trainer_config.trained_model_file_path, obj=network_model)

        save_object(file_path="final_model/model.pkl", obj=network_model)

        model_trainer_artifact = ModelTrainerArtifact(
            trained_model_file_path=self.model_trainer_config.trained_model_file_path,
            trained_metric_artifact=classification_train_metric,
            test_metric_artifact=classification_test_metric
        )
        logging.info(f"Model trainer artifact: {model_trainer_artifact}")
        return model_trainer_artifact



    def initiate_model_trainer(self):
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            # loading transformed data 
            train_array = load_numpy_array_data(train_file_path)
            test_array = load_numpy_array_data(test_file_path)

            # splitting the data into input and target feature
            x_train, y_train = train_array[:,:-1], train_array[:,-1]
            x_test, y_test = test_array[:,:-1], test_array[:,-1]

            model_trainer_artifact = self.train_model(x_train, y_train, x_test, y_test)
            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)