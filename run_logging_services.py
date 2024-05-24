import subprocess


def run_logging_service_instances(ports):
    processes = []

    for port in ports:
        process = subprocess.Popen(['python', 'LoggingService.py', str(port)])
        processes.append(process)

    for process in processes:
        process.wait()


if __name__ == '__main__':
    ports = [5002, 5003, 5004]
    run_logging_service_instances(ports)
