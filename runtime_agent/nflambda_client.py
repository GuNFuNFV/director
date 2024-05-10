import socket
import time

import os
import psutil
import sys




def is_process_running(process_name):
    for process in psutil.process_iter():
        try:
            if process.name() == process_name:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def get_internet_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def is_valid_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def check_daemon_is_running(ip):
    UDP_IP = "0.0.0.0"
    UDP_PORT = 5000
    UDP_PORT2 = 5005

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.sendto("status".encode("utf-8"), (ip, UDP_PORT2))
    # receive data from the socket, timeout after 1 second
    data, addr = sock.recvfrom(1024)
    time_elapsed = 0
    while data is None:
        time.sleep(0.1)
        # non-blocking receive
        data, addr = sock.recvfrom(1024)
        time_elapsed += 0.1
        if time_elapsed > 1:
            return False
    # close the socket
    sock.close()
    return True # don't care about the result


def start_nflambda_runtime(ip):
    daemon_running = check_daemon_is_running(ip)
    if daemon_running is False:
        raise Exception("NFlambda daemon is not running")
    UDP_IP = "0.0.0.0"
    UDP_PORT = 5000
    UDP_PORT2 = 5005

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.sendto("start".encode("utf-8"), (ip, UDP_PORT2))
    # receive data from the socket
    data, addr = sock.recvfrom(1024)
    command_result = data.decode("utf-8")
    sock.close()
    match command_result:
        case "running":
            # print("NFlambda runtime_agent is running")
            return True
        case "failed":
            print("Failed to start NFlambda runtime_agent")
            raise Exception("Failed to start NFlambda runtime_agent")
        case "already running":
            print("NFlambda runtime_agent is already running")
            raise Exception("NFlambda runtime_agent is already running")
        case _:
            print("Unknown error")
            exit(1)



def stop_nflambda_runtime(ip):
    result = check_daemon_is_running(ip)
    if result is False:
        raise Exception("NFlambda daemon is not running")
    UDP_IP = "0.0.0.0"
    UDP_PORT = 5000
    UDP_PORT2 = 5005

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.sendto("stop".encode("utf-8"), (ip, UDP_PORT2))
    # receive data from the socket
    data, addr = sock.recvfrom(1024)
    result = data.decode("utf-8")
    sock.close()
    match result:
        case "stopped":
            print("NFlambda runtime_agent is stopped")
        case "failed":
            print("Failed to stop NFlambda runtime_agent")
        case "already stopped":
            print("NFlambda runtime_agent is already stopped")
        case _:
            print("Unknown error")


if __name__ == "__main__":
    print(get_internet_ip())
    # get the command line arguments
    # the first command is the ip address of the nflambda_daemon
    # the second command is the command to send to the daemon
    # example usage:
    # python3 nflambda_client.py 128.101.118.41 start
    # python3 nflambda_client.py 128.101.118.41 stop
    # python3 nflambda_client.py 128.101.118.41 status

    if len(sys.argv) != 3:
        print("Usage: python3 nflambda_client.py <daemon_ip> <command>")
        exit(1)

    daemon_ip = sys.argv[1]
    command = sys.argv[2]
    try:
        assert is_valid_ip(daemon_ip)
        assert command in ["start", "stop", "status"]
    except:
        print("Invalid command")
        exit(1)
    UDP_IP = "0.0.0.0"
    UDP_PORT = 5000
    UDP_PORT2 = 5005

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.sendto(command.encode("utf-8"), (daemon_ip, UDP_PORT2))
    # receive data from the socket
    data, addr = sock.recvfrom(1024)
    result = data.decode("utf-8")
    match result:
        case "running":
            print("NFlambda runtime_agent is running")
        case "stopped":
            print("NFlambda runtime_agent is stopped")
        case "failed":
            print("Failed to start/stop NFlambda runtime_agent")
        case "invalid command":
            print("Invalid command")
            print(result)
        case "already running":
            print("NFlambda runtime_agent is already running")
            print("kill it first if you want to start a new one")
        case _:
            print("Invalid response from daemon")
