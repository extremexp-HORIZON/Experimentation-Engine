import streamlit as st
import textx
import time
from classes import *
from functions import *

def main():
    st.image("https://extremexp.eu/wp-content/uploads/2023/04/logo-crop.png", width=700)
    st.markdown("<h1 style='text-align: center;'>Experimentation Engine Text Editor</h1>", unsafe_allow_html=True)

    st.write("")
    st.write("")

    start_button_clicked = st.button("Start New Project or Experiment")

    if "clicked" not in st.session_state:
        st.session_state.clicked = False

    if start_button_clicked:
        st.session_state.clicked = True

    if st.session_state.clicked:
        project_title = st.text_input("Enter project title:")
        project_description = st.text_area("Enter project description:")
        dsl_file = st.file_uploader("Upload DSL File", type=["dsl"])

        if dsl_file is not None:
            filepath = str(dsl_file.name)
        else:
            st.write("Please provide a valid DSL file.")

        if project_title and project_description:
            st.button("Create Project", key="cre_prj")

        if (st.session_state.get("cre_prj")):
            progress_text = "Creating the Project. Please wait."
            my_bar = st.progress(0, text=progress_text)

            for percent_complete in range(100):
                time.sleep(0.01)
                my_bar.progress(percent_complete + 1, text=progress_text)
            time.sleep(1)

            if checkDSL(filepath):
                st.success(f"Project {project_title} complies with the grammar and created successfully!")

            workflow_model = None

            with open(filepath, 'r') as file:
                workflow_code = file.read()
                workflow_metamodel = textx.metamodel_from_file('workflow_grammar.tx')
                workflow_model = workflow_metamodel.model_from_str(workflow_code)

            view_wf_expander = st.expander("Parsed Workflows")
            if workflow_model:
                with view_wf_expander:
                    parsed_workflows = print_parse_workflows(workflow_model)
                    for wf in parsed_workflows:
                        wf.print()

            view_awf_expander = st.expander("Assembled Workflows Data")
            if workflow_model:
                with view_awf_expander:
                    assembled_workflows_data = print_assembled_wf_data(workflow_model)
                    st.write(assembled_workflows_data)

            generate_awf_expander = st.expander("Generate Assembled Workflows")
            if workflow_model:
                with generate_awf_expander:
                    parsed_workflows = print_parse_workflows(workflow_model)
                    assembled_workflows_data = print_assembled_wf_data(workflow_model)
                    generate_assembled_workflows(parsed_workflows, assembled_workflows_data, workflow_model)

if __name__ == "__main__":
    main()
