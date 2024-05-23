from proactive_interface import *
import credentials
from proactive import ProactiveScriptLanguage

def create_flow_script(gateway, task_if, task_else, task_continuation, condition):
    branch_script = """
    # Always select the "IF" branch
    if """ + condition + """:
        branch = "if"
    else:
        branch = "else"
    """

    print("branch script",branch_script)

    flow_script = gateway.createBranchFlowScript(
        branch_script,
        task_if,
        task_else,
        task_continuation,
        script_language=ProactiveScriptLanguage().python()
    )
    return flow_script

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
        print("t.is_condition_task()")
        print(t.is_condition_task())
        if t.is_condition_task():
            print("t.task_if")
            print(t.task_if)
            t.setFlowScript(create_flow_script(gateway, t.task_if, t.task_else, t.task_continuation, t.condition))
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


