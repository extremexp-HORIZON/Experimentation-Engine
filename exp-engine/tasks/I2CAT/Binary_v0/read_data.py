#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
[sys.path.append(os.path.join(os.getcwd(), folder)) for folder in variables.get("dependent_modules_folders").split(",")]

import utils.proactive_helper as ph
import pandas as pd


def load_data(path: str, dataset_id: str, entity_type: str) -> pd.DataFrame:
    """
    Load dataset based on provided path, dataset ID, and entity type.

    Parameters:
        path (str): Path to the dataset directory.
        dataset_id (str): Identifier for the dataset.
        entity_type (str): Type of entity data (e.g., desktop, mobile).

    Returns:
        pd.DataFrame or None: DataFrame containing loaded data or None if the file is not found.
    """
    dataset_file = "{}/{}_{}.parquet".format(path, dataset_id, entity_type)
    print(dataset_file)

    try:
        data = pd.read_parquet(dataset_file)
        return data
    except FileNotFoundError:
        print(f"File not found: {dataset_file}")
        return None


if __name__ == '__main__':

    #dataset_id = variables.get("dataset_id")
    #entity_type = variables.get("entity_type")
    dataset_id = "phishing_behaviour"
    entity_type = "workstation"

    path = variables.get("InputData")
    dataset = load_data(path, dataset_id, entity_type)

    ph.save_dataset(variables,"dataset", dataset)