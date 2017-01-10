import docker
import json


def start(container_id):
    return 'Started container with id: ' + container_id


def destroy(container_id):
    return 'Destroyed container with id: ' + container_id


client = docker.Client(base_url='unix://var/run/docker.sock')
for event in client.events():
    event = json.loads(event)
    if 'Action' in event.keys() and 'id' in event.keys():
        if 'start' in event['Action']:
            start(event['id'])
        if 'destroy' in event['Action']:
            destroy(event['id'])
