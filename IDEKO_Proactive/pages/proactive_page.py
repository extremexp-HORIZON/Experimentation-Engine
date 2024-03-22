import streamlit as st
from functions import *
import time
import proactive
import credentials
def main():
    st.image("https://extremexp.eu/wp-content/uploads/2023/04/logo-crop.png", width=700)
    st.markdown("<h1 style='text-align: center;'>Experimentation Engine Text Editor</h1>", unsafe_allow_html=True)

    st.write("")
    st.write("")

    start_button_clicked = st.button("Connect Proactive")

    if "clicked" not in st.session_state:
        st.session_state.clicked = False

    if start_button_clicked:
        st.session_state.clicked = True

    if st.session_state.clicked:
        with st.status("Connecting to proactive-server...", expanded=True) as status:
            st.write("Logging on proactive-server...")
            # time.sleep(1)
            proactive_host = 'try.activeeon.com'
            proactive_port = '8443'
            proactive_url = "https://" + proactive_host + ":" + proactive_port
            # st.write("Creating gateway...")
            gateway = proactive.ProActiveGateway(proactive_url, debug=False)
            # time.sleep(2)
            # st.write("Gateway created.")
            # time.sleep(1)
            # st.write("Connecting on: " + proactive_url)
            # time.sleep(1)
            gateway.connect(username=credentials.proactive_username, password=credentials.proactive_password)
            assert gateway.isConnected() is True
            status.update(label="Done!", state="complete", expanded=True)

        st.success("Successfully Connected")


        job = create_job(gateway, "PythonMLWorkflow")

        fork_env = create_fork_env(gateway, job)

        init_task = create_python_task(gateway, "init", fork_env, 'tasks/02_ML_Example/init.py', "datasets/boston-local.csv")
        split_task = create_python_task(gateway, "split", fork_env, "tasks/02_ML_Example/split.py", [], [init_task])
        train_task = create_python_task(gateway, "train", fork_env, "tasks/02_ML_Example/train.py", [], [split_task])
        predict_task = create_python_task(gateway, "predict", fork_env, "tasks/02_ML_Example/predict.py", [], [split_task, train_task], True)

        st.write("Adding tasks to the job...")
        job.addTask(init_task)
        job.addTask(split_task)
        job.addTask(train_task)
        job.addTask(predict_task)
        st.write("Tasks added.")

        st.write("Submitting the job to the proactive scheduler...")
        # job_id = gateway.submitJob(job, debug=False)
        job_id = gateway.submitJobWithInputsAndOutputsPaths(job, debug=False)
        st.write("job_id: " + str(job_id))

        st.write("Getting job results...")
        job_result = gateway.getJobResult(job_id)
        st.write(job_result)

        st.write("Getting job outputs...")
        job_outputs = gateway.printJobOutput(job_id)
        st.write(job_outputs)

        st.write("Disconnecting")
        gateway.disconnect()
        st.write("Disconnected")
        gateway.terminate()
        st.write("Finished")


if __name__ == "__main__":
    main()