#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
[sys.path.append(os.path.join(os.getcwd(), folder)) for folder in variables.get("dependent_modules_folders").split(",")]

import pandas as pd
import xgboost as xgb

import utils.metrics as ut_metrics
import split_dataset as sd

import utils.proactive_helper as ph

SEED = 42
NUM_WORKERS = -1


def train_model(dataset: object, n_splits: int, grid_search_cross_validation: str, 
                grid_search_n_splits: int, outer_cross_validation: str, 
                outer_cross_validation_n_splits: int, scoring: int, 
                hyperparameters: dict) -> (xgb.XGBClassifier, pd.DataFrame, pd.DataFrame):

    # Function to train a parent model via cross validation grid search and compute metrics
    overall_best_model = None
    best_data_train = None
    best_data_test = None
    overall_best_score = -1
 
    fix_params = {'objective': 'binary:logistic', "nthread": NUM_WORKERS, "seed": SEED}
 
    # Splits for cross validation using StratifiedKfold
    
    splits = sd.cross_validation_split(dataset, outer_cross_validation_n_splits, outer_cross_validation, SEED)

    # Labels not to use in train test
    columns_to_drop = ["timestamp", "user_id", "entity", "label"]
    labels_to_drop = [col for col in columns_to_drop if col in dataset.columns]
        
    # Grid search declaration
    csv = sd.grid_search_creator(fix_params, hyperparameters, grid_search_n_splits, 
                                      scoring, NUM_WORKERS, grid_search_cross_validation, SEED)
 
    # Cross_validation
    for split, (train_index, test_index) in enumerate(splits):

        print(f"Cross validation: {split}")
        x_train = dataset.iloc[train_index].drop(labels_to_drop, axis=1)
        y_train = dataset.iloc[train_index]["label"]

        """if isinstance(augmented_data, pd.DataFrame) and not augmented_data.empty: #if augemtned_data
            print("[DEBUG]: Data augemntation")
            fraction_augemnted_samples = ((grid_search_n_splits-1)/grid_search_n_splits)*((outer_cross_validation_n_splits-1)/outer_cross_validation_n_splits)
            split_augmented_data = augmented_data.sample(int(fraction_augemnted_samples*len(augmented_data)))
            x_train = pd.concat([x_train, split_augmented_data.drop(["label"], axis=1)])
            y_train = pd.concat([y_train, split_augmented_data["label"]])       
        """

        # Fit model
        csv.fit(x_train, y_train)

        # Calculate score in test
        x_test = dataset.iloc[test_index].drop(labels_to_drop, axis=1)
        y_test = dataset.iloc[test_index]["label"]
        y_pred = csv.best_estimator_.predict(x_test)
        test_score = ut_metrics.f1_score(y_test, y_pred)
        print(f"Test score:{test_score}")

        # Save the best model if it performs better on the test set
        if test_score > overall_best_score:
            overall_best_model = csv.best_estimator_
            overall_best_score = test_score
            best_data_train = dataset.iloc[train_index]
            best_data_test = dataset.iloc[test_index]
            # metricas = ut_metrics.metrics_model(overall_best_model, best_data_test)
            # print(f"Best scores: {metricas}")
        

    return overall_best_model, best_data_train, best_data_test
    

if __name__ == '__main__':
    
    dataset = ph.load_datasets(variables, "data_train")

    print ("TYPE: {}".format(type(dataset)))
    """
    n_splits = variables.get("n_splits") 
    grid_search_cross_validation =  variables.get("grid_search_cross_validation")
    grid_search_n_splits = variables.get("grid_search_n_splits")
    outer_cross_validation = variables.get("outer_cross_validation")
    outer_cross_validation_n_splits = variables.get("outer_cross_validation_n_splits")
    scoring = variables.get("scoring")
    
    hyperparameters =  {'max_depth': [variables.get("hyp_max_depth")], 
                        'min_child_weight': [variables.get("hyp_min_child_weight")],
                        'learning_rate': [variables.get("hyp_learning_rate")], 
                        'n_estimators': [variables.get("hyp_n_estimators")]}
    """
    n_splits = 2
    grid_search_cross_validation = "stratified"
    grid_search_n_splits = 5
    outer_cross_validation = "stratified"
    outer_cross_validation_n_splits = 5
    scoring = "f1"
    hyperparameters = {'max_depth': [2], 'min_child_weight': [1],
                       'learning_rate': [0.1], 'n_estimators': [100]}

    overall_best_model, best_data_train, best_data_test = train_model(dataset, n_splits, grid_search_cross_validation,
                                                                      grid_search_n_splits, outer_cross_validation,
                                                                      outer_cross_validation_n_splits,
                                                                      scoring, hyperparameters)


    ph.save_dataset(variables, "overall_best_model", overall_best_model)
