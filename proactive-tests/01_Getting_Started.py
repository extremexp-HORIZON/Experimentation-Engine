import proactive
import credentials

print("Logging on proactive-server...")
proactive_host = 'try.activeeon.com'
proactive_port = '8443'
proactive_url  = "https://"+proactive_host+":"+proactive_port
print("Creating gateway ")
gateway = proactive.ProActiveGateway(proactive_url, debug=False)
print("Gateway created")

print("Connecting on: " + proactive_url)
gateway.connect(username=credentials.proactive_username, password=credentials.proactive_password)
assert gateway.isConnected() is True
print("Connected")

print("Creating a proactive job...")
proactive_job = gateway.createJob()
proactive_job.setJobName("SimplePythonJob")
print("Job created.")

print("Creating a proactive task...")
proactive_task = gateway.createPythonTask()
proactive_task.setTaskName("SimplePythonTask")
proactive_task.setTaskImplementation("""
result='Hello from SimplePythonJob world!'
print(result)
""")
print("Task created.")

print("Adding task to the job...")
proactive_job.addTask(proactive_task)
print("Task added.")

print("Submitting the job to the proactive scheduler...")
job_id = gateway.submitJob(proactive_job, debug=False)
print("job_id: " + str(job_id))

print("Getting job output...")
job_result = gateway.getJobResult(job_id)
print(job_result)

print("Disconnecting")
gateway.disconnect()
print("Disconnected")
gateway.terminate()
print("Finished")
