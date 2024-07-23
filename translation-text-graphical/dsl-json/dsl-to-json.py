import textx
import json

def parse_dsl(dsl):
    workflow_metamodel = textx.metamodel_from_file('workflow_grammar.tx')
    workflow_model = workflow_metamodel.model_from_str(dsl)

    if workflow_model:
        print("Successfully Parsed!")

    return workflow_model


def dsl_to_json(workflow_model):
    workflows = []
    for workflow in workflow_model.workflows:
        tasks = []
        configurations = []
        for element in workflow.elements:
            if element.__class__.__name__ == "DefineTask":
                tasks.append({"type": element.__class__.__name__, "name": element.name})

            if element.__class__.__name__ == "ConfigureTask":
                configurations.append({"type": element.__class__.__name__, "name": element.name, "implementation": element.filename, "dependency": element.dependency})


        workflows.append({"name": workflow.name, "elements": tasks, "configurations": configurations})
    return {"workflows": workflows}



with open('../json-dsl/simple-dsl.dsl', 'r') as file:
    dsl = file.read()

workflow_model = parse_dsl(dsl)

json_data = dsl_to_json(workflow_model)

json_string = json.dumps(json_data, indent=4)
print(json_string)
