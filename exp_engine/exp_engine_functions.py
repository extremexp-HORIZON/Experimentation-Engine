import exp_engine_classes as classes
from data_abstraction_layer.data_abstraction_api import *
import proactive_executionware.proactive_runner as proactive_runner
import exp_engine_exceptions
import os
import textx
import itertools
import random
import pprint


EXPERIMENTS_FOLDER = 'IDEKO-experiment1/'
EXECUTIONWARE = "PROACTIVE"

assembled_flat_wfs = []
printexperiments = []
nodes = set()
automated_events = set()
manual_events = set()
spaces = set()
space_configs = []
automated_dict = {}
manual_dict = {}
parsed_manual_events = []
parsed_automated_events = []
workflows_to_run = {}
workflow_combinations_to_run = {}

results = {}

def process_dependencies(task_dependencies, nodes, parsing_node_type, verbose_logging=False):
    if verbose_logging:
        print(parsing_node_type)
    for n1, n2 in zip(nodes[0::1], nodes[1::1]):
        if verbose_logging:
            print(str(n2.name), ' depends on ', str(n1))
        if n2.name in task_dependencies:
            print(f"{parsing_node_type}: Double dependency ({n2.name}), check your specification")
            # exit(0)
        else:
            # TODO what about tasks with multiple dependencies?
            task_dependencies[n2.name] = [n1.name]


def add_input_output_data(wf, nodes):
    for n1, n2 in zip(nodes[0::1], nodes[1::1]):
        if n1.__class__.__name__ == "DefineTask":
            ds = wf.get_dataset(n2.name)
            wf.get_task(n1.name).output_files.append(ds)
        if n1.__class__.__name__ == "Data":
            ds = wf.get_dataset(n1.name)
            wf.get_task(n2.name).input_files.append(ds)


def apply_task_dependencies_and_set_order(wf, task_dependencies):
    for t in wf.tasks:
        if t.name in task_dependencies.keys():
            t.add_dependencies(task_dependencies[t.name])
    re_order_tasks_in_workflow(wf)


def re_order_tasks_in_workflow(wf):
    first_task = [t for t in wf.tasks if not t.dependencies][0]
    order = 0
    first_task.set_order(order)
    dependent_tasks = [t for t in wf.tasks if first_task.name in t.dependencies]
    while dependent_tasks:
        order += 1
        new_dependent_tasks = []
        for dependent_task in dependent_tasks:
            dependent_task.set_order(order)
            new_dependent_tasks += [t for t in wf.tasks if dependent_task.name in t.dependencies]
        dependent_tasks = new_dependent_tasks


def find_dependent_tasks(wf, task, dependent_tasks):
    for t in wf.tasks:
        if task.name in t.dependencies:
            dependent_tasks.append(t)
        if t.sub_workflow:
            find_dependent_tasks(t.sub_workflow, task, dependent_tasks)
    return dependent_tasks


def exists_parent_workflow(wfs, wf_name):
    for wf in wfs:
        if wf_name in [task.sub_workflow.name for task in wf.tasks if task.sub_workflow]:
            return True
    return False


def set_is_main_attribute(wfs):
    for wf in wfs:
        wf.set_is_main(not exists_parent_workflow(wfs, wf.name))


def get_underlying_tasks(t, assembled_wf, tasks_to_add):
    i = 0
    for task in sorted(t.sub_workflow.tasks, key=lambda t: t.order):
        if not task.sub_workflow:
            if i==0:
                task.add_dependencies(t.dependencies)
            if i==len(t.sub_workflow.tasks)-1:
                dependent_tasks = find_dependent_tasks(assembled_wf, t, [])
                dep = [t.name for t in dependent_tasks]
                print(f"{t.name} --> {dep} becomes {task.name} --> {dep}")
                for dependent_task in dependent_tasks:
                    dependent_task.remove_dependency(t.name)
                    dependent_task.add_dependencies([task.name])
            tasks_to_add.append(task)
        else:
            get_underlying_tasks(task, assembled_wf, tasks_to_add)
        i += 1
    return tasks_to_add


