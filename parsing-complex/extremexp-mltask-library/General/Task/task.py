import proactive_helper as ph

# get inputs, e.g.;
input_dataset_1 = ph.get_input("InputDataset1")

# perform logic 
print("I am indeed working!")

# get outputs, e.g.;
ph.save_output(("OutputDataset1", output_dataset_1))
