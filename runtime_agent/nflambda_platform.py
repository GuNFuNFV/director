import os
import pprint
import sys
import time
from socket import socket, AF_INET, SOCK_STREAM
from typing import Callable, Any, List

from runtime_agent.command import Command, print_command_simulation, command_worker_fsm_amac


from orchestration.resource_orchestration import configuration_analyzer


from runtime_agent.nflambda_client import start_nflambda_runtime, stop_nflambda_runtime

class Host:
    hostname = None

    def __init__(self, hostname=None, runtime_path=None, ip="127.0.0.1", port=8093, nic_list=None, core_list=None):
        self.hostname = hostname
        self.runtime_path = runtime_path
        self.ip = ip
        self.port = port
        self.nic_list = nic_list
        self.core_list = core_list
        self.s = None  # the socket used to connect to the host
        self.available_workers = None
        self.controller = None
        self.nf_set = {}  # the set of nfs that are deployed on the host
        return


debug_mode = False


def red_print(*args, **kwargs):
    global debug_mode
    if debug_mode:
        print("\033[1;31;40m", *args, "\033[0m", flush=True, **kwargs)


# decorator
# command_instance is a function that returns a command
def nflambda_send_command(command_instance: Callable[[Any], Command]) -> Callable[[Any], None]:
    def wrapper(*args, **kwargs):
        self: NFlambda = args[0]
        ret = command_instance(*args, **kwargs)
        if self.offline == False:
            self.connect_runtime()
            response = self.send_command(ret)
            print_command_simulation(ret)
            self.disconnect_runtime()
        else:
            print_command_simulation(ret)
            response = "offline"
        return response

    return wrapper


def nflambda_send_commands(command_instances: Callable[[Any], List[Command]]) -> Callable[[Any], None]:
    def wrapper(*args, **kwargs):
        self: NFlambda = args[0]
        ret = command_instances(*args, **kwargs)
        if self.offline == False:
            self.connect_runtime()
            for i in ret:
                self.send_command(i)
                print_command_simulation(i)
            self.disconnect_runtime()
        else:
            for i in ret:
                print_command_simulation(i)

    return wrapper


