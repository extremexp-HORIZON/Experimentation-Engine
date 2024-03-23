from proactive_interface import *
import credentials


def execute_wf(w):
    print("****************************")
    print(f"Executing workflow {w.name}")
    print("****************************")
    w.print()
    print("****************************")

    gateway = create_gateway_and_connect_to_it(credentials.proactive_username, credentials.proactive_password)
    job = create_job(gateway, w.name)
    fork_env = create_fork_env(gateway, job)

    previous_tasks = []
    for t in w.tasks:
        task_to_execute = create_python_task(gateway, t.name, fork_env, t.impl_file, t.input_files, previous_tasks)
        if len(t.params)>0:
            configure_task(task_to_execute, t.params)
        job.addTask(task_to_execute)
        previous_tasks = [task_to_execute]
    print("Tasks added.")

    job_id, job_result, job_outputs = submit_job_and_retrieve_results_and_outputs(gateway, job)
    teardown(gateway)

    print("****************************")
    print(f"Finished executing workflow {w.name}")
    print("****************************")