def flatten_workflows(assembled_wf):
    print(f"Flattening assembled workflow with name {assembled_wf.name}")
    new_wf = classes.Workflow(assembled_wf.name)
    for t in assembled_wf.tasks:
        if t.sub_workflow:
            print (t.sub_workflow.name)
            tasks_to_add = get_underlying_tasks(t, assembled_wf, [])
            for t in tasks_to_add:
                new_wf.add_task(t)
        else:
            new_wf.add_task(t)
    re_order_tasks_in_workflow(new_wf)
    new_wf.set_is_main(True)
    return new_wf


def configure_wf(workflow, assembled_wf_data):
    print(workflow.name)
    for task in workflow.tasks:
        if task.name in assembled_wf_data["tasks"].keys():
            print(f"Need to configure task '{task.name}'")
            task_data = assembled_wf_data["tasks"][task.name]
            if "implementation" in task_data:
                print(f"Changing implementation of task '{task.name}' to '{task_data['implementation']}'")
                task.add_implementation_file(task_data["implementation"])
        else:
            print(f"Do not need to configure task '{task.name}'")
        if task.sub_workflow:
            configure_wf(task.sub_workflow, assembled_wf_data)


def generate_final_assembled_workflows(parsed_workflows, assembled_wfs_data):
    new_wfs = []
    for assembled_wf_data in assembled_wfs_data:
        wf = next(w for w in parsed_workflows if w.name == assembled_wf_data["parent"]).clone(parsed_workflows)
        wf.name = assembled_wf_data["name"]
        new_wfs.append(wf)
        print(wf.name)
        for task in wf.tasks:
            if task.name in assembled_wf_data["tasks"].keys():
                print(f"Need to configure task '{task.name}'")
                task_data = assembled_wf_data["tasks"][task.name]
                if "implementation" in task_data:
                    print(f"Changing implementation of task '{task.name}' to '{task_data['implementation']}'")
                    task.add_implementation_file(task_data["implementation"])
                if "dependency" in task_data:
                    print(f"Changing dependency of task '{task.name}' to '{task_data['dependency']}'")
                    task.add_dependent_module(task_data["dependency"])
            else:
                print(f"Do not need to configure task '{task.name}'")
            if task.sub_workflow:
                configure_wf(task.sub_workflow, assembled_wf_data)
        print("-------------------------------")
    return new_wfs


def generate_assembled_flast_workflows(assembled_wfs):

    for wf in assembled_wfs:
        flat_wf = flatten_workflows(wf)
        assembled_flat_wfs.append(flat_wf)
        flat_wf.print()

def execute_wf(w, executionware):
    if executionware == "PROACTIVE":
        return proactive_runner.execute_wf(w)


def get_task_implementation_path(implementation):
    task_library_path = 'IDEKO-task-library'
    experiment1_path = 'IDEKO-experiment1'
    mltask_library_path = 'extremexp-mltask-library'
    parts = implementation.split('.')
    # print(implementation)
    if parts[0] == 'IDEKO-experiment1':
        return os.path.join(experiment1_path, parts[1] + '.xxp'), "composite"
    if parts[0] == 'IDEKO-task-library':
        folder_path = os.path.join(task_library_path, parts[1])
        return parse_task(folder_path),"simple"
    if parts[0] == 'extremexp-mltask-library':
        folder_path = os.path.join(mltask_library_path, parts[1])
        return parse_task(folder_path), "simple"
    else:
        return None, None

def parse_task(folder_path):
    file_path = os.path.join(folder_path, 'task.xxp')
    with open(file_path, 'r') as task_file:
        task_dsl= task_file.read()
    workflow_metamodel = textx.metamodel_from_file('IDEKO-experiment1/task_grammar.tx')
    workflow_model = workflow_metamodel.model_from_str(task_dsl)
    for component in workflow_model.component:
        for e in component.elements:
            if e.__class__.__name__ == "Implementation":
                if e.filename:
                    if not os.path.exists(e.filename):
                        raise exp_engine_exceptions.ImplementationFileNotFound(f"{e.filename}")
                return e.filename


