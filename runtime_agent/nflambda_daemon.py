import time
import socket

from configuration import runtime_path_loader, parameter_loader

# nflambda_daemon.py is the daemon that controls the start/stop of nflambda_runtime
nflambda_runtime_path = runtime_path_loader()
parameters = parameter_loader()

import os
import psutil

process_name = nflambda_runtime_path.split("/")[-1]


def run_nflambda_runtime():
    os.system("sudo " + nflambda_runtime_path + " " + parameters + " &")


def kill_nflambda_runtime():
    os.system("sudo pkill " + process_name)


def is_process_running(process_name):
    for process in psutil.process_iter():
        try:
            if process.name() == process_name:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--kill", action="store_true", help="kill the daemon")
    args = parser.parse_args()
    if args.kill:
        kill_nflambda_runtime()
        exit(0)
    UDP_IP = "0.0.0.0"
    UDP_PORT = 5005

    # create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # bind the socket to a specific IP address and port
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        # receive data from the socket
        data, addr = sock.recvfrom(1024)
        result = data.decode("utf-8")
        match result:
            case "start":
                print("start")
                # first check if the runtime_agent is already running
                if is_process_running(process_name):
                    sock.sendto(b"already running", addr)
                    continue
                run_nflambda_runtime()
                n = 0
                while not is_process_running(process_name):
                    time.sleep(0.1)
                    n += 1
                    if n > 50:
                        sock.sendto(b"failed", addr)
                sock.sendto(b"running", addr)
            case "stop":
                print("stop")
                kill_nflambda_runtime()
                n = 0
                while is_process_running(process_name):
                    time.sleep(0.1)
                    n += 1
                    if n > 50:
                        sock.sendto(b"failed", addr)
                sock.sendto(b"stopped", addr)
            case "status":
                print("status")
                if is_process_running(process_name):
                    sock.sendto(b"running", addr)
                else:
                    sock.sendto(b"stopped", addr)
            case _:
                sock.sendto(b"invalid command", addr)
