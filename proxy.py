import docker
import json

client = docker.Client(base_url='unix://var/run/docker.sock')
for event in client.events():
    event = json.loads(event)
    if hasattr(event, 'status') and hasattr(event, 'id'):
        print('Status: ' + event['status'] + ', on container with ID: ' + event['id'])