def get_workflow_components(experiments_metamodel, experiment_model, parsed_workflows, task_dependencies):
    for component in experiment_model.component:
        if component.__class__.__name__ == 'Workflow':
            wf = classes.Workflow(component.name)

            parsed_workflows.append(wf)

            for e in component.elements:
                if e.__class__.__name__ == "DefineTask":
                    task = classes.WorkflowTask(e.name)
                    wf.add_task(task)

                if e.__class__.__name__ == "Data":
                    ds = classes.WorkflowDataset(e.name)
                    wf.add_dataset(ds)

                if e.__class__.__name__ == "ConfigureTask":
                    task = wf.get_task(e.alias.name)
                    # if e.workflow:
                    #     task.add_sub_workflow_name(e.workflow.name)
                    if e.filename:
                        implementation = e.filename
                        task_file_path, task_type = get_task_implementation_path(implementation)
                        if not os.path.exists(task_file_path):
                            raise exp_engine_exceptions.ImplementationFileNotFound(
                                f"{task_file_path} in task {e.alias.name}")
                        if task_type == "composite":
                            with open(task_file_path) as file:
                                workflow_specification = file.read()
                                # print(workflow_specification)
                                subworkflow_model = experiments_metamodel.model_from_str(workflow_specification)
                                sub_wf, parsed_workflows, task_dependencies = get_workflow_components(experiments_metamodel,subworkflow_model,parsed_workflows,task_dependencies)
                                task.add_sub_workflow(sub_wf)
                                task.add_sub_workflow_name(sub_wf.name)
                        else:
                            task.add_implementation_file(task_file_path)
                    if e.dependency:
                        task.add_dependent_module(e.dependency)

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

    return wf, parsed_workflows, task_dependencies


def get_experiment_specification(workflow_specification):
    experiment_specifications = []
    experiments_metamodel = textx.metamodel_from_file('IDEKO-experiment1/workflow_grammar_new_v2.tx')
    workflow_model = experiments_metamodel.model_from_str(workflow_specification)


    for component in workflow_model.component:
        if component.__class__.__name__ == 'Workflow':
            for e in component.elements:
                if e.__class__.__name__ == "ConfigureTask":
                    if e.filename:
                        implementation = e.filename
                        # print(implementation)
                        parts = implementation.split('.')

                        if parts[0] == 'IDEKO-experiment1':
                            task_file_path = os.path.join('IDEKO-experiment1', parts[1] + '.xxp')
                        else:
                            task_file_path = None

                        if not os.path.exists(task_file_path):
                            raise exp_engine_exceptions.ImplementationFileNotFound(
                                f"{task_file_path} in task {e.alias.name}")
                        else:
                            with open(task_file_path, 'r') as file:
                                experiment_specification = file.read()
                                # print(experiment_specification)
                                experiment_specifications.append(experiment_specification)

    return experiment_specifications








def parse_workflows(experiment_specification):
    parsed_workflows = []
    task_dependencies = {}

    experiments_metamodel = textx.metamodel_from_file('IDEKO-experiment1/workflow_grammar_new_v2.tx')
    experiment_model = experiments_metamodel.model_from_str(experiment_specification)

    _, parsed_workflows, task_dependencies = get_workflow_components(experiments_metamodel, experiment_model, parsed_workflows, task_dependencies)

    for wf in parsed_workflows:
        apply_task_dependencies_and_set_order(wf, task_dependencies)

    set_is_main_attribute(parsed_workflows)

    for wf in parsed_workflows:
        wf.print()

    return parsed_workflows, task_dependencies


def parse_assembled_workflow_data(experiment_specification):
    experiments_metamodel = textx.metamodel_from_file('IDEKO-experiment1/workflow_grammar_new_v2.tx')
    experiment_model = experiments_metamodel.model_from_str(experiment_specification)

    assembled_workflows_data = []
    for component in experiment_model.component:
        if component.__class__.__name__ == 'AssembledWorkflow':
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
                        implementation = config.filename
                        task_file_path, _ = get_task_implementation_path(implementation)
                        if not os.path.exists(task_file_path):
                            raise exp_engine_exceptions.ImplementationFileNotFound(
                                f"{task_file_path} in task {config.alias.name}")
                        assembled_workflow_task["implementation"] = task_file_path
                        assembled_workflow_tasks[config.alias.name] = assembled_workflow_task
                    if config.dependency:
                        assembled_workflow_task["dependency"] = config.dependency
                    configurations.remove(config)
                    configurations += config.subtasks

    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(assembled_workflows_data)

    return assembled_workflows_data



