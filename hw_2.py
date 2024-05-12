import hazelcast
# from hazelcast import HazelcastClient
import threading
import time


def task_1():
    client = hazelcast.HazelcastClient(
        cluster_name="dev",
    )
    d_map = client.get_map("my-distributed-map")
    for i in range(1000):
        d_map.put(str(i), f"{i}_el")
    client.shutdown()


def perform_operations(d_map, function_name, key):
    if function_name == "pessimistic":
        pessimistic_operation(d_map, key)
    elif function_name == "optimistic":
        optimistic_operation(d_map, key)
    elif function_name == "no_lock":
        no_lock_operation(d_map, key)


def pessimistic_operation(d_map, key):
    for _ in range(10000):
        d_map.lock(key)
        try:
            value = d_map.get(key)
            d_map.put(key, value + 1)
        finally:
            d_map.unlock(key)


def optimistic_operation(d_map, key):
    for _ in range(10000):
        while True:
            value = d_map.get(key)
            if d_map.replace_if_same(key, value, value + 1):
                break


def no_lock_operation(d_map, key):
    for _ in range(10000):
        value = d_map.get(key)
        value += 1
        d_map.put(key, value)


def task_2_distributed_with_locks(function_name, key):
    client = hazelcast.HazelcastClient(cluster_name="dev")
    d_map = client.get_map("my-distributed-map").blocking()
    d_map.put(key, 0)

    value = d_map.get(key)
    print("Initial: ", value)

    start_time = time.time()

    threads = []
    for _ in range(3):
        thread = threading.Thread(target=perform_operations, args=(d_map, function_name, key))
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    duration = time.time() - start_time
    print(f"{function_name.capitalize()} operation duration: {duration:.4f} seconds")

    value = d_map.get(key)
    print("Final: ", value)
    client.shutdown()


def task_3(max_size):
    client = hazelcast.HazelcastClient()
    queue = client.get_queue("queue").blocking()

    def produce(max_size):
        for i in range(max_size):
            queue.offer("value-" + str(i))
            print(f'write: {i}')

    def consume():
        while True:
            head = queue.take().result()
            print("consuming: ", str(head))

    producer_thread = threading.Thread(target=produce, args=(max_size, ))
    consumer_thread_1 = threading.Thread(target=consume)
    consumer_thread_2 = threading.Thread(target=consume)

    producer_thread.start()
    consumer_thread_1.start()
    consumer_thread_2.start()

    producer_thread.join()
    consumer_thread_1.join()
    consumer_thread_2.join()

    client.shutdown()


if __name__ == "__main__":
    task_1()

    # task_2_distributed_with_locks("pessimistic", "key")
    # task_2_distributed_with_locks("optimistic", "key")
    # task_2_distributed_with_locks("no_lock", "key")
    #
    # task_3(100)


