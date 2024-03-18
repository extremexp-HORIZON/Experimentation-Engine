import streamlit as st
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

    def clone(self,parsed_workflows):
        new_t = WorkflowTask(self.name)
        new_t.add_implementation_file(self.impl_file)
        new_t.add_sub_workflow_name(self.sub_workflow_name)
        if self.sub_workflow_name:
            new_t.add_sub_workflow(next(w for w in parsed_workflows if w.name == self.sub_workflow_name).clone(parsed_workflows))
        new_t.add_dependencies(self.dependencies)
        new_t.input_files = self.input_files
        new_t.output_files = self.output_files
        new_t.set_order(self.order)
        new_t.params = self.params
        return new_t

    def print(self, tab=""):
        st.subheader(f"Task: {self.name}")
        st.text(f"Sub-workflow name: {self.sub_workflow_name}")
        st.text(f"Dependencies: {self.dependencies}")
        st.text(f"Inputs: {self.input_files}")
        st.text(f"Outputs: {self.output_files}")
        st.text(f"Order: {self.order}")
        st.text(f"Params: {self.params}")
        st.text(f"Implementation: {self.impl_file}")

class Workflow():

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

    def clone(self,parsed_workflows):
        new_w = Workflow(self.name)
        new_w.is_main = self.is_main
        for t in self.tasks:
            new_t = t.clone(parsed_workflows)
            new_w.tasks.append(new_t)
        return new_w

    def print(self, tab=""):
        st.header(f"Workflow: {self.name}")
        st.write(f"Main Workflow: {self.is_main}")
        st.write(f"Flat Workflow: {self.is_flat()}")

        for t in self.tasks:
            st.write("")
            t.print()



