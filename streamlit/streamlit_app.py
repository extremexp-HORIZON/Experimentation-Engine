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
            # Get the uploaded file's contents as bytes
            dsl_file_bytes = dsl_file.read()

            # Define the target filename (assuming a fixed location)
            target_filename = "project.dsl"

            # Open the target file in write-binary mode (wb)
            with open(target_filename, "wb") as f:
                f.write(dsl_file_bytes)

            # Success message after overwriting
            st.success(f"DSL file uploaded successfully!")

        else:
            st.write("Please provide a valid DSL file.")

        if project_title and project_description and dsl_file:
            # Use a flag and conditional rendering
            create_project_button = st.button("Create Project", key="cre_prj")
            if create_project_button:
                progress_text = "Creating the Project. Please wait."
                my_bar = st.progress(0, text=progress_text)

                for percent_complete in range(100):
                    time.sleep(0.01)
                    my_bar.progress(percent_complete + 1, text=progress_text)
                time.sleep(1)

                workflow_model = checkDSL(target_filename)
                if workflow_model is not None:
                    st.success(f"Project {project_title} complies with the grammar and created successfully!")

                if workflow_model:
                    view_wf_expander = st.expander("Parsed Workflows")
                    with view_wf_expander:
                        st.markdown("""
                                <h1 style="text-align: center; font-size: 36px; color: #007bff;">PARSED WORKFLOWS</h1>
                                <hr style="border: 0; height: 1px; background-color: #333; margin: 1em 0;">""", unsafe_allow_html=True)
                        parsed_workflows = print_parse_workflows(workflow_model)  # Placeholder
                        for wf in parsed_workflows:
                            wf.print("\t")

                    view_awf_expander = st.expander("Assembled Workflows Data")
                    with view_awf_expander:
                        st.markdown("""<h1 style="text-align: center; font-size: 36px; color: #007bff;">PARSE ASSEMBLED WORKFLOWS DATA</h1>
                                      <hr style="border: 0; height: 1px; background-color: #333; margin: 1em 0;">""",unsafe_allow_html=True)
                        assembled_workflows_data = print_assembled_wf_data(workflow_model)
                        st.write(assembled_workflows_data)

                    generate_awf_expander = st.expander("Generate Assembled Workflows")
                    with generate_awf_expander:
                        st.markdown("""<h1 style="text-align: center; font-size: 36px; color: #007bff;">GENERATE ASSEMBLED WORKFLOWS</h1>
                                    <hr style="border: 0; height: 1px; background-color: #333; margin: 1em 0;">""",unsafe_allow_html=True)
                        parsed_workflows = print_parse_workflows(workflow_model)
                        assembled_wfs = generate_assembled_workflows(parsed_workflows, assembled_workflows_data,workflow_model)




if __name__ == "__main__":
    main()
