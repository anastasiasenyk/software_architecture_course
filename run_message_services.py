import subprocess


def run_message_service_instances(ports):
    processes = []

    for port in ports:
        process = subprocess.Popen(['python', 'LoggingService.py', str(port)])
        processes.append(process)

    for process in processes:
        process.wait()


if __name__ == '__main__':
    ports = [5001, 5005]
    run_message_service_instances(ports)