def generate_experiment_specification(experiment_specification):
    experiments_metamodel = textx.metamodel_from_file('IDEKO-experiment1/workflow_grammar_new_v2.tx')
    experiment_model = experiments_metamodel.model_from_str(experiment_specification)

    for component in experiment_model.component:
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
                        parsed_event = classes.AutomatedEvent(node.name, node.validation_task, node.condition)
                        parsed_automated_events.append(parsed_event)

                    if node.eventType == 'manual':
                        manual_events.add(node.name)
                        parsed_event = classes.ManualEvent(node.name, node.validation_task, node.restart)
                        parsed_manual_events.append(parsed_event)

                    if node.condition:
                        print(f"    Condition: {node.condition}")
                    print(f"    Task: {node.validation_task}")
                    if node.restart:
                        print(f"    Restart: {node.restart}")
                    print()

                elif node.__class__.__name__ == 'SpaceConfig':
                    print(f"  Space: {node.name}")
                    print(f"    Assembled Workflow: {node.assembled_workflow.name}")
                    print(f"    Vairbality : {node.strategy_name}")

                    spaces.add(node.name)

                    space_config_data = {
                        "name": node.name,
                        "assembled_workflow": node.assembled_workflow.name,
                        "strategy": node.strategy_name,
                        "tasks": {},
                        "VPs": [],
                        "runs": node.runs
                    }

                    if node.tasks:
                        for task_config in node.tasks:
                            print(f"    Task: {task_config.task.name}")
                            task_name = task_config.task.name
                            task_data = {}

                            for param_config in task_config.config:
                                print(f"        Param: {param_config.param_name} = {param_config.vp}")
                                param_name = param_config.param_name
                                param_vp = param_config.vp

                                task_data[param_name] = param_vp

                            space_config_data["tasks"][task_name] = task_data

                    if node.vps:
                        for vp in node.vps:
                            if hasattr(vp.vp_values, 'values'):
                                print(f"        {vp.vp_name} = enum{vp.vp_values.values};")
                                vp_data = {
                                    "name": vp.vp_name,
                                    "values": vp.vp_values.values,
                                    "type": "enum"
                                }
                                space_config_data["VPs"].append(vp_data)

                            elif hasattr(vp.vp_values, 'minimum') and hasattr(vp.vp_values, 'maximum'):
                                min_value = vp.vp_values.minimum
                                max_value = vp.vp_values.maximum
                                step_value = getattr(vp.vp_values, 'step', 1)
                                print(f"        {vp.vp_name} = range({min_value}, {max_value}, {step_value});")

                                vp_data = {
                                    "name": vp.vp_name,
                                    "min": min_value,
                                    "max": max_value,
                                    "step": step_value,
                                    "type": "range"
                                }
                                space_config_data["VPs"].append(vp_data)

                    if (node.runs != 0):
                        print(f"        Runs: ", {node.runs})

                    space_configs.append(space_config_data)

                print()

            nodes = automated_events | manual_events | spaces

            if component.control:
                print("Control exists")
                print('------------------------------------------')
                print("Automated Events")
                for control in component.control:
                    for explink in control.explink:
                        if explink.__class__.__name__ == 'RegularExpLink':
                            if explink.initial_space and explink.spaces:
                                initial_space_name = explink.initial_space.name

                                if any(event in initial_space_name or any(
                                        event in space.name for space in explink.spaces) for event in automated_events):
                                    for event in automated_events:
                                        if event in initial_space_name or any(
                                                event in space.name for space in explink.spaces):
                                            print(f"Event: {event}")
                                            link = f"  Regular Link: {initial_space_name}"
                                            for space in explink.spaces:
                                                link += f" -> {space.name}"
                                                # if space.name in nodes:
                                                #     nodes.remove(space.name)
                                            print(link)

                                if initial_space_name not in automated_dict:
                                    automated_dict[initial_space_name] = {}

                                for space in explink.spaces:
                                    if space is not None:
                                        automated_dict[initial_space_name]["True"] = space.name
                                        if space.name in nodes:
                                            nodes.remove(space.name)


                        elif explink.__class__.__name__ == 'ConditionalExpLink':
                            if explink.fromspace and explink.tospace:
                                if any(event in explink.fromspace.name or event in explink.tospace.name for event in
                                       automated_events):
                                    line = f"  Conditional Link: {explink.fromspace.name}"
                                    line += f" ?-> {explink.tospace.name}"
                                    line += f"  Condition: {explink.condition}"
                                    print(line)

                                    if explink.tospace.name in nodes:
                                        nodes.remove(explink.tospace.name)

                                if explink.fromspace.name not in automated_dict:
                                    automated_dict[explink.fromspace.name] = {}

                                automated_dict[explink.fromspace.name][explink.condition] = explink.tospace.name

                        # if explink.initial_space.name in automated_events or any(space.name in automated_events for space in explink.spaces):
                        #     for event in automated_events:
                        #         if event in explink.initial_space.name or any(event in space.name for space in explink.spaces):
                        #             print()
                        #             print(f"Event: {event}")
                        #             link = f"  Regular Link: {explink.initial_space.name}"
                        #             for space in explink.spaces:
                        #                 link += f" -> {space.name}"
                        #             print(link)
                        #
                        #             automated_queue.append(explink.initial_space.name)
                        #             for space in explink.spaces:
                        #                 automated_queue.append(space.name)

                print('------------------------------------------')
                print("Manual Events")
                for control in component.control:
                    for explink in control.explink:
                        if explink.__class__.__name__ == 'RegularExpLink':
                            if explink.initial_space and explink.spaces:
                                initial_space_name = explink.initial_space.name
                                if initial_space_name == "START":
                                    initial_space_name = explink.start.name

                                if any(event in initial_space_name or any(
                                        event in space.name for space in explink.spaces) for event in manual_events):
                                    for event in manual_events:
                                        if event in initial_space_name or any(
                                                event in space.name for space in explink.spaces):
                                            print(f"Event: {event}")
                                            link = f"  Regular Link: {initial_space_name}"
                                            for space in explink.spaces:
                                                link += f" -> {space.name}"
                                            print(link)

                                if initial_space_name not in manual_dict:
                                    manual_dict[initial_space_name] = {}

                                for space in explink.spaces:
                                    if space is not None:
                                        manual_dict[initial_space_name]["True"] = space.name

                        elif explink.__class__.__name__ == 'ConditionalExpLink':
                            if explink.fromspace and explink.tospace:
                                if any(event in explink.fromspace.name or event in explink.tospace.name for event in
                                       manual_events):
                                    line = f"  Conditional Link: {explink.fromspace.name}"
                                    line += f" ?-> {explink.tospace.name}"
                                    line += f"  Condition: {explink.condition}"
                                    print(line)

                                if explink.fromspace.name not in manual_dict:
                                    manual_dict[explink.fromspace.name] = {}

                                manual_dict[explink.fromspace.name][explink.condition] = explink.tospace.name
                print('------------------------------------------')

    # print("Nodes: ",nodes)
    # print("Automated Events:", automated_events)
    # print("Manual Events",manual_events)
    # print("Spaces: ", spaces)

    # print("Spaces Config: ")
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(space_configs)
    # #
    # print("Automated Dictionary:")
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(automated_dict)
    #
    # print("Manual Dictionary:")
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(manual_dict)

    # print("Parsed Automated Events")
    # for e in parsed_automated_events:
    #     print(e.name)
    #     print()
    #
    # print("Parsed Manual Events")
    # for e in parsed_manual_events:
    #     print(e.name)
    #     print()

    #
    # for space_config in space_configs:
    #     pp.pprint(space_config)
    #     print()
    #

    return  nodes, automated_dict


