import textx
from itertools import product
import random
import streamlit as st
from classes import *

def process_dependencies(task_dependencies, nodes, parsing_node_type, verbose_logging=False):
    if verbose_logging:
        st.write(parsing_node_type)
    for n1, n2 in zip(nodes[0::1], nodes[1::1]):
        if verbose_logging:
            st.write(str(n2.name), ' depends on ', str(n1))
        if n2.name in task_dependencies:
            st.write(f"{parsing_node_type}: Double dependency ({n2.name}), check your specification")
            exit(0)
        else:
            # TODO what about tasks with multiple dependencies?
            task_dependencies[n2.name] = [n1.name]


def add_input_output_data(wf, nodes):
    for n1, n2 in zip(nodes[0::1], nodes[1::1]):
        if n1.__class__.__name__ == "DefineTask":
            wf.get_task(n1.name).output_files.append(n2.name)
        if n1.__class__.__name__ == "Data":
            wf.get_task(n2.name).input_files.append(n1.name)


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
                st.write(f"{t.name} --> {dep} becomes {task.name} --> {dep}")
                for dependent_task in dependent_tasks:
                    dependent_task.remove_dependency(t.name)
                    dependent_task.add_dependencies([task.name])
            tasks_to_add.append(task)
        else:
            get_underlying_tasks(task, assembled_wf, tasks_to_add)
        i += 1
    return tasks_to_add


def flatten_workflows(assembled_wf):
    st.write(f"Flattening assembled workflow with name {assembled_wf.name}")
    new_wf = Workflow(assembled_wf.name)
    for t in assembled_wf.tasks:
        if t.sub_workflow:
            tasks_to_add = get_underlying_tasks(t, assembled_wf, [])
            for t in tasks_to_add:
                new_wf.add_task(t)
        else:
            new_wf.add_task(t)
    re_order_tasks_in_workflow(new_wf)
    new_wf.set_is_main(True)
    return new_wf


def configure_wf(workflow, assembled_wf_data):
    st.write(workflow.name)
    for task in workflow.tasks:
        if task.name in assembled_wf_data["tasks"].keys():
            st.write(f"Need to configure task '{task.name}'")
            task_data = assembled_wf_data["tasks"][task.name]
            if "implementation" in task_data:
                st.write(f"Changing implementation of task '{task.name}' to '{task_data['implementation']}'")
                task.add_implementation_file(task_data["implementation"])
        else:
            st.write(f"Do not need to configure task '{task.name}'")
        if task.sub_workflow:
            configure_wf(task.sub_workflow, assembled_wf_data)


def generate_final_assembled_workflows(wfs, assembled_wfs_data):
    new_wfs = []
    for assembled_wf_data in assembled_wfs_data:
        wf = next(w for w in wfs if w.name == assembled_wf_data["parent"]).clone(wfs)
        wf.name = assembled_wf_data["name"]
        new_wfs.append(wf)
        st.write(wf.name)
        for task in wf.tasks:
            if task.name in assembled_wf_data["tasks"].keys():
                st.write(f"Need to configure task '{task.name}'")
                task_data = assembled_wf_data["tasks"][task.name]
                if "implementation" in task_data:
                    st.write(f"Changing implementation of task '{task.name}' to '{task_data['implementation']}'")
                    task.add_implementation_file(task_data["implementation"])
            else:
                st.write(f"Do not need to configure task '{task.name}'")
            if task.sub_workflow:
                configure_wf(task.sub_workflow, assembled_wf_data)
        st.write("-------------------------------")
    return new_wfs


def execute_wf(w):
    st.write(f"Executing workflow {w.name}")
    w.print()
    st.write(f"Finished executing workflow {w.name}")


def configure_final_workflow(assembled_flat_wfs,vp_method, c):
    w = next(w for w in assembled_flat_wfs if w.name == vp_method["assembled_workflow"])
    for t in w.tasks:
        if t.name in vp_method["tasks"].keys():
            task_config = vp_method["tasks"][t.name]
            for p in task_config.keys():
                alias = task_config[p]
                st.write(f"Setting param '{p}' of task '{t.name}' to '{c[alias]}'")
                t.set_param(p, c[alias])
    return w


def generate_parameter_combinations(parameters):
    param_names = parameters.keys()
    param_values = parameters.values()
    return [dict(zip(param_names, values)) for values in product(*param_values)]


def run_grid_search_exp(assembled_flat_wfs, vp_method):
    combinations = generate_parameter_combinations(vp_method["vps"])
    st.write(f"Grid search generated {len(combinations)} configurations to run.")
    st.write(combinations)
    run_count = 1
    for c in combinations:
        st.write(f"Run {run_count}")
        workflow_to_run = configure_final_workflow(assembled_flat_wfs,vp_method, c)
        execute_wf(workflow_to_run)
        st.write("..........")
        run_count += 1


def generate_random_config(vps):
    c = {}
    for key in vps.keys():
        param = vps[key]
        value = random.randint(param["min"], param["max"])
        c[key] = value
    return c


