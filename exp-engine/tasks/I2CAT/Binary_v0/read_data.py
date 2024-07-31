import pandas as pd

[sys.path.append(os.path.join(os.getcwd(), folder)) for folder in variables.get("dependent_modules_folders").split(",")]
import src.utils.proactive_helper as ph


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
    dataset_file = f'{path}/{dataset_id}/min_windows_size_6/{entity_type}_features.pckl'
    try:
        data = pd.read_pickle(dataset_file)
        return data
    except FileNotFoundError:
        print(f"File not found at path: {dataset_file}")
        return None


if __name__ == '__main__':

    #dataset_id = variables.get("dataset_id")
    #entity_type = variables.get("entity_type")

    path = variables.get("InputData")
    dataset_id = "phishing_behaviour"
    entity_type = "desktop"


    dataset = load_data(path, dataset_id, entity_type)

    ph.save_datasets(variables, ("dataset", dataset))


