import docker
import json

client = docker.Client(base_url='unix://var/run/docker.sock')


def get_containers():
    containers = client.containers(all=True, filters={
        'status': 'running'
    })
    for container in containers:
        ip_address = container['NetworkSettings']['Networks']['bridge']['IPAddress']
        container_ports = ports(container['Ports'])
        container_id = container['Id'][:8]
        print(
            'Container with id: ' + container_id + ', on ip ' + ip_address + ', on port/s: ' + ', '.join(
                container_ports))
    print()


def ports(container_ports):
    public_ports = []
    for port in container_ports:
        public_ports = port['PublicPort']
    return public_ports


def start(container_id):
    container = client.inspect_container(container_id)
    ipaddress = container['NetworkSettings']['Networks']['bridge']['IPAddress']
    exp_ports = container['NetworkSettings']['Ports']
    env = container['Config']['Env']
    ports = []
    ports_str = 'no ports'

    for port in exp_ports:
        if exp_ports[port] is not None:
            ports[:0] = [exp_ports[port][0]['HostPort']]

    if ports:
        ports_str = ', '.join(ports)
        # data(container_id, ports, env)

    print('Started container with id: ' + container_id)
    print(
        'Container ' + container['Config']['Hostname'] + ', is on ip ' + ipaddress + ', and port/s ' + ports_str)
    print(json.dumps(client.containers(all=True, filters={
        'status': 'running'
    })))


def destroy(container_id):
    print('Destroyed container with id: ' + container_id)


def data(container_id, ports, env):
    add_host = True
    nginx_config = sort_env(env)

    with open('data.json', 'r') as f:
        json_data = json.load(f)

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
    print([{'ports': ports}, {'config': config}])
    json_data = json_data.append([{'ports': ports}, {'config': config}])
    print(json_data)
    with open('data.json', 'w') as f:
        json.dump(json_data, f)


for event in client.events():
    event = json.loads(event)
    if 'Action' in event.keys() and 'id' in event.keys():
        if 'start' in event['Action']:
            get_containers()
        if 'destroy' in event['Action']:
            destroy(event['id'])
