import docker
import json

client = docker.Client(base_url='unix://var/run/docker.sock')


def start(container_id):
    container = client.inspect_container(container_id)
    ipaddress = container['NetworkSettings']['Networks']['bridge']['IPAddress']
    exp_ports = container['HostConfig']['PortBindings']
    ports = ''

    for port, host_port in exp_ports:
        print(host_port)
        # ports += ', ' + port[0]['HostPort']

    print(json.dumps(container))
    print('Started container with id: ' + container_id)
    print('Container ' + container['Config']['Hostname'] + ', is on ip ' + ipaddress + ', and port/s ' + ports)


def destroy(container_id):
    print('Destroyed container with id: ' + container_id)


print('Started proxy')
for event in client.events():
    event = json.loads(event)
    if 'Action' in event.keys() and 'id' in event.keys():
        if 'start' in event['Action']:
            print('Got a start action')
            start(event['id'])
        if 'destroy' in event['Action']:
            print('Got a destroy action')
            destroy(event['id'])
