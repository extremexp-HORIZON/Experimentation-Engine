import streamlit as st
import pandas as pd

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

    st.markdown("<h1 style='font-family: Merriweather, serif;text-align: left; color: #0055BC;'>Project Library</h1>", unsafe_allow_html=True)
    st.write(" ")
    st.write(" ")



    projects = [
            {"Title": "Project 1", "Description": "Description of Project 1", "Created": "January 1, 2023"},
            {"Title": "Project 2", "Description": "Description of Project 2", "Created": "February 15, 2023"},
            {"Title": "Project 3", "Description": "Description of Project 3", "Created": "March 10, 2023"}
        ]


    df = pd.DataFrame(projects)
    st.table(df[["Title", "Description", "Created"]])


if __name__ == "__main__":
    main()

