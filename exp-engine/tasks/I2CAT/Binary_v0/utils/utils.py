import pandas as pd
import json
import os


def load_data(path_load: str) -> pd.DataFrame:
    try:
        data = pd.read_pickle(path_load)
        return data
    except FileNotFoundError:
        print("File not found. Please provide a valid path.")
        return None
    
    
def save_metrics(metrics: dict, path_save: str) -> None:
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path_save), exist_ok=True)
        
        with open(path_save, 'w') as json_file:
            json.dump(metrics, json_file)
        print("Metrics saved successfully.")
    except FileNotFoundError:
        print("File not found. Please provide a valid path.")