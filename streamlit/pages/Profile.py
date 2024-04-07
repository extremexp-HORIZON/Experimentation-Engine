import streamlit as st
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

createsidebar()


st.markdown("<h1 style='text-align: center; color: #0055BC;'>Profile</h1>", unsafe_allow_html=True)
st.write(" ")
st.write(" ")