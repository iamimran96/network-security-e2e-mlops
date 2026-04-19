from  networksecurity.entity.artifact_entity import ClassificationMetricArtifact
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from sklearn.metrics import f1_score, precision_score, recall_score

def get_classification_metric(y_true, y_pred) -> ClassificationMetricArtifact:
    try:
        logging.info("Entered the get_classification_metric function")
        f1 = f1_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        classification_metric_artifact = ClassificationMetricArtifact(
            f1_score=f1,
            precision_score=precision,
            recall_score=recall
        )
        return classification_metric_artifact
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e