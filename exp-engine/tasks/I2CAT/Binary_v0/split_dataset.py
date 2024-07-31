#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import KFold
from sklearn.model_selection import GridSearchCV
import xgboost as xgb

import utils.proactive_helper as ph

SEED = 42

def split_data(dataset: pd.DataFrame, proportion: float) -> (pd.DataFrame, pd.DataFrame):
    # Split data in train validation
    # The train validation splits do not share users.
    data_validation_unlabeled = dataset[dataset["label"] == -1]
    unique_users = dataset.loc[dataset["label"] != -1, 'user_id'].unique()
 
    # Split user IDs into train_test and validation sets
    # We fix validation dataset to be always the same by fixing the random state, the rest changes
    users_train_test, users_validation = train_test_split(unique_users, test_size=proportion, random_state=SEED)

    # Filter data for train and test sets based on user IDs
    data_train_test = dataset[dataset['user_id'].isin(users_train_test)]
    data_validation_labeled = dataset[dataset['user_id'].isin(users_validation)]

    data_validation = pd.concat([data_validation_unlabeled, data_validation_labeled])

    return data_train_test, data_validation


def cross_validation_split(data: pd.DataFrame, n_splits: int, 
                           cv_type: str = "kfold", seed:int = None):
    # Function to split dataset in n_splits and make th crossvalidation.
    if cv_type == "kfold":
        # print("Outer cross valdiation using KFOLD")
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
        return list(kf.split(data.drop(columns="label"), data["label"]))
    elif cv_type == "stratified":
        # print("Outer cross valdiation using stratified")
        kf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
        return list(kf.split(data.drop(columns="label"), data["label"]))
    
    return -1


def grid_search_creator(fix_params: dict, cv_params: dict, n_splits: int, 
                        scoring: str, n_jobs: int, cv_type: str = "kfold", seed:int = None):
    # Function to create a grid search object with the given parameters.
    if cv_type == "stratified":
        print("GridSearch using stratified")
        cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    elif cv_type == "kfold":
        print("GridSearch using KFold")
        cv = KFold(n_splits=n_splits, shuffle=True, random_state=seed)

    csv = GridSearchCV(xgb.XGBClassifier(**fix_params), cv_params, cv=cv, scoring=scoring, n_jobs=n_jobs)
    return csv


if __name__ == '__main__':

    proportion = variables.get("proportion")
    dataset = ph.load_datasets(variables, "dataset")

    data_train_test, data_validation = split_data(dataset,proportion, SEED)

    ph.save_datasets(variables, ("data_train", data_train_test))
    ph.save_datasets(variables, ("data_validation", data_validation))



    