def execute_automated_event(node):
    print("executing automated event")
    e = next((e for e in parsed_automated_events if e.name == node), None)

    print(e.task)

    module = __import__('IDEKO_events')
    func = getattr(module, e.task)
    ret = func(results)
    print("--------------------------------------------------------------------")
    return ret

def execute_manual_event(node):
    print("executing manual event")
    e = next((e for e in parsed_manual_events if e.name == node), None)

    # print(e.task)

    module = __import__('IDEKO_events')
    func = getattr(module, e.task)
    ret = func(automated_dict,space_configs,e.name)
    print("--------------------------------------------------------------------")
    return ret


def execute_space(node, exp_id):
    print("executing space")

    space_config = next((s for s in space_configs if s['name'] == node), None)
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(space_config)
    print('-------------------------------------------------------------------')
    print(f"Running experiment of espace '{space_config['name']}' of type '{space_config['strategy']}'")
    method_type = space_config["strategy"]

    if method_type == "gridsearch":
        run_grid_search(space_config, exp_id)

    if method_type == "randomsearch":
        run_random_search(space_config, exp_id)

    print("node executed")
    print("Results so far")
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(results)

    return 'True'


def run_scheduled_workflows(space_results, exp_id):
    exp = get_experiment(exp_id)
    workflows_count = len(exp["workflowIds"])

    for attempts in range(workflows_count):
        wf_ids = get_experiment(exp_id)["workflowIds"]
        run_count = 1
        for wf_id in wf_ids:
            workflow_to_run = workflows_to_run[wf_id]
            if get_workflow(wf_id)["status"] != "completed":
                update_workflow(wf_id, {"status": "running"})
                result = execute_wf(workflow_to_run, EXECUTIONWARE)
                update_workflow(wf_id, {"status": "completed"})
                workflow_results = {}
                workflow_results["configuration"] = workflow_combinations_to_run[wf_id]
                workflow_results["result"] = result
                space_results[run_count] = workflow_results
            # TODO fix this count in case of reordering
            run_count += 1


