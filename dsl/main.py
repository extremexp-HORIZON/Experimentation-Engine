import textx
from itertools import product
import random


class ConcreteFlatWorkflowTask():

    def __init__(self, name):
        self.params = {}
        self.order = None
        self.sub_workflow_name = None
        self.sub_workflow = None
        self.impl_file = None
        self.input_files = []
        self.output_files = []
        self.dependencies = []
        self.name = name

    def add_implementation_file(self, impl_file):
        self.impl_file = impl_file

    def add_sub_workflow_name(self, workflow_name):
        self.sub_workflow_name = workflow_name

    def add_sub_workflow(self, workflow):
        self.sub_workflow = workflow

    def add_dependencies(self, dependencies):
        self.dependencies += dependencies

    def remove_dependency(self, dependency):
        self.dependencies.remove(dependency)

    def set_order(self, order):
        self.order = order

    def set_param(self, key, value):
        self.params[key] = value

    def clone(self):
        new_t = ConcreteFlatWorkflowTask(self.name)
        new_t.add_implementation_file(self.impl_file)
        new_t.add_sub_workflow_name(self.sub_workflow_name)
        if self.sub_workflow_name:
            new_t.add_sub_workflow(next(w for w in parsed_workflows if w.name == self.sub_workflow_name).clone())
        new_t.add_dependencies(self.dependencies)
        new_t.input_files = self.input_files
        new_t.output_files = self.output_files
        new_t.set_order(self.order)
        new_t.params = self.params
        return new_t

    def print(self, tab=""):
        print(f"{tab}with task name : {self.name}")
        print(f"{tab}\twith task implementation: {self.impl_file}")
        print(f"{tab}\twith sub_workflow_name: {self.sub_workflow_name}")
        print(f"{tab}\twith sub_workflow: {self.sub_workflow}")
        print(f"{tab}\twith dependencies: {self.dependencies}")
        print(f"{tab}\twith inputs: {self.input_files}")
        print(f"{tab}\twith outputs: {self.output_files}")
        print(f"{tab}\twith order: {self.order}")
        print(f"{tab}\twith params: {self.params}")


class ConcreteFlatWorkflow():

    def __init__(self, name):
        self.is_main = None
        self.name = name
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def get_task(self, name):
        return next(t for t in self.tasks if t.name == name)

    def is_flat(self):
        for t in self.tasks:
            if t.sub_workflow:
                return False
        return True

    def set_is_main(self, is_main):
        self.is_main = is_main

    def clone(self):
        new_w = ConcreteFlatWorkflow(self.name)
        new_w.is_main = self.is_main
        for t in self.tasks:
            new_t = t.clone()
            new_w.tasks.append(new_t)
        return new_w

    def print(self, tab=""):
        print(f"{tab}Workflow with name: {self.name}")
        print(f"{tab}Workflow is main?: {self.is_main}")
        print(f"{tab}Workflow is flat?: {self.is_flat()}")
        for t in self.tasks:
            t.print(tab+"\t")
            if t.sub_workflow:
                t.sub_workflow.print(tab+"\t\t")


def process_dependencies(task_dependencies, nodes, parsing_node_type, verbose_logging=False):
    if verbose_logging:
        print(parsing_node_type)
    for n1, n2 in zip(nodes[0::1], nodes[1::1]):
        if verbose_logging:
            print(str(n2.name), ' depends on ', str(n1))
        if n2.name in task_dependencies:
            print(f"{parsing_node_type}: Double dependency ({n2.name}), check your specification")
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
    new_wf = ConcreteFlatWorkflow(assembled_wf.name)
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


def generate_final_assembled_workflows(wfs, assembled_wfs_data):
    new_wfs = []
    for assembled_wf_data in assembled_wfs_data:
        wf = next(w for w in wfs if w.name == assembled_wf_data["parent"]).clone()
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
            else:
                print(f"Do not need to configure task '{task.name}'")
            if task.sub_workflow:
                configure_wf(task.sub_workflow, assembled_wf_data)
        print("-------------------------------")
    return new_wfs


def execute_wf(w):
    print(f"Executing workflow {w.name}")
    w.print()
    print(f"Finished executing workflow {w.name}")


