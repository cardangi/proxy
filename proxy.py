import docker

client = docker.Client(base_url='unix://var/run/docker.sock')
for event in client.events():
    print('Status:' + event['status'] + ', on container with ID: ' + event['id'])
