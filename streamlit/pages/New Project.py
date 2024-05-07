import streamlit as st
import textx
import subprocess
import time
import webbrowser
import os
import sys
parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)
from classes import *
from functions import *
from View import *
from itertools import product
import random
from dsl import dsl_exceptions
from wf_execution import execute_wf


def createsidebar():
    st.markdown("""<style>[data-testid=stSidebar] { background-color: #E9FCDB;}</style> """, unsafe_allow_html=True)

    st.sidebar.write(" ")
    st.sidebar.write(" ")

    st.sidebar.image("images/ExtremeXPLogoIcon.png", use_column_width=True)

    st.sidebar.image("images/ExtremeXPLogoText.png", use_column_width=True)

    st.sidebar.write(" ")

    st.sidebar.subheader("About")
    about_text="Our platform is dedicated to optimizing complex data analytics workflows. With the application, you can create workflows, generate workflow variants, and run experiments to refine your analytical processes. Join us and unlock the potential of your analytics journey."
    st.sidebar.markdown(f'<p style="text-align: justify;">{about_text}</p>', unsafe_allow_html=True)

    st.sidebar.write(" ")
    st.sidebar.write(" ")

    st.sidebar.subheader("Version 1.0")
    st.sidebar.subheader("Copyright © 2023 ExtremeXP")



def wide_space_default():
    st.set_page_config(layout="wide")




def main():
    wide_space_default()
    createsidebar()

    st.markdown("<h1 style='font-family: Merriweather, serif;text-align: left; color: #0055BC;'>Start New Project</h1>", unsafe_allow_html=True)
    st.write(" ")
    st.write(" ")
    st.write("")
    st.write("")

    st.markdown("<h2 style='color: #38D6A2;'>Demo</h2>", unsafe_allow_html=True)

    # st.markdown(
    #     f'<img src="https://media.giphy.com/media/vFKqnCdLPNOKc/giphy.gif" style="width: 600px; height: 500px; display: block; margin-left: auto; margin-right: auto;" alt="Image">',
    #     unsafe_allow_html=True
    # )

    st.video("ScreenRecording1.mp4", start_time=0, subtitles=None)

    st.write(" ")
    st.write(" ")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        pass
    with col2:
        pass
    with col4:
        pass
    with col5:
        pass
    with col3:
        start_button_clicked = st.button("Create Project")

    if "clicked" not in st.session_state:
        st.session_state.clicked = False

    if start_button_clicked:
        st.session_state.clicked = True

    if st.session_state.clicked:
        project_title = st.text_input("Enter project title:")
        project_description = st.text_area("Enter project description:")
        dsl_file = st.file_uploader("Create/ Upload DSL File", type=["dsl"])
        if dsl_file is not None:
            dsl_file_bytes = dsl_file.read()

            target_filename = "project.dsl"

            with open(target_filename, "wb") as f:
                f.write(dsl_file_bytes)

            # st.success(f"DSL file uploaded successfully!")


        filename =""
        if st.button("New DSL"):
            dsl = st.text_area("Type your DSL here.",height=500)

            filename = st.text_input("Enter a file name:", max_chars=100)


            save_button = st.button("Save DSL", key="save_dsl")


        if st.session_state.get("save_dsl"):
            if filename.strip() == "":
                st.error("Please enter a file name.")
            else:
                st.success("Saved")



        if project_title and project_description and dsl_file:
            st.button("Create Project", key="cre_prj")
        else:
            st.write("Please enter the correct details.")

        if (st.session_state.get("cre_prj")):
            progress_text = "Creating the Project. Please wait."
            my_bar = st.progress(0, text=progress_text)

            for percent_complete in range(100):
                time.sleep(0.01)
                my_bar.progress(percent_complete + 1, text=progress_text)
            time.sleep(1)


            workflow_model = checkDSL(target_filename)

            if workflow_model:
                # st.success(f"Project {project_title} created successfully!")
                st.success(f"Project {project_title} complies with the grammar and created successfully!")

                with st.spinner('Loading the Workflows'):
                    time.sleep(5)

                view_wf_expander = st.expander("Parsed Workflows")
                with view_wf_expander:
                    st.markdown("""
                            <h1 style="text-align: center; font-size: 36px; color: #007bff;">PARSED WORKFLOWS</h1>
                            <hr style="border: 0; height: 1px; background-color: #333; margin: 1em 0;">""",
                                unsafe_allow_html=True)
                    parsed_workflows = print_parse_workflows(workflow_model)
                    for wf in parsed_workflows:
                        wf.print("\t")

                view_awf_expander = st.expander("Assembled Workflows Data")
                with view_awf_expander:
                    st.markdown("""<h1 style="text-align: center; font-size: 36px; color: #007bff;">PARSE ASSEMBLED WORKFLOWS DATA</h1>
                                  <hr style="border: 0; height: 1px; background-color: #333; margin: 1em 0;">""",
                                unsafe_allow_html=True)
                    assembled_workflows_data = print_assembled_wf_data(workflow_model)
                    st.write(assembled_workflows_data)

                generate_awf_expander = st.expander("Generate Assembled Workflows")
                with generate_awf_expander:
                    st.markdown("""<h1 style="text-align: center; font-size: 36px; color: #007bff;">GENERATE ASSEMBLED WORKFLOWS</h1>
                                                    <hr style="border: 0; height: 1px; background-color: #333; margin: 1em 0;">""",
                                unsafe_allow_html=True)
                    parsed_workflows = print_parse_workflows(workflow_model)
                    generate_assembled_workflows(parsed_workflows, assembled_workflows_data, workflow_model)


            st.markdown("[Show on Proactive](https://try.activeeon.com/automation-dashboard/#/workflow-execution)")




if __name__ == "__main__":
    main()