def configure_final_workflow(vp_method, c):
    w = next(w for w in assembled_flat_wfs if w.name == vp_method["assembled_workflow"])
    for t in w.tasks:
        if t.name in vp_method["tasks"].keys():
            task_config = vp_method["tasks"][t.name]
            for p in task_config.keys():
                alias = task_config[p]
                print(f"Setting param '{p}' of task '{t.name}' to '{c[alias]}'")
                t.set_param(p, c[alias])
    return w


def generate_parameter_combinations(parameters):
    param_names = parameters.keys()
    param_values = parameters.values()
    return [dict(zip(param_names, values)) for values in product(*param_values)]


def run_grid_search_exp(vp_method):
    combinations = generate_parameter_combinations(vp_method["vps"])
    print(f"Grid search generated {len(combinations)} configurations to run.")
    pp.pprint(combinations)
    run_count = 1
    for c in combinations:
        print(f"Run {run_count}")
        workflow_to_run = configure_final_workflow(vp_method, c)
        execute_wf(workflow_to_run)
        print("..........")
        run_count += 1


def generate_random_config(vps):
    c = {}
    for key in vps.keys():
        param = vps[key]
        value = random.randint(param["min"], param["max"])
        c[key] = value
    return c


def run_random_search_exp(vp_method):
    for i in range(vp_method["runs"]):
        print(f"Run {i+1}")
        c = generate_random_config(vp_method["vps"])
        workflow_to_run = configure_final_workflow(vp_method, c)
        execute_wf(workflow_to_run)
        print("..........")


def run_experiment(vp_method):
    print(f"Running experiment of espace '{vp_method['espace']}' of type '{vp_method['type']}'")
    method_type = vp_method["type"]
    if method_type == "gridsearch":
        run_grid_search_exp(vp_method)
    if method_type == "randomsearch":
        run_random_search_exp(vp_method)


with open('IDEKO.dsl', 'r') as file:
    workflow_code = file.read()

workflow_metamodel = textx.metamodel_from_file('workflow_grammar.tx')
workflow_model = workflow_metamodel.model_from_str(workflow_code)

print("*********************************************************")
print("***************** PARSE WORKFLOWS ***********************")
print("*********************************************************")

parsed_workflows = []
for workflow in workflow_model.workflows:
    wf = ConcreteFlatWorkflow(workflow.name)
    parsed_workflows.append(wf)

    task_dependencies = {}

    for e in workflow.elements:
        if e.__class__.__name__ == "DefineTask":
            task = ConcreteFlatWorkflowTask(e.name)
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

for wf in parsed_workflows:
    wf.print()

print("*********************************************************")
print("********** PARSE ASSEMBLED WORKFLOWS DATA ***************")
print("*********************************************************")

assembled_workflows_data = []
for assembled_workflow in workflow_model.assembledWorkflows:
    assembled_workflow_data = {}
    assembled_workflows_data.append(assembled_workflow_data)
    assembled_workflow_data["name"] = assembled_workflow.name
    assembled_workflow_data["parent"] = assembled_workflow.parent_workflow.name
    assembled_workflow_tasks = {}
    assembled_workflow_data["tasks"] = assembled_workflow_tasks

    configurations = assembled_workflow.configure
    while configurations:
        for config in assembled_workflow.configure:
            assembled_workflow_task = {}
            if config.workflow:
                assembled_workflow_task["workflow"] = config.workflow
                assembled_workflow_tasks[config.alias.name] = assembled_workflow_task
            elif config.filename:
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

assembled_flat_wfs = []

for wf in assembled_wfs:
    flat_wf = flatten_workflows(wf)
    assembled_flat_wfs.append(flat_wf)
    flat_wf.print()

print("************")

for espace in workflow_model.espaces:
    vp_methods = []

    print(f"Experiment Space '{espace.name}' of '{espace.assembled_workflow.name}'")

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
        print(f"Method with name '{m.name}' of type '{m.type}'")

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

    print("************")
    pp.pprint(vp_methods)
    print("************")

    for vp_method in vp_methods:
        run_experiment(vp_method)
