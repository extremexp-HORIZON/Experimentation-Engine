[sys.path.append(os.path.join(os.getcwd(), folder)) for folder in variables.get("dependent_modules_folders").split(",")]

import pandas as pd
from sklearn import metrics
from sklearn.metrics import classification_report

import utils.proactive_helper as ph


SEED = 42

def benchmarking(model: object, validation: pd.DataFrame):  

    # Split the test dataset into features and labels
    columns_to_drop = ["timestamp", "user_id", "entity", "label"]
    labels_to_drop = [col for col in columns_to_drop if col in validation.columns]
   
    validation = validation[validation["label"] != -1]
    
    x_test = validation.drop(labels_to_drop , axis=1)
    y_test = validation['label']

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
                    "false_negatives": int(fn)}
    
    # Calculate the dataframe with sample-level fp and fn rates 
    results_df = pd.DataFrame({'Predicted': y_pred, 'Actual': y_test})
    classification_rep = pd.DataFrame(classification_report(y_test, y_pred,output_dict=True)).transpose()
    validation_ret = validation.copy()
    validation_ret['predicted'] = y_pred
    validation_ret['false_positive'] = (results_df['Predicted'] == 1) & (results_df['Actual'] == 0)
    validation_ret["false_negative"] = (results_df['Predicted'] == 0) & (results_df['Actual'] == 1)

    return metrics_dict, validation_ret , classification_rep


if __name__ == '__main__':
    
    model = variables.get("model") 
    validation_dataset = ph.load_datasets(variables, "data_validation")
    
    metrics_dict, validation_ret , classification_rep = benchmarking(model, validation_dataset)
    
    print (metrics_dict) # Main output of the workflow
    
