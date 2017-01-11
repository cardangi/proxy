import docker
import json

client = docker.Client(base_url='unix://var/run/docker.sock')

hosts = []


def get_containers():
    containers = client.containers(all=True, filters={
        'status': 'running'
    })
    print('')
    for container in containers:
        network = container['NetworkSettings']['Networks']
        ip_address = 'None'
        if 'bridge' in network.keys():
            ip_address = network['bridge']['IPAddress']
        container_ports = ports(container['Ports'])
        container_id = container['Id'][:12]
        print(
            'Container with id: ' + container_id + ', on ip ' + ip_address + ', on port/s: ' + ', '.join(
                container_ports))
        group_containers_by_env(container_id, container_ports, ip_address)


def group_containers_by_env(container_id, container_ports, ip_address):
    if 0 in container_ports:
        container = client.inspect_container(container_id)
        env = container['Config']['Env']
        env = sort_env(env)
        print(ip_address + ':' + container_ports[0])
        hosts[env[1]] = None


def ports(container_ports):
    public_ports = []
    for port in container_ports:
        private_port = str(port['PrivatePort'])
        if 'PublicPort' in port.keys() and 'PrivatePort' in port.keys():
            if '80' in private_port or '8080' in private_port or '8000' in private_port:
                public_ports[:0] = [private_port]
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
