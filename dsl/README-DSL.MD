_WORK IN PROGRESS_

## Overview 
This is (or will be eventially) the heart of the experimentation framework.  

The Python script parses the model of in the `IDEKO.dsl` file 
based on the textx grammar specified in `workflow_grammar.tx`.

According to the parsed model, experiments are generated and run. 

In the first version, the Python SDK of Proactive will be used for running the experiments.
We still need to connect the two parts by having the `main.py` essentially create a proactive workflow 
as in, e.g. `ideko-case.py`.

## Instructions
```
python3 -m venv env    if not already present) 
source ./env/bin/activate
pip install textx
```

