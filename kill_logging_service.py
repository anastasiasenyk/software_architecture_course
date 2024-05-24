import os
import signal
import subprocess


def kill_process_on_port(port):
    try:
        result = subprocess.run(['lsof', '-i', f':{port}'], stdout=subprocess.PIPE, text=True)
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            pid = int(lines[1].split()[1])
            os.kill(pid, signal.SIGTERM)
            print(f'Service on port {port} has been terminated.')
        else:
            print(f'No process found on port {port}.')
    except Exception as e:
        print(f"Error stopping service: {e}")


if __name__ == '__main__':
    port = 5002
    kill_process_on_port(port)
