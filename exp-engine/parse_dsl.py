import os
import textx
from classes import *
from functions import *

with open('../dsl/examples_new/ideko-with-events.dsl', 'r') as file:
    no_events_workflow_code = file.read()

workflow_metamodel = textx.metamodel_from_file('../dsl/workflow_grammar_new.tx')
no_events_workflow_model = workflow_metamodel.model_from_str(no_events_workflow_code)

if no_events_workflow_model:
    print('parses dsl with no events')


print("*********************************************************")
print("***************** PARSE WORKFLOWS ***********************")
print("*********************************************************")

parsed_workflows = []
for component in no_events_workflow_model.component:
    if component.__class__.__name__ == 'Workflow':
        wf = Workflow(component.name)
        parsed_workflows.append(wf)

        task_dependencies = {}

        for e in component.elements:
            if e.__class__.__name__ == "DefineTask":
                task = WorkflowTask(e.name)
                wf.add_task(task)

            if e.__class__.__name__ == "DefineData":
                ds = WorkflowDataset(e.name)
                wf.add_dataset(ds)

            if e.__class__.__name__ == "ConfigureTask":
                task = wf.get_task(e.alias.name)
                if e.workflow:
                    task.add_sub_workflow_name(e.workflow.name)
                elif e.filename:
                    if not os.path.exists(e.filename):
                        raise dsl_exceptions.ImplementationFileNotFound(f"{e.filename} in task {e.alias.name}")
                    task.add_implementation_file(e.filename)
                if e.dependency:
                    task.input_files.append(e.dependency)

            if e.__class__.__name__ == "ConfigureData":
                ds = wf.get_dataset(e.alias.name)
                ds.add_path(e.path)

            if e.__class__.__name__ == "StartAndEndEvent":
                process_dependencies(task_dependencies, e.nodes, "StartAndEndEvent")

            if e.__class__.__name__ == "StartEvent":
                process_dependencies(task_dependencies, e.nodes, "StartEvent")

            if e.__class__.__name__ == "EndEvent":
                process_dependencies(task_dependencies, e.nodes, "EndEvent")

            if e.__class__.__name__ == "TaskLink":
                process_dependencies(task_dependencies, [e.initial_node] + e.nodes, "TaskLink")

            if e.__class__.__name__ == "DataLink":
                add_input_output_data(wf, [e.initial] + e.rest)

            if e.__class__.__name__ == "ConditionLink":
                condition = e.condition
                fromNode = e.from_node
                ifNode = e.if_node
                elseNode = e.else_node
                contNode = e.continuation_Node

                conditional_task = wf.get_task(e.from_node.name)
                conditional_task.set_conditional_tasks(ifNode.name, elseNode.name, contNode.name, condition)

for wf in parsed_workflows:
            wf.print()

assembled_workflows_data = []
for component in no_events_workflow_model.component:
    if component.__class__.__name__ == 'AssembledWorkflow':
        print("*********************************************************")
        print("********** PARSE ASSEMBLED WORKFLOWS DATA ***************")
        print("*********************************************************")

        assembled_workflow_data = {}
        assembled_workflows_data.append(assembled_workflow_data)
        assembled_workflow_data["name"] = component.name
        assembled_workflow_data["parent"] = component.parent_workflow.name
        assembled_workflow_tasks = {}
        assembled_workflow_data["tasks"] = assembled_workflow_tasks

        configurations = component.tasks

        while configurations:
            for config in component.tasks:
                assembled_workflow_task = {}
                if config.workflow:
                    assembled_workflow_task["workflow"] = config.workflow
                    assembled_workflow_tasks[config.alias.name] = assembled_workflow_task
                elif config.filename:
                    if not os.path.exists(config.filename):
                        raise dsl_exceptions.ImplementationFileNotFound(f"{config.filename} in task {config.alias.name}")
                    assembled_workflow_task["implementation"] = config.filename
                    assembled_workflow_tasks[config.alias.name] = assembled_workflow_task
                configurations.remove(config)
                configurations += config.subtasks

import pprint
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(assembled_workflows_data)


print("*********************************************************")
print("************ GENERATE ASSEMBLED WORKFLOWS ***************")
print("*********************************************************")

assembled_wfs = generate_final_assembled_workflows(parsed_workflows, assembled_workflows_data)

print("************")
for wf in assembled_wfs:
    wf.print()

print("************")

printexperiments = []
for component in no_events_workflow_model.component:
    if component.__class__.__name__ == 'Experiment':
        # experiments.append(component.name)
        print("Experiment name: ", component.name)
        print("Experiment intent: ", component.intent_name)

        for node in component.experimentNode:
            if node.__class__.__name__ == 'Event':
                print(f"Event: {node.name}")
                print(f"    Type: {node.eventType}")
                if node.condition:
                    print(f"    Condition: {node.condition}")
                print(f"    Task: {node.validation_task}")
                if node.restart:
                    print(f"    Restart: {node.restart}")
                print()

            elif node.__class__.__name__ == 'SpaceConfig':
                print(f"  Space: {node.name}")
                print(f"    Assembled Workflow: {node.assembled_workflow.name}")
                print(f"    Strategy: {node.strategy_name}")
                if node.vps:
                    for vp in node.vps:
                        print(f"    VP: {vp.vp_name} = ", end="")
                        vp_values = vp.vp_values
                        if hasattr(vp_values, 'values'):
                            values = ", ".join(str(v) for v in vp_values.values)
                            print(f"enum({values});")
                        elif hasattr(vp_values, 'min') and hasattr(vp_values, 'max'):
                            if hasattr(vp_values, 'step'):
                                print(f"range({vp_values.min}, {vp_values.max}, {vp_values.step});")
                            else:
                                print(f"range({vp_values.min}, {vp_values.max});")
                if node.tasks:
                    for task in node.tasks:
                        print(f"    Task: {task.task.name}")
                        if task.config:
                            for config in task.config:
                                print(f"    Param: {config.param_name} = {config.vp}")
                        print()

        if component.control:
            print("Control exists")
            for control in component.control:
                for explink in control.explink:
                    if explink.__class__.__name__ == 'RegularExpLink':
                        link = f"  Regular Link: {explink.initial_space.name}"
                        for space in explink.spaces:
                            link += f" -> {space.name}"
                        print(link)


                    elif explink.__class__.__name__ == 'ConditionalExpLink':
                        line = f"  Conditional Link: {explink.fromspace.name}"
                        line += f" ?-> {explink.tospace.name}"
                        line += f"  Condition: {explink.condition}"
                        print(line)