class NFlambda:
    username = "ziyan"
    NFLAMBDA_IP = '127.0.0.1'
    NFLAMBDA_PORT = 8093  # Port to listen on (non-privileged ports are > 1023)
    counter = 0
    running_core = []
    data_cores = []
    data_queue_map = {}
    log_path = None
    debug = True
    host_list = []
    offline = False
    # ip pool as a set: 192.168.1.1 - 192.168.1.200
    ip_pool = set()
    for i in range(168, 200):
        ip_pool.add("192.{}.0.1".format(i))

    def __init__(self, *, offline_mode, debug_mode, runtime_setting: dict):
        # pprint.pprint(runtime_setting)
        # get the environment variable HOST_IP
        self.default_host = Host(ip=runtime_setting["ip"])
        self.offline = offline_mode
        self.runtime_setting = runtime_setting
        self.debug_mode = debug_mode

    def configure(self):
        runtime_setting = self.runtime_setting
        if self.offline == False and self.debug_mode == False:
            # start the runtime_agent only when the offline mode is not set and the debug mode is not set
            start_nflambda_runtime(self.default_host.ip)
        self.connect_runtime()
        self.port_init(configuration_analyzer.get_num_queue(runtime_setting))
        for key, value in runtime_setting["WorkerSetting"].items():
            worker_id = key
            worker_config_dict = value
            self.nflambda_instruction("init", [worker_id, configuration_analyzer.get_worker_parameter(worker_config_dict)])
            self.nflambda_instruction("worker_actor_table_init", [worker_id, configuration_analyzer.get_actor_table(worker_config_dict)])
            self.nflambda_instruction("worker_actor_entry_event",
                                      [worker_id, configuration_analyzer.get_actor_entry_event(worker_config_dict)])
            self.nflambda_instructions("control_state_init",
                                       [[worker_id] + i for i in configuration_analyzer.get_control_state_init_parameters(worker_config_dict)])

            self.nflambda_instruction("actor_control_state_association", [worker_id,
                                                                          configuration_analyzer.get_actor_id_control_id_association(
                                                                              worker_config_dict)])

            self.nflambda_instruction("actor_datablock_association", [worker_id,
                                                                      configuration_analyzer.get_actor_id_datablock_id_association(
                                                                          worker_config_dict)])
            self.nflambda_instructions("init_datablock", [[worker_id,i] for i in configuration_analyzer.init_datablocks(worker_config_dict)])

        for key, value in runtime_setting["WorkerSetting"].items():
            worker_id = key
            self.nflambda_instruction("run", [worker_id])
        return

    def get_total_packet(self):
        if self.offline is False:
            total_packet_list_1 = []
            for key, value in self.runtime_setting["WorkerSetting"].items():
                worker_id = key
                total_packet_1 = self.nflambda_instruction("worker_fsm_amac_total_packet", [worker_id])
                total_packet_list_1.append(total_packet_1)
            time.sleep(1)
            total_packet_list_2 = []
            for key, value in self.runtime_setting["WorkerSetting"].items():
                worker_id = key
                total_packet_2 = self.nflambda_instruction("worker_fsm_amac_total_packet", [worker_id])
                total_packet_list_2.append(total_packet_2)
            result = []
            for i in range(len(total_packet_list_1)):
                result.append(int(total_packet_list_2[i]) - int(total_packet_list_1[i]))

            return result
        else:
            return 0

    def stop_runtime(self):
        if self.offline == False:
            stop_nflambda_runtime(self.default_host.ip)

    def connect_runtime(self, host: Host = None):
        red_print("connecting runtime_agent...")
        if self.offline:
            return
        if host is None:
            host = self.default_host
        # dprint("connecting runtime_agent...")
        host.s = socket(AF_INET, SOCK_STREAM)
        count = 0
        result = None
        while result is None:
            try:
                host.s.connect(
                    (host.ip,
                     host.port))  # always throws Con Refused when tryed
                data = host.s.recv(1024)
                host.counter = 0
                result = True
            except Exception as e:
                time.sleep(1)
                count = count + 1
                if (count == 10):
                    # print(e)
                    raise ValueError('dont know __init__')
        self.host_list.append(host)
        self.default_host = host
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect_runtime(self.default_host)

    def disconnect_runtime(self, host: Host = None):
        if host is None:
            host = self.default_host
        host.s.close()
        host.s = None

    def send_command(self, command, host=None):
        if host is None:
            host = self.default_host
        count = 0
        try:
            host.s.sendall(command.apply())
            data = host.s.recv(1024)
            while (data == None):
                data = host.s.recv(1024)
                count = count + 1
                time.sleep(1)
                if (count == 10):
                    raise ValueError('10 seconds with no response')

            # if (host.debug == True):
            #     print(data.decode())
            # dprint(data.decode())
            return data.decode()

        except:
            result = None
            while result is None:
                try:
                    # connect
                    host.s.connect(
                        (host.ip,
                         host.port))  # always throws Con Refused when tryed

                    # print("Connected")
                    host.s.sendall(command.apply())
                    # self.s.settimeout(10)
                    data = host.s.recv(1024)
                    result = True
                    return data.decode()

                except:
                    time.sleep(1)
                    count = count + 1
                    if (count == 5):
                        self.disconnect_runtime(host)
                        raise ValueError('dont know send_command')

    @nflambda_send_command
    def nflambda_instruction(self, instruction, instruction_parameter):
        red_print("{}...".format(instruction))
        argument_list = []
        for item in instruction_parameter:
            if type(item) == dict:
                # convert it into json string
                import json
                json_string = json.dumps(item)
                # remove space
                json_string = json_string.replace(" ", "")
                argument_list.append(json_string)
            else:
                argument_list.append(str(item))
        command = command_worker_fsm_amac.with_argument([instruction] + argument_list)
        return command

    @nflambda_send_commands
    def nflambda_instructions(self, instruction, worker_parameters_list):
        try:
            command_list = []
            for worker_parameters in worker_parameters_list:
                argument_list = []
                argument_list.append(instruction)
                for item in worker_parameters:
                    if type(item) == dict:
                        # convert it into json string
                        import json
                        json_string = json.dumps(item)
                        # remove space
                        json_string = json_string.replace(" ", "")
                        argument_list.append(json_string)
                    else:
                        argument_list.append(str(item))
                command = command_worker_fsm_amac.with_argument(argument_list)
                command_list.append(command)
            return command_list
        except Exception as e:
            print(e)
            raise ValueError("nflambda_instructions")

    @nflambda_send_command
    def port_init(self, num_queue=1) -> Command:
        red_print("port_init...")
        command = command_worker_fsm_amac.with_argument(
            ["port_init", str(num_queue)])
        return command
    #
    # @nflambda_send_command
    # def run_amac_fsm(self, worker_fsm):
    #     red_print("run_amac_fsm...")
    #     command = command_worker_fsm_amac.with_argument(["run_amac_fsm", str(worker_fsm.id)])
    #     return command
    #
