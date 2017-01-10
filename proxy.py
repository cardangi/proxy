import docker


def main():
    client = docker.Client(base_url='unix://var/run/docker.sock')
    for event in client.events():
        print(event)
        


def created():
    return 'Created'


def removed():
    return 'Removed'


main()
