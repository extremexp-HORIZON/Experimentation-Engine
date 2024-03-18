import streamlit as st
from functions import connect_proactive, create_proactive_job

st.image("https://extremexp.eu/wp-content/uploads/2023/04/logo-crop.png", width=700)
st.markdown("<h1 style='text-align: center;'>Experimentation Engine Text Editor</h1>", unsafe_allow_html=True)

st.write("")
st.write("")

connect_pro_button = st.button("Connect Proactive", key="connect_pro")

if "clicked" not in st.session_state:
    st.session_state.clicked = False

if connect_pro_button:
    st.session_state.clicked = True

if st.session_state.clicked:
    gateway = connect_proactive()

    if gateway:
        st.button("Create Proactive Job", key="create_job")

    if (st.session_state.get("create_job")):
        create_proactive_job(gateway)


