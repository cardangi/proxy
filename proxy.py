import docker
import json

client = docker.Client(base_url='unix://var/run/docker.sock')

hosts = {}


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
    print('')
    print(hosts)


def group_containers_by_env(container_id, container_ports, ip_address):
    if container_ports:
        container = client.inspect_container(container_id)
        env = container['Config']['Env']
        print(env)
        env = sort_env(env)
        if 'VIRTUAL_HOST' in env.keys():
            if env['VIRTUAL_HOST'] not in hosts.keys():
                hosts[env['VIRTUAL_HOST']] = {
                    'ip': [],
                    'https': 'True'
                }
            hosts[str(env['VIRTUAL_HOST'])]['ip'][:0] = [ip_address + ':' + container_ports[0]]
            hosts[str(env['VIRTUAL_HOST'])]['https'] = env['HTTPS']


def ports(container_ports):
    public_ports = []
    for port in container_ports:
        if 'PublicPort' in port.keys() and 'PrivatePort' in port.keys():
            private_port = str(port['PrivatePort'])
            public_port = str(port['PublicPort'])
            if '80' in private_port or '8080' in private_port or '8000' in private_port:
                public_ports[:0] = [public_port]
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


def sort_env(env):
    nginx_config = {}
    for env_var in env:
        environment = {env_var.split('=')[0]: env_var.split('=')[1]}
        if 'VIRTUAL_HOST' in environment.keys():
            nginx_config['VIRTUAL_HOST'] = environment['VIRTUAL_HOST']
        if 'LETSENCRYPT_EMAIL' in environment.keys():
            nginx_config['LETSENCRYPT_EMAIL'] = environment['LETSENCRYPT_EMAIL']
        if not 'HTTPS' in environment.keys():
            nginx_config['HTTPS'] = True
    return nginx_config


for event in client.events():
    event = json.loads(event)
    if 'Action' in event.keys() and 'id' in event.keys():
        if 'start' in event['Action']:
            get_containers()
        if 'destroy' in event['Action']:
            destroy(event['id'])
