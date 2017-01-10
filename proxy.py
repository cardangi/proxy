import docker


def main():
    client = docker.Client(base_url='unix://var/run/docker.sock')
    for event in client.events():
        print(event)
        if event['status'] is 'created':
            return created()

        if event['status'] is 'removed':
            return removed()


def created():
    return 'Created'


def removed():
    return 'Removed'


if __name__ is '__main__':
    main()
