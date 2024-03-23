import proactive


def create_gateway_and_connect_to_it(username, password):
    print("Logging on proactive-server...")
    proactive_host = 'try.activeeon.com'
    proactive_port = '8443'
    proactive_url  = "https://"+proactive_host+":"+proactive_port
    print("Creating gateway ")
    gateway = proactive.ProActiveGateway(proactive_url, debug=False)
    print("Gateway created")

    print("Connecting on: " + proactive_url)
    gateway.connect(username=username, password=password)
    assert gateway.isConnected() is True
    print("Connected")
    return gateway


def create_job(gateway, workflow_name):
    print("Creating a proactive job...")
    proactive_job = gateway.createJob()
    proactive_job.setJobName(workflow_name)
    print("Job created.")
    return proactive_job


def create_fork_env(gateway, proactive_job):
    print("Adding a fork environment to the import task...")
    proactive_fork_env = gateway.createForkEnvironment(language="groovy")
    proactive_fork_env.setImplementationFromFile("./scripts/fork_env.groovy")
    proactive_job.addVariable("CONTAINER_PLATFORM", "docker")
    proactive_job.addVariable("CONTAINER_IMAGE", "docker://activeeon/dlm3")
    proactive_job.addVariable("CONTAINER_GPU_ENABLED", "false")
    proactive_job.addVariable("CONTAINER_LOG_PATH", "/shared")
    proactive_job.addVariable("HOST_LOG_PATH", "/shared")
    print("Fork environment created.")
    return proactive_fork_env


def create_python_task(gateway, task_name, fork_environment, task_impl, input_files=[], dependencies=[], is_precious_result=False):
    print(f"Creating task {task_name}...")
    task = gateway.createPythonTask()
    task.setTaskName(task_name)
    task.setTaskImplementationFromFile(task_impl)
    task.setForkEnvironment(fork_environment)
    for input_file in input_files:
        task.addInputFile(input_file)
    for dependency in dependencies:
        task.addDependency(dependency)
    task.setPreciousResult(is_precious_result)
    print("Task created.")
    return task


def configure_task(task, configurations):
    for k in configurations.keys():
        task.addVariable(k, configurations[k])


def submit_job_and_retrieve_results_and_outputs(gateway, job):
    print("Submitting the job to the scheduler...")

    job_id = gateway.submitJobWithInputsAndOutputsPaths(job, debug=False)
    print("job_id: " + str(job_id))

    print("Getting job results...")
    job_result = gateway.getJobResult(job_id)
    print(job_result)

    print("Getting job outputs...")
    job_outputs = gateway.printJobOutput(job_id)
    print(job_outputs)

    return job_id, job_result, job_outputs


def teardown(gateway):
    print("Disconnecting")
    gateway.disconnect()
    print("Disconnected")
    gateway.terminate()
    print("Finished")
