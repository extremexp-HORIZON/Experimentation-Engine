import pandas as pd
import xgboost as xgb
from sklearn import metrics


def metrics_model(model: xgb.XGBClassifier, dataset: pd.DataFrame) -> dict:

    # Evauate the model and give some metrics and save the metrics
 
    # Split the test dataset into features and labels
    x_test = dataset.drop(['label'], axis=1)
    y_test = dataset['label']

    # Make predictions on the test set
    y_pred = model.predict(x_test)
 
    tn, fp, fn, tp = metrics.confusion_matrix(y_test, y_pred).ravel()
 
    # Calculate and print various metrics
    metrics_dict = {
                    "accuracy": metrics.accuracy_score(y_test, y_pred),
                    "precision": metrics.precision_score(y_test, y_pred),
                    "recall": metrics.recall_score(y_test, y_pred),
                    "f1_score": metrics.f1_score(y_test, y_pred),
                    "f1_macro": metrics.f1_score(y_test, y_pred, average='macro'),
                    "true_positives": int(tp),
                    "false_positives": int(fp),
                    "true_negatives": int(tn),
                    "false_negatives": int(fn)
                }
    
    return metrics_dict

def f1_score(y_test: pd.DataFrame, y_pred: pd.DataFrame) -> float:
    return metrics.f1_score(y_test, y_pred)