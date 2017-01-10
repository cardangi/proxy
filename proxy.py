import docker
import json

client = docker.Client(base_url='unix://var/run/docker.sock')
for event in client.events():
    event = json.loads(event)
    if 'Action' in event.keys():
        print('Action: ' + event['Action'] + ', on container with ID: ' + event['id'])
