import streamlit as st

class WorkflowDataset():
    def __init__(self, name):
        self.name = name
        self.path = None

    def add_path(self, path):
        self.path = path

class WorkflowTask():

    def __init__(self, name):
        self.params = {}
        self.order = None
        self.sub_workflow = None
        self.sub_workflow_name = None
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
        new_t = WorkflowTask(self.name)
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
        st.markdown(f"""<b><span style="font-size: 24px;">{tab}Task name: {self.name}</span></b>""",unsafe_allow_html=True)
        st.write(f"{tab}\twith task implementation: {self.impl_file}")
        st.write(f"{tab}\twith sub_workflow_name: {self.sub_workflow_name}")
        st.write(f"{tab}\twith sub_workflow: {self.sub_workflow}")
        st.write(f"{tab}\twith dependencies: {self.dependencies}")
        st.write(f"{tab}\twith inputs: {self.input_files}")
        st.write(f"{tab}\twith outputs: {self.output_files}")
        st.write(f"{tab}\twith order: {self.order}")
        st.write(f"{tab}\twith params: {self.params}")


class Workflow():

    def __init__(self, name):
        self.is_main = None
        self.name = name
        self.tasks = []
        self.datasets = []

    def add_task(self, task):
        self.tasks.append(task)

    def add_dataset(self, dataset):
        self.datasets.append(dataset)

    def get_task(self, name):
        return next(t for t in self.tasks if t.name == name)

    def get_dataset(self, name):
        return next(ds for ds in self.datasets if ds.name == name)

    def is_flat(self):
        for t in self.tasks:
            if t.sub_workflow:
                return False
        return True

    def set_is_main(self, is_main):
        self.is_main = is_main

    def clone(self):
        new_w = Workflow(self.name)
        new_w.is_main = self.is_main
        for t in self.tasks:
            new_t = t.clone()
            new_w.tasks.append(new_t)
        return new_w

    def print(self, tab=" "):
        st.markdown(f"""<b><span style="font-size: 24px;">{tab}Workflow with name: {self.name}</span></b>""", unsafe_allow_html=True)
        st.write(f"{tab}Workflow is main?: {self.is_main}")
        st.write(f"{tab}Workflow is flat?: {self.is_flat()}")
        for t in self.tasks:
            t.print(tab + "\t")
            if t.sub_workflow:
                t.sub_workflow.print(tab + "\t\t\t")



