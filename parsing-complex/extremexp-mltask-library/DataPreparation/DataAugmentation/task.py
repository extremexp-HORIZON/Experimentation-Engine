import analytics_task_library.bindings as bindings
 
ASSET = "policy_based_data_augmentation"

TASK = "DummyAugmentation"
 
if __name__ == '__main__':
 
    dataset = ph.load_datasets(variables, "data_train")

    samples = int(variables.get("da_samples"))

    method = variables.get("da_method") 

    distance = variables.get("da_distance") 

    parameters = {"Method": "SMOTE",

                  "Samples": 20,

                  "Distance": "pairwise", 

                  "datahandler": "json", 

                  "data": input_dataset.to_dict(orient='records'), 

                  "label": "label"}


    result = bindings.run_analytical_task(asset, task, parameters)

    new_dataset = pd.concat([dataset, result])
 
    ph.save_datasets(variables, ("data_train", new_dataset))
 