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
automated_events = set()
manual_events = set()
for component in no_events_workflow_model.component:
    if component.__class__.__name__ == 'Experiment':
        # experiments.append(component.name)
        print("Experiment name: ", component.name)
        print("Experiment intent: ", component.intent_name)

        for node in component.experimentNode:
            if node.__class__.__name__ == 'Event':
                print(f"Event: {node.name}")
                print(f"    Type: {node.eventType}")
                if node.eventType == 'automated':
                    automated_events.add(node.name)
                if node.eventType == 'manual':
                    manual_events.add(node.name)
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

                if node.tasks:
                    for task_config in node.tasks:
                        print(f"    Task: {task_config.task.name}")
                        for param_config in task_config.config:
                            print(f"        Param: {param_config.param_name} = {param_config.vp}")
                if node.vps:
                    for vp in node.vps:
                        if hasattr(vp.vp_values, 'values'):
                            print(f"        {vp.vp_name} = enum{vp.vp_values.values};")

                        elif hasattr(vp.vp_values, 'minimum') and hasattr(vp.vp_values, 'maximum'):
                            min_value = vp.vp_values.minimum
                            max_value = vp.vp_values.maximum
                            step_value = getattr(vp.vp_values, 'step', None)
                            if step_value is not None:
                                print(f"        {vp.vp_name} = range({min_value}, {max_value}, {step_value});")
                            else:
                                print(f"        {vp.vp_name} = range({min_value}, {max_value});")

                print()

        if component.control:
                print("Control exists")
                # for control in component.control:
                #     for explink in control.explink:
                #         if explink.__class__.__name__ == 'RegularExpLink':
                #             link = f"  Regular Link: {explink.initial_space.name}"
                #             for space in explink.spaces:
                #                 link += f" -> {space.name}"
                #             print(link)
                #
                #
                #         elif explink.__class__.__name__ == 'ConditionalExpLink':
                #             line = f"  Conditional Link: {explink.fromspace.name}"
                #             line += f" ?-> {explink.tospace.name}"
                #             line += f"  Condition: {explink.condition}"
                #             print(line)
                print('------------------------------------------')
                print("Automated Events")
                for control in component.control:
                    for explink in control.explink:
                        if explink.__class__.__name__ == 'RegularExpLink':
                            if explink.initial_space.name in automated_events or any(space.name in automated_events for space in explink.spaces):
                                for event in automated_events:
                                    if event in explink.initial_space.name or any(event in space.name for space in explink.spaces):
                                        print()
                                        print(f"Event: {event}")
                                        link = f"  Regular Link: {explink.initial_space.name}"
                                        for space in explink.spaces:
                                            link += f" -> {space.name}"
                                        print(link)

                        elif explink.__class__.__name__ == 'ConditionalExpLink':
                            if explink.fromspace.name in automated_events or explink.tospace.name in automated_events:
                                line = f"  Conditional Link: {explink.fromspace.name}"
                                line += f" ?-> {explink.tospace.name}"
                                line += f"  Condition: {explink.condition}"
                                print(line)



                print('------------------------------------------')
                print("Manual Events")
                for control in component.control:
                    for explink in control.explink:
                        if explink.__class__.__name__ == 'RegularExpLink':
                            if explink.initial_space.name in manual_events or any(space.name in manual_events for space in explink.spaces):
                                for event in manual_events:
                                    if event in explink.initial_space.name or any(
                                            event in space.name for space in explink.spaces):
                                        print()
                                        print(f"Event: {event}")
                                        link = f"  Regular Link: {explink.initial_space.name}"
                                        for space in explink.spaces:
                                            link += f" -> {space.name}"
                                        print(link)

                        elif explink.__class__.__name__ == 'ConditionalExpLink':
                            if explink.fromspace.name in manual_events or explink.tospace.name in manual_events:
                                line = f"  Conditional Link: {explink.fromspace.name}"
                                line += f" ?-> {explink.tospace.name}"
                                line += f"  Condition: {explink.condition}"
                                print(line)

                print('------------------------------------------')