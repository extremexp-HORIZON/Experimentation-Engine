import os
import textx

with open('../dsl/examples_new/no-event.dsl', 'r') as file:
    workflow_code = file.read()

workflow_metamodel = textx.metamodel_from_file('../dsl/workflow_grammar_new.tx')
workflow_model = workflow_metamodel.model_from_str(workflow_code)


