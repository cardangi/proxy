import docker
import json

client = docker.Client(base_url='unix://var/run/docker.sock')
for event in client.events():
    event = json.loads(event)
    print(event)
