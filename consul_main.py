import consul


def set_service(name, id, port):
    consul_client = consul.Consul()
    consul_client.agent.service.register(
        name=name,
        service_id=id,
        address='172.17.0.2',
        port=port,
        tags=['microservice']
    )


def get_service(name):
    consul_client = consul.Consul()
    index, services = consul_client.health.service(name, passing=True)
    addresses = []
    for node in services:
        addresses.append(f"http://{node['Service']['Address']}:{node['Service']['Port']}")
    return addresses


def set_key_value(key, value):
    consul_client = consul.Consul()
    consul_client.kv.put(key, value)


def get_value_by_key(key):
    c = consul.Consul()
    index, data = c.kv.get(key)
    return data['Value'].decode('utf-8')


def main():
    print('set start')

    set_key_value("hazelcast_name", "dev")
    set_key_value("hazelcast_queue", "message-queue")
    set_key_value("hazelcast_map", "distributed-map")

    print(get_value_by_key("hazelcast_name"))
    print(get_service("facade_service"))
    print('set end')


if __name__ == '__main__':
    main()
