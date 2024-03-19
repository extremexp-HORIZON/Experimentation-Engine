_WORK IN PROGRESS_

## Overview 
This is (or will be eventially) the heart of the experimentation framework.  

The Python script parses the model of in the `IDEKO.dsl` file 
based on the textx grammar specified in `workflow_grammar.tx`.

According to the parsed model, experiments are generated and run. 

In the first version, the Python SDK of Proactive will be used for running the experiments.
We still need to connect the two parts by having the `main.py` essentially create a proactive workflow 
as in, e.g. `ideko-case.py`.

### Installation
```
python3 -m venv env    #(if not already present) 
source ./env/bin/activate
pip install textx
```

### Running
```
source ./env/bin/activate
python main.py
```

### Checking model and meta-model via textx

#### Preliminaries
1. Make sure you activate (and create if needed) the virtual environment via `source ./env/bin/activate`
1. Make sure that the xtext library is installed via `pip install textx`

#### Check meta-model
```
textx check workflow_grammar.tx
```

#### Check model
```
textx generate IDEKO.dsl --language workflow_grammar.tx --target plantuml
```

### Generating graphs via textx

#### Preliminaries
1. Download and install Graphviz for your OS via https://graphviz.org/download/
1. (Optional) Download and install PlantUML via https://plantuml.com/download
1. Make sure you activate (and create if needed) the virtual environment via `source ./env/bin/activate`
1. Make sure that the xtext library is installed via `pip install textx`

#### Generate PNG of meta-model graph (via Graphviz)
```
textx generate workflow_grammar.tx --target dot
dot -Tpng -O workflow_grammar.dot
rm workflow_grammar.dot
```

#### Generate PNG of meta-model graph (via PlantUML)
```
textx generate workflow_grammar.tx --target plantuml
plantuml workflow_grammar.pu
rm workflow_grammar.pu
```

#### Generate PNG of model graph (only possible via Graphviz)
```
textx generate IDEKO.dsl --grammar workflow_grammar.tx --target dot
dot -Tpng -O IDEKO.dot
rm IDEKO.dot 
```