def get_workflow_to_run(space_config, c):
    c_dict = dict(c)
    w = next(w for w in assembled_flat_wfs if w.name == space_config["assembled_workflow"])
    for t in w.tasks:
        if t.name in space_config["tasks"].keys():
            task_config = space_config["tasks"][t.name]
            for param_name, param_vp in task_config.items():
                alias = param_vp
                print(f"Setting param '{param_name}' of task '{t.name}' to '{c_dict[alias]}'")
                t.set_param(param_name, c_dict[alias])
    return w


def create_executed_workflow_in_db(exp_id, run_count, workflow_to_run):
    task_specifications = []
    for t in sorted(workflow_to_run.tasks, key=lambda t: t.order):
        t_spec = {}
        task_specifications.append(t_spec)
        t_spec["id"] = t.name
        t_spec["name"] = t.name
        t_spec["source_code"] = t.impl_file
        if len(t.params) > 0:
            params = []
            t_spec["parameters"] = params
            for name in t.params:
                param = {}
                params.append(param)
                value = t.params[name]
                param["name"] = name
                param["value"] = str(value)
                if type(value) is int:
                    param["type"] = "integer"
                else:
                    param["type"] = "string"
        if len(t.input_files) > 0:
            input_datasets = []
            t_spec["input_datasets"] = input_datasets
            for f in t.input_files:
                input_file = {}
                input_datasets.append(input_file)
                input_file["name"] = f.name
                input_file["uri"] = f.path
    body = {
        "name": f"{exp_id}--w{run_count}",
        "executedTasks": task_specifications
    }
    wf_id = create_workflow(exp_id, body)
    return wf_id


