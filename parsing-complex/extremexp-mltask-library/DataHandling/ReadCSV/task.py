import proactive_helper as ph
import pandas as pd 

input_file_path = ph.get_input("ExternalDataFile")

df = pd.read_csv(zip_file.open(input_file_path), delimiter = ";")

ph.save_output("Dataframe", df)