def run_random_search_exp(assembled_flat_wfs, vp_method):
    for i in range(vp_method["runs"]):
        st.write(f"Run {i+1}")
        c = generate_random_config(vp_method["vps"])
        workflow_to_run = configure_final_workflow(assembled_flat_wfs,vp_method, c)
        execute_wf(workflow_to_run)
        st.write("..........")


def run_experiment(assembled_flat_wfs,vp_method):
    st.write(f"Running experiment of espace '{vp_method['espace']}' of type '{vp_method['type']}'")
    method_type = vp_method["type"]
    if method_type == "gridsearch":
        run_grid_search_exp(assembled_flat_wfs,vp_method)
    if method_type == "randomsearch":
        run_random_search_exp(assembled_flat_wfs,vp_method)

def checkDSL(filepath):
    with open(filepath, 'r') as file:
        workflow_code = file.read()

    workflow_metamodel = textx.metamodel_from_file('workflow_grammar.tx')
    workflow_model = workflow_metamodel.model_from_str(workflow_code)

    return workflow_model

def print_parse_workflows(workflow_model):
    parsed_workflows = []
    for workflow in workflow_model.workflows:
        wf = Workflow(workflow.name)
        parsed_workflows.append(wf)

        task_dependencies = {}

        for e in workflow.elements:
            if e.__class__.__name__ == "DefineTask":
                task = WorkflowTask(e.name)
                wf.add_task(task)

            if e.__class__.__name__ == "ConfigureTask":
                task = wf.get_task(e.alias.name)
                if e.workflow:
                    task.add_sub_workflow_name(e.workflow.name)
                elif e.filename:
                    task = wf.get_task(e.alias.name)
                    task.add_implementation_file(e.filename)

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

        apply_task_dependencies_and_set_order(wf, task_dependencies)

    set_is_main_attribute(parsed_workflows)



    return parsed_workflows

def print_assembled_wf_data(workflow_model):

    assembled_workflows_data = []  # Initialize the list outside the loop

    for assembled_workflow in workflow_model.assembledWorkflows:
        assembled_workflow_data = {}
        assembled_workflow_data["name"] = assembled_workflow.name
        assembled_workflow_data["parent"] = assembled_workflow.parent_workflow.name
        assembled_workflow_tasks = {}
        assembled_workflow_data["tasks"] = assembled_workflow_tasks

        configurations = assembled_workflow.configure
        while configurations:
            for config in configurations:
                assembled_workflow_task = {}
                if config.workflow:
                    assembled_workflow_task["workflow"] = config.workflow
                elif config.filename:
                    assembled_workflow_task["implementation"] = config.filename
                assembled_workflow_tasks[config.alias.name] = assembled_workflow_task
                configurations.remove(config)
                configurations += config.subtasks

        assembled_workflows_data.append(assembled_workflow_data)

    return assembled_workflows_data

def generate_assembled_workflows(parsed_workflows, assembled_workflows_data, workflow_model):
    assembled_wfs = generate_final_assembled_workflows(parsed_workflows, assembled_workflows_data)

    st.write("************")
    for wf in assembled_wfs:
        wf.print()

    st.write("************")

    assembled_flat_wfs = []

    for wf in assembled_wfs:
        flat_wf = flatten_workflows(wf)
        assembled_flat_wfs.append(flat_wf)
        flat_wf.print()

    st.write("************")

    for espace in workflow_model.espaces:
        vp_methods = []

        st.write(f"Experiment Space '{espace.name}' of '{espace.assembled_workflow.name}'")

        for m in espace.configure.methods:
            vp_method = {}
            vp_methods.append(vp_method)
            vp_method["espace"] = espace.name
            vp_method["assembled_workflow"] = espace.assembled_workflow.name
            vp_method["name"] = m.name
            vp_method["type"] = m.type
            vp_method["vps"] = {}
            vp_method["tasks"] = {}
            if m.runs:
                vp_method["runs"] = m.runs
            st.write(f"Method with name '{m.name}' of type '{m.type}'")

        for vp in espace.configure.vps:
            method_name = vp.method.name
            vp_method = next(m for m in vp_methods if m["name"] == method_name)
            if vp_method["type"] == "gridsearch":
                vp_method["vps"][vp.name] = vp.vp_values.values
            if vp_method["type"] == "randomsearch":
                vp_method["vps"][vp.name] = {"min": vp.vp_values.min, "max": vp.vp_values.max}

        for task in espace.tasks:
            for c in task.config:
                param = {c.name: c.vp}
                vp_method = next(v for v in vp_methods if v["name"] == c.method.name)
                tasks = vp_method["tasks"]
                if task.alias.name not in tasks:
                    tasks[task.alias.name] = {c.name: c.vp}
                else:
                    tasks[task.alias.name][c.name] = c.vp

        st.write("************")
        st.write(vp_methods)
        st.write("************")

        for vp_method in vp_methods:
            run_experiment(assembled_flat_wfs,vp_method)
