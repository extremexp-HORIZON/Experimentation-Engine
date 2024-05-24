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

    created_tasks = []
    for t in w.tasks:
        dependent_tasks = [ct for ct in created_tasks if ct.getTaskName() in t.dependencies]
        task_to_execute = create_python_task(gateway, t.name, fork_env, t.impl_file, t.input_files, dependent_tasks)
        if len(t.params)>0:
            configure_task(task_to_execute, t.params)
        if t.is_condition_task():
            task_to_execute.setFlowScript(
                create_flow_script(gateway, t.name, t.if_task_name, t.else_task_name, t.continuation_task_name, t.condition)
            )
        job.addTask(task_to_execute)
        created_tasks.append(task_to_execute)
    print("Tasks added.")

    job_id, job_result, job_outputs = submit_job_and_retrieve_results_and_outputs(gateway, job)
    teardown(gateway)

    print("****************************")
    print(f"Finished executing workflow {w.name}")
    print("****************************")


