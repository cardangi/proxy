import docker
import json

client = docker.Client(base_url='unix://var/run/docker.sock')


def start(container_id):
    container = client.inspect_container(container_id)
    ipaddress = container['NetworkSettings']['Networks']['bridge']['IPAddress']
    exp_ports = container['NetworkSettings']['Ports']
    env = container['Config']['Env']
    ports = []

    for port in exp_ports:
        if exp_ports[port] is not None:
            ports[:0] = [exp_ports[port][0]['HostPort']]

    print('Started container with id: ' + container_id)
    print(
        'Container ' + container['Config']['Hostname'] + ', is on ip ' + ipaddress + ', and port/s ' + ', '.join(ports))
    data(container_id, ports, env)


def destroy(container_id):
    print('Destroyed container with id: ' + container_id)


def data(container_id, ports, env):
    add_host = True
    nginx_config = sort_env(env)

    json_data = json.loads(open('data.json').read())
    for host in json_data:
        if nginx_config[1] in host:
            add_host = False

    if add_host is True:
        add_host_to_json(container_id, ports, nginx_config, json_data)
    if add_host is False:
        return None


def sort_env(env):
    nginx_config = []
    for env_var in env:
        if 'VIRTUAL_HOST' in env_var:
            nginx_config[1] = env_var['VIRTUAL_HOST']
        if 'LETSENCRYPT_EMAIL' in env_var:
            nginx_config[2] = env_var['LETSENCRYPT_EMAIL']
        if 'HTTPS' in env_var:
            nginx_config[3] = env_var['HTTPS']
    return nginx_config


def add_host_to_json(container_id, ports, config, json_data):
    json_data = json_data.append([('ports', ports), ('config', config)])
    json_data = json.dumps(json_data)
    open('data.json', 'r+').write(json_data)


for event in client.events():
    event = json.loads(event)
    if 'Action' in event.keys() and 'id' in event.keys():
        if 'start' in event['Action']:
            start(event['id'])
        if 'destroy' in event['Action']:
            destroy(event['id'])