def run_grid_search(space_config, exp_id):
    grid_search_combinations = []
    VPs = space_config["VPs"]
    vp_combinations = []

    for vp_data in VPs:
        if vp_data["type"] == "enum":
            vp_name = vp_data["name"]
            vp_values = vp_data["values"]
            vp_combinations.append([(vp_name, value) for value in vp_values])

        elif vp_data["type"] == "range":
            vp_name = vp_data["name"]
            min_value = vp_data["min"]
            max_value = vp_data["max"]
            step_value = vp_data.get("step", 1) if vp_data["step"] != 0 else 1
            vp_values = list(range(min_value, max_value + 1, step_value))
            vp_combinations.append([(vp_name, value) for value in vp_values])

    # Generate combinations
    combinations = list(itertools.product(*vp_combinations))
    grid_search_combinations.extend(combinations)

    print(f"\nGrid search generated {len(combinations)} configurations to run.\n")
    for combination in combinations:
        print(combination)

    run_count = 1
    for c in combinations:
        print(f"Run {run_count}")
        workflow_to_run = get_workflow_to_run(space_config, c)
        wf_id = create_executed_workflow_in_db(exp_id, run_count, workflow_to_run)
        workflows_to_run[wf_id] = workflow_to_run
        workflow_combinations_to_run[wf_id] = c
        run_count += 1

    space_results = {}
    results[space_config['name']] = space_results
    run_scheduled_workflows(space_results, exp_id)


def  run_random_search(space_config, exp_id):
    random_combinations = []

    vps = space_config['VPs']
    runs = space_config['runs']

    for i in range(runs):
        combination = []
        for vp in vps:
            vp_name = vp['name']
            min_val = vp['min']
            max_val = vp['max']

            value = random.randint(min_val, max_val)

            combination.append((vp_name, value))

        random_combinations.append(tuple(combination))

    print(f"\nRandom search generated {len(random_combinations)} configurations to run.\n")
    for c in random_combinations:
        print(c)

    run_count = 1
    space_results = {}
    results[space_config['name']] = space_results
    for c in random_combinations:
        print(f"Run {run_count}")
        workflow_to_run = get_workflow_to_run(space_config, c)
        result = execute_wf(workflow_to_run, EXECUTIONWARE)
        workflow_results = {}
        workflow_results["configuration"] = c
        workflow_results["result"] = result
        space_results[run_count] = workflow_results
        print("..........")
        run_count += 1

def execute_node(node, exp_id):
    print(node)

    if node in spaces:
        return execute_space(node, exp_id)

    elif node in automated_events:
        return  execute_automated_event(node)

    elif node in manual_events:
        return execute_manual_event(node)


def find_start_node(nodes, automated_dict):
    values = automated_dict.values()
    if len(values) == 0:
        # if the control is trivial, just pick the first node
        return list(nodes)[0]
    for n in automated_dict:
        if n not in values:
            return n


def run_workflow(nodes, automated_dict, exp_id):
    start_node = find_start_node(nodes, automated_dict)
    print("Nodes: ", nodes)
    print("Start Node: ", start_node)

    node = start_node
    result = execute_node(node, exp_id)
    while node in automated_dict:
        next_action = automated_dict[node]
        node = next_action[result]
        result = execute_node(node, exp_id)


def run_experiment(experiment_specification, exp_id):

    print("*********************************************************")
    print("***************** PARSE WORKFLOWS ***********************")
    print("*********************************************************")
    parsed_workflows, task_dependencies = parse_workflows(experiment_specification)

    print("*********************************************************")
    print("********** PARSE ASSEMBLED WORKFLOWS DATA ***************")
    print("*********************************************************")
    assembled_workflows_data = parse_assembled_workflow_data(experiment_specification)

    print("*********************************************************")
    print("************ GENERATE ASSEMBLED WORKFLOWS ***************")
    print("*********************************************************")
    assembled_wfs = generate_final_assembled_workflows(parsed_workflows, assembled_workflows_data)
    for wf in assembled_wfs:
        wf.print()

    print("*********************************************************")
    print("********** GENERATE ASSEMBLED FLAT WORKFLOWS ************")
    print("*********************************************************")
    generate_assembled_flast_workflows(assembled_wfs)

    print("*********************************************************")
    print("************** EXPERIMENT SPECIFICATION *****************")
    print("*********************************************************")
    nodes, automated_dict = generate_experiment_specification(experiment_specification)

    print("\n*********************************************************")
    print("***************** RUNNING WORKFLOWS ***********************")
    print("*********************************************************")
    run_workflow(nodes, automated_dict, exp_id)





