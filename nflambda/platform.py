import os
import socket
import time
from typing import List, Any, Callable

# from nf_model import deployment_model
# from nf_model.nf_model import Action_instance_execution, State_instance_execution
from nf_model import *
from nf_state_machine import WorkerFSM, NFType
from utility import dic_to_configuration_string, red_print
from . import get_microarchitecture_snapshot
from .command import *
from orchestration import *
import subprocess


# NFlambda is the interface to the NFlambda runtime_agent and orchestrator
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

    def __init__(self, host_ip, offline_mode=False):
        # get the environment variable HOST_IP
        self.default_host = Host(ip=host_ip)
        self.offline = offline_mode
        # self.connect_runtime()
        # self.get_available_worker()
        return

    def start_runtime(self, host: Host):
        if self.is_running(host):
            print("kill the runtime_agent first")
            return -1
            # self.kill_runtime(host)
            # time.sleep(1)
        print("starting runtime_agent...")
        allow_list = ""
        if host.nic_list is None:
            print("no nic is available")
            return -1
        for i in host.nic_list:
            allow_list += " -a " + i

        core_list = str(host.core_list[0])
        if host.core_list is None:
            print("no core is available")
            return -1
        for i in host.core_list[1:]:
            core_list += "," + str(i)
        # print( '''ssh {} "nohup sudo {} {} -l {} > foo.out 2> foo.err < /dev/null &"'''.format(
        #         host.hostname, host.runtime_path, allow_list, core_list))
        os.system(
            '''ssh {} "nohup sudo {} {} -l {} > foo.out 2> foo.err < /dev/null &"'''.format(
                host.hostname, host.runtime_path, allow_list, core_list)
        )
        time.sleep(1)
        return 1

    def kill_runtime(self, host: Host = None):
        if self.is_running(host):
            # print("here")
            # os.system(
            #     ''' ssh {} "sudo kill -9 `ps aux | grep nf_p | sed -n '2 p' | awk '{{print $2}}'`" '''.format(
            #         host.hostname)
            # )
            # os.system(
            #     ''' ssh {} "sudo kill -9 `ps aux | grep nf_p | sed -n '3 p' | awk '{{print $2}}'`" '''.format(
            #         host.hostname)
            # )

            pid = subprocess.Popen(
                ''' ssh {} "ps aux | grep nf_p | sed -n '2 p' | awk '{{print $2}}' "'''.format(host.hostname),
                shell=True,
                stdout=subprocess.PIPE).stdout
            pid = (pid.read())
            pid = (int)(pid.split()[1])
            # print(''' ssh {} "sudo kill -9 {}"'''.format(host.hostname, pid))
            subprocess.Popen(''' ssh {} "sudo kill -9 {}"'''.format(host.hostname, pid), shell=True,
                             stdout=subprocess.PIPE).stdout

            return 1
        else:
            return -1

    def is_running(self, host: Host):
        # print(''' ssh {} " ps aux | grep nf_p  | grep -v grep | wc -l"'''.format(host.hostname))
        getVersion = subprocess.Popen(''' ssh {} " ps aux | grep nf_p  | grep -v grep | wc -l"'''.format(host.hostname),
                                      shell=True,
                                      stdout=subprocess.PIPE).stdout
        value = int(getVersion.read())
        # print(value)
        if value == 0:
            return False
        else:
            return True

    def connect_runtime(self, host: Host = None):
        if host is None:
            host = self.default_host
        dprint("connecting runtime_agent...")
        host.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        dprint("disconnecting runtime_agent...")
        host.s.close()
        host.s = None

    def __init_test__(self, start=True, runtime_path=None):
        self.runtime_path = self.default_runtime_path
        if (runtime_path != None):
            self.runtime_path = runtime_path
        # assert set(data_cores) <= set(running_core)
        if (start == True):
            self.kill_runtime()
            time.sleep(0.2)
            self.start_runtime()
            time.sleep(0.2)

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = self.NFLAMBDA_IP
        self.port = self.NFLAMBDA_PORT
        # Connect the socket to the port where the server is listening
        server_address = (self.ip, self.port)
        count = 0
        result = None
        time.sleep(1)
        while result is None:
            try:
                self.s.connect(
                    (self.ip,
                     self.port))  # always throws Con Refused when tryed
                data = self.s.recv(1024)
                self.counter = 0
                result = True
            except Exception as e:
                time.sleep(1)
                count = count + 1
                if (count == 5):
                    # print(e)
                    raise ValueError('dont know __init__')

        # self.parameter = Parameter()
        # self.parameter.d["state_size"] = 1000000
        # self.parameter.d["data_state"] = 1000
        # self.parameter.d["control_state"] = 100
        # self.parameter.d["control_frequency"] = 100
        # self.parameter.d["control_complexity"] = 500
        # self.configure_parameter(self.parameter)

        self.log_pd = None

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

    def controller_worker(self, worker, action, host):
        # tell the worker that for this particular action, it should execute the function locally
        dprint("Scheduling worker {} to execute action {} locally".format(worker, action))
        response = self.send_command(command_worker.with_argument(["controller", "local", str(worker), action]), host)
        return response

    def controller_workers(self, host):
        for worker in host.available_workers:
            for nf in host.nf_set:
                for action in host.nf_set[nf].actions:
                    dprint("control worker {} to execute action {} locally".format(worker, action.name))
                    response = self.controller_worker(worker.core_id, action, host)
                    dprint(response)
        return

    def configure_worker_controller(self, worker_id, host):
        worker = host.available_workers[worker_id]
        dprint("Configuring worker {} to execute actions locally".format(worker))
        c_d: Controller_descriptor
        for c_d in worker.controller.controller_descriptors:
            dprint("install {} on worker {}".format(c_d, worker))

            # insert the controller descriptor in the worker
            response = self.send_command(
                command_worker.with_argument(["controller", "install", str(worker.core_id), c_d.action.name]), host)

            dprint(response)
            # how to get the predicate for this particular action?
            from packet_model import Packet
            # if c_d.action.predicate.n_field > 0:
            #     predicate_id = c_d.predicate_id
            #     dprint("install predicate {} for action{} on worker {}".format(predicate_id,c_d.action.name, worker))
            #     response = self.send_command(
            #         command_worker.with_argument(
            #             ["controller", "predicate", str(worker.core_id), c_d.action.name, str(predicate_id)]), host)
            # else:
            #     response = self.send_command(
            #         command_worker.with_argument(
            #             ["controller", "predicate", str(worker.core_id), c_d.action.name, "-1"]), host)

            # given the descriptor, install the state offset
            for i in c_d.action.state:
                if i.type == "nflow":
                    # worker_id, action_name, state_id, offset
                    index = c_d.action.state.index(i)
                    offset = worker.nflow_template.return_offset_by_name(i.name)
                    state_name = worker.nflow_template.return_state_name_by_index(index)
                    response = self.send_command(command_worker.with_argument(
                        ["controller", "nflow_template", str(worker.core_id), c_d.action.name, str(index),
                         str(state_name),
                         str(offset)]), host)
                    dprint(response)
                if i.type == "shared_state":
                    # worker_id, action_name, state_id, offset
                    state_id = worker.shared_state_template.return_state_index(i)
                    offset = worker.shared_state_template.return_offset(state_id)
                    response = self.send_command(command_worker.with_argument(
                        ["controller", "shared_state", str(worker.core_id), c_d.action.name, str(state_id),
                         str(offset)]), host)
                    dprint(response)
                if i.type == "global_state":
                    # worker_id, action_name, state_id, offset
                    state_id = worker.global_state_template.return_state_index(i)
                    offset = worker.global_state_template.return_offset(state_id)
                    response = self.send_command(command_worker.with_argument(
                        ["controller", "global_state", str(worker.core_id), c_d.action.name, str(state_id),
                         str(offset)]), host)
                    dprint(response)

    def initialize_workers_nflow_pool(self, nflow_size, nflow_num, predicate_size, host):
        for worker in host.available_workers:
            response = self.initialize_worker_nflow_pool(worker.core_id, nflow_size, nflow_num, predicate_size, host)
            dprint(response)
        return

    def initialize_worker_nflow_pool(self, worker_id, host):
        worker: Worker = host.available_workers[worker_id]
        nflow = worker.nflow
        nflow_size = 200
        nflow_num = 10000
        response = self.send_command(command_worker.with_argument(
            ["nflow_pool", "initialize", str(worker.core_id), str(nflow_size), str(nflow_num)]),
            host)
        dprint(response)
        for predicate in nflow.predicate_collection:
            predicate_size = predicate.total_size
            predicate_index = nflow.predicate_collection.index(predicate)
            response = self.send_command(command_worker.with_argument(
                ["nflow_pool", "initialize_indirect_table", str(worker.core_id), str(predicate_size),
                 str(predicate_index)]), host)
            for i in range(predicate.n_field):
                response = self.send_command(command_worker.with_argument(
                    ["nflow_pool", "initialize_predicate_descriptor", str(worker.core_id), str(predicate_index),
                     str(predicate.offset_list[i]), str(predicate.length_list[i]), str(i)]), host)
            dprint(response)

    def destroy_worker_nflow_pool(self, worker_id, host):
        worker = host.available_workers[worker_id]
        response = self.send_command(command_worker.with_argument(
            ["nflow_pool", "destroy", str(worker.core_id)]), host)
        return response

    def insert_nflow(self, worker_id, action_name, predicate, host):
        worker = host.available_workers[worker_id]
        response = self.send_command(command_worker.with_argument(
            ["nflow_pool", "insert", str(worker.core_id), str(action_name), str(predicate)]), host)
        return response

    def assign_nflow_value_to_field(self, worker_id, predicate, field_name, value, host):
        worker = host.available_workers[worker_id]
        offset = worker.nflow_template.return_offset_by_name(field_name)
        dprint("offset of {} is {}".format(field_name, offset))
        response = self.send_command(command_worker.with_argument(
            ["nflow_pool", "assign", str(worker.core_id), str(predicate), str(offset), str(value)]), host)
        return response

    def get_nflow_value_from_field(self, worker_id, predicate, field_name, host):
        worker = host.available_workers[worker_id]
        offset = worker.nflow_template.return_offset_by_name(field_name)
        response = self.send_command(command_worker.with_argument(
            ["nflow_pool", "get", str(worker.core_id), str(predicate), str(offset)]), host)
        # extract the first integer from the response
        for i in response.split():
            if i.isdigit():
                return int(i)
        return int(response.split(" ")[0])

    def initailize_worker_shared_state(self, worker_id, size, host):
        worker = host.available_workers[worker_id]
        response = self.send_command(command_worker.with_argument(
            ["shared_state", "initialize", str(worker.core_id), str(size)]), host)
        return response

    def assign_shared_state(self, worker_id, share_state_name, value, host):
        worker = host.available_workers[worker_id]
        shared_state_offset = worker.shared_state_template.return_offset_by_name(share_state_name)
        dprint("Assigning shared state {} to worker {}, and offset is {}".format(share_state_name, worker,
                                                                                 shared_state_offset))
        response = self.send_command(
            command_worker.with_argument(
                ["shared_state", "assign", str(worker.core_id), str(shared_state_offset), str(value)]), host)
        return response

    def worker_instruction(self, worker_id=0, predicate=0, predicate_name=None, functiona_name=None, host=None):
        worker = host.available_workers[worker_id]
        if predicate_name is not None:
            offset = worker.nflow_template.return_offset_by_name(predicate_name)
        else:
            offset = 0  # don't care the value
        response = self.send_command(
            command_worker.with_argument(
                ["instruction", str(worker.core_id), str(predicate), str(offset), str(functiona_name)]), host)
        return response

    def load_nf(self, host, nf):

        nf_dic = NF(nf)
        # self.nf_set[nf] = nf_dic
        host.nf_set[nf] = nf_dic
        filepath = nf_dic.filepath
        if filepath == "local":
            dprint("Loading NF {} from local".format(nf))
            exit()
        response = self.send_command(command_nf.with_argument(["load", filepath]), host)
        # action_list = response.split(",")
        # nf_dic["action_list"] = action_list

    def workers_run(self, host):
        response = self.send_command(command_worker.with_argument(["run"]), host)
        return response

    def worker_fsm_test(self, host):
        response = self.send_command(command_worker_fsm.with_argument(["test"]), host)
        return response

    def worker_fsm_command_fsm_state_table(self, host, worker_fsm_id, action_name, index):
        response = self.send_command(command_worker_fsm.with_argument(["fsm_state_table", str(worker_fsm_id),
                                                                       str(action_name), str(index)]), host)
        return response

    def worker_fsm_install_actions(self, worker_fsm: WorkerFSM):
        for action in worker_fsm.actor_table:
            # remove the stars in the end of the action
            action_name = action.split("*")[0]
            self.worker_fsm_command_fsm_state_table(self.default_host, worker_fsm.id, action_name,
                                                    worker_fsm.actor_table.index(action))
        return

    # def worker_fsm_command_global_transition_table(self, host, worker_fsm_id, state_index, transition_index):
    #     response = self.send_command(command_worker_fsm.with_argument(["global_transition_table", str(worker_fsm_id),
    #                                                                    str(state_index), str(transition_index)]), host)
    #     return response
    # #
    # def worker_fsm_install_global_transition_table(self, worker_fsm: WorkerFSM):
    #     for transition in worker_fsm.global_transition_table:
    #         end_state = transition.to_state
    #         # get the index of the end state in the action list
    #         end_state_index = worker_fsm.action_list.index(end_state.name)
    #         # index of transition in the global transition table
    #         transition_index = worker_fsm.global_transition_table.index(transition)
    #         self.worker_fsm_command_global_transition_table(self.default_host, worker_fsm.id, end_state_index,
    #                                                         transition_index)
    #     return

    def worker_fsm_install_local_transition_table(self, worker_fsm: WorkerFSM):
        for state_name in worker_fsm.local_index:
            for local_transition_table_index in range(len(worker_fsm.local_index[state_name])):
                action_index = worker_fsm.local_index[state_name][local_transition_table_index][1]
                state_index = worker_fsm.actor_table.index(state_name)
                self.send_command(command_worker_fsm.with_argument(["local_transition_table", str(worker_fsm.id),
                                                                    str(state_index), str(local_transition_table_index),
                                                                    str(action_index)]),
                                  self.default_host)
                print("Installing local transition table for state {} and index {}: action {}".format(state_name,
                                                                                                      local_transition_table_index,
                                                                                                      action_index))
        return

    def worker_fsm_install_nflow(self, worker_fsm: WorkerFSM):
        # first get how many cache lines
        n_cache_lines = len(worker_fsm.data_layout)
        self.send_command(command_worker_fsm.with_argument(["nflow", str(worker_fsm.id), str(n_cache_lines)]),
                          self.default_host)
        self.worker_fsm_install_state_variables_offset(worker_fsm)
        return

    def worker_fsm_install_state_variables_offset(self, worker_fsm: WorkerFSM):
        for state_variable_name in worker_fsm.flow_state_variables:
            state_variable = worker_fsm.flow_state_variables[state_variable_name]
            # get the offset of the state form_variable.py in the cache line
            offset = 0
            for cache_line in worker_fsm.data_layout:
                offset = cache_line.get_offset(state_variable)
                if offset == -1:
                    continue
            assert offset != -1, "State variable {} is not in the cache line".format(state_variable_name)
            action_id = worker_fsm.actor_table.index(state_variable.fsm_state_name)
            self.send_command(
                command_worker_fsm.with_argument(["state_variables", str(worker_fsm.id), str(action_id), str(offset)]),
                self.default_host)
        return

    def worker_fsm_initialize(self, worker_fsm: WorkerFSM = None):
        # TODO: change all configurations into key value pairs
        host = self.default_host
        if worker_fsm.working_mode == "local_rtc_hash" or worker_fsm.working_mode == "local_interleaved_hash":
            parameters = []
            worker_id = worker_fsm.id
            concurrency = worker_fsm.concurrency
            working_mode = worker_fsm.working_mode
            num_interleaved = worker_fsm.num_interleaved
            parameters.append(str(worker_id))
            parameters.append(str(concurrency))
            parameters.append(str(working_mode))
            parameters.append(str(num_interleaved))
            response = self.send_command(command_worker_fsm.with_argument(["initialize_local_hash"] + parameters),
                                         host)
        elif worker_fsm.working_mode == "local_rtc_mdi_tree" or worker_fsm.working_mode == "local_interleaved_mdi_tree":
            parameters = []
            worker_id = worker_fsm.id
            concurrency = worker_fsm.concurrency
            working_mode = worker_fsm.working_mode
            num_interleaved = worker_fsm.num_interleaved
            depth = worker_fsm.depth
            parameters.append(str(worker_id))
            parameters.append(str(concurrency))
            parameters.append(str(working_mode))
            parameters.append(str(num_interleaved))
            parameters.append(str(depth))
            response = self.send_command(command_worker_fsm.with_argument(["initialize_local_mdi_tree"] + parameters),
                                         host)
        else:
            parameters = []
            worker_id = worker_fsm.id
            concurrency = worker_fsm.concurrency
            working_mode = worker_fsm.working_mode
            complexity = worker_fsm.complexity
            parameters.append(str(worker_id))
            parameters.append(str(concurrency))
            parameters.append(str(working_mode))
            parameters.append(str(complexity))
            response = self.send_command(command_worker_fsm.with_argument(["initialize"] + parameters),
                                         host)
        return response

    def worker_fsm_start(self, worker_fsm: WorkerFSM = None):
        worker_id = worker_fsm.id
        host = self.default_host
        response = self.send_command(command_worker_fsm.with_argument(["run", str(worker_id)]),
                                     host)
        return response

    def worker_fsm_concurrency(self, worker_fsm: WorkerFSM = None, concurrency=1):
        worker_id = worker_fsm.id
        host = self.default_host
        response = self.send_command(
            command_worker_fsm.with_argument(["concurrency", str(worker_id), str(concurrency)]),
            host)
        return response

    def worker_fsm_complexity(self, worker_fsm: WorkerFSM = None, complexity=1):
        worker_id = worker_fsm.id
        host = self.default_host
        response = self.send_command(command_worker_fsm.with_argument(["complexity", str(worker_id), str(complexity)]),
                                     host)
        return response

    def worker_fsm_throughput(self, worker_id=0):
        host = self.default_host
        response = self.send_command(command_worker_fsm.with_argument(["throughput", str(worker_id)]), host)

        return response

    def worker_fsm_performance(self, worker_id=0):
        host = self.default_host
        response = self.send_command(command_worker_fsm.with_argument(["performance", str(worker_id)]), host)
        return response

    def worker_fsm_dump(self, worker_fsm: WorkerFSM = None):
        worker_id = worker_fsm.id
        host = self.default_host
        response = self.send_command(command_worker_fsm.with_argument(["dump", str(worker_id)]), host)
        return response

    def worker_fsm_stop(self, host=None, worker_id=0):
        if host is None:
            host = self.default_host
        response = self.send_command(command_worker_fsm.with_argument(["stop", str(worker_id)]), host)
        return response

    def exit(self, host):
        response = self.send_command(command_exit.with_argument([]), host)
        self.disconnect_runtime(host)
        return response

    def get_available_worker(self, host: Host = None):
        if host is None:
            host = self.default_host
        # nflambda.send_command(command_worker.with_argument(["run"]), host)
        response = self.send_command(command_worker.with_argument(["available"]), host)
        # split the response using the delimiter ,
        # transform the string to int
        available_worker = [int(x) for x in response.split(",")]
        # for each worker in the list
        # map the worker to an instance of the class Worker
        dprint("Available workers: {}".format(available_worker))
        available_worker = [Worker(x) for x in available_worker]
        host.available_workers = available_worker

    def allocate_worker_ip(self, host):
        for worker in host.available_workers:
            # take one ip from the list of available ips
            ip = self.ip_pool.pop()
            # allocate the ip to the worker
            worker.ip = ip
            self.send_command(command_worker.with_argument(["ip", str(worker.core_id), str(ip)]), host)

    def set_default_action(self, worker_id, default_action, host):
        worker = host.available_workers[worker_id]
        response = self.send_command(command_worker.with_argument(
            ["default_action", "set", str(worker.core_id), str(default_action)]), host)
        return response

    def start_port(self, host):
        self.send_command(command_port.with_argument(["init"]), host)

    def start_pcm(self):
        os.system(
        )
        return

    def kill_pcm(self):
        os.system(
        )
        return

    def run(self, host):
        #
        self.start_port(host)
        self.configure_rss(host)
        print("run")
        self.send_command(command_worker.with_argument(["run"]), host)

    def register_action(self, filename, action_name):
        self.send_command(command_action.with_argument(["register", filename, action_name]))

    def worker_first_action(self, worker_id, action_id, starting_bucket, num_bucket):
        self.send_command(command_worker.with_argument(
            ["first_action", str(worker_id), str(action_id), str(starting_bucket), str(num_bucket)]))

    def install_simple_path(self, state_id_1, action_id_2, local_path_id):
        self.send_command(command_state.with_argument(
            ["install_simple_path", str(state_id_1), str(action_id_2), str(local_path_id)]))

    def create_packet_out_action(self, action_index, core_id):
        self.send_command(command_action.with_argument(
            ["create_packet_out", str(action_index), str(core_id)]))

    # def migrate_action(self, a_i_e, action_index):
    #     self.send_command(command_action.with_argument(["migrate", str(action_index), str(a_i_e.core_id)]))

    def state_num_flows(self, state_id, num_flows):
        self.send_command(
            command_state.with_argument(["data_state", str(state_id), str(num_flows)]))

    def configure_rss_reta(self, starting_bucket, num_bucket, core_id, action_id):
        self.send_command(
            command_config.with_argument(
                ["rss_reta_config", str(starting_bucket), str(num_bucket), str(core_id), str(action_id)]))

    def configure_rss(self, host):
        self.send_command(command_config.with_argument(["rss"]), host)

    def dump_worker(self):
        self.send_command(command_dump.with_argument(["worker_stat"]))

    def configure_parameter(self, parameter):
        self.send_command(command_config.with_argument(["parameter", parameter.to_string()]))

    def configure_state(self, state_key, state_id, val):
        return self.send_command(command_state.with_argument([str(state_key), str(state_id), str(val)]))

    def dump_message_num(self, state_id):
        return self.send_command(command_state.with_argument(["message_num", str(state_id)]))

    def exp_generic_decomposed(self):
        pass

    def get_snapshot(self, sampling_time):
        time.sleep(sampling_time)
        v1 = (int)(self.send_command(command_dump.with_argument(["stat"])))
        time.sleep(sampling_time)
        v2 = (int)(self.send_command(command_dump.with_argument(["stat"])))
        snapshot = get_microarchitecture_snapshot()
        result = {}
        result["throughput"] = (v2 - v1) / 1000000000 * 84 / 64 / sampling_time
        return result | snapshot

    def update_parameter(self):
        # self.parameter.d["data_state"] = 20000
        self.configure_parameter(self.parameter)
        for i in self.actor_graph.state_runtime_table.data:
            state_id = self.actor_graph.state_runtime_table.data.index(i)
            self.send_command(command_state.with_argument(["create", str(0), str(state_id)]))

    def update_parameter_state(self, state_id):
        # self.parameter.d["data_state"] = 20000
        self.configure_parameter(self.parameter)
        self.send_command(command_state.with_argument(["create", str(0), str(state_id)]))

    def install_actor_graph(self, actor_graph, host):
        print("install_actor_graph...")
        self.actor_graph = actor_graph
        # install the parameters into
        # self.configure_parameter(self.parameter)
        # initialize all the states
        for i in actor_graph.state_runtime_table.data:
            index = actor_graph.state_runtime_table.data.index(i)
            registration_id = i.state.registration_id
            self.send_command(command_state.with_argument(
                ["init", str(index), str(registration_id)]), host)

        # install action
        for i in actor_graph.action_runtime_table.data:
            action_index = actor_graph.action_runtime_table.data.index(i)
            if (i.action.action.name == "packet_in"):
                self.send_command(
                    command_config.with_argument(
                        ["rss_reta_config", str(i.starting_bucket), str(i.num_bucket), str(i.core_id),
                         str(action_index)]), host)

                next_action = i.next_action
                self.send_command(command_worker.with_argument(
                    ["first_action", str(i.core_id), str(next_action), str(i.starting_bucket), str(i.num_bucket)]),
                    host)

            elif (i.action.action.name == "packet_out"):
                # print(["create_packet_out", str(action_index), str(i.core_id)])
                # configure last action
                self.send_command(
                    command_action.with_argument(
                        ["create_packet_out", str(action_index), str(i.core_id), str(i.port_id)]), host)
            else:
                # print(i.action.action.registration_id,action_index,i.state_id, i.core_id)
                self.send_command(command_action.with_argument(
                    ["create", str(i.action.action.registration_id), str(action_index),
                     str(i.state_id), str(i.core_id)]), host)
                pass

        # install path
        for i in actor_graph.state_runtime_table.data:
            state_id = actor_graph.state_runtime_table.data.index(i)
            for j in i.path:
                if j != -1:
                    path_index = i.path.index(j)
                    path_id = j
                    # print(path_index,path_id,state_id)
                    self.send_command(
                        command_state.with_argument(["install_simple_path", str(state_id), str(j), str(path_index)]),
                        host)

    def action_migrate(self, action_id, core_id):
        self.send_command(command_action.with_argument(
            ["migrate", str(action_id), str(core_id)]))

    def worker_stop(self):
        self.send_command(command_worker.with_argument(
            ["stop"]
        ))


    def __del__(self):
        return

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

    @nflambda_send_command
    def port_init(self, num_queue) -> Command:
        red_print("port_init...")
        command = command_worker_fsm_amac.with_argument(
            ["port_init", str(num_queue)])
        return command

    @nflambda_send_command
    def install_amac_fsm(self, workfsm: WorkerFSM = None, parameters=None) -> Command:
        if workfsm is not None:
            red_print("install_amac_fsm...")
            command = command_worker_fsm_amac.with_argument(
                ["init", str(workfsm.id), dic_to_configuration_string(workfsm.configurations)])
            return command
        else:
            red_print("install_amac_fsm...")
            id = parameters["id"]
            configuration_string = dic_to_configuration_string(parameters["configurations"])
            command = command_worker_fsm_amac.with_argument(
                ["init", str(id), configuration_string])
            return command

    @nflambda_send_command
    def install_amac_fsm_actor_table(self, workfsm: WorkerFSM = None, parameters=None) -> Command:
        if workfsm is not None:
            red_print("install_amac_fsm_actor_table...")
            command = command_worker_fsm_amac.with_argument(
                ["worker_actor_table_init", str(workfsm.id), workfsm.actor_table.to_config()])
            return command
        else:
            red_print("install_amac_fsm_actor_table...")
            id = parameters["id"]
            configuration_string = dic_to_configuration_string(parameters["actor_table"])
            command = command_worker_fsm_amac.with_argument(
                ["worker_actor_table_init", str(id), configuration_string])
            return command

    @nflambda_send_command
    def install_amac_fsm_install_control_state(self, workfsm: WorkerFSM = None, parameters=None) -> Command:
        if workfsm is not None:
            red_print("install control state table onto the actor table...")
            configuration = ""
            for nf in workfsm.actor_table:
                nf_fsm = workfsm.actor_table.factory.nf_fsm_dic[nf]
                if nf_fsm.control_state == -1:
                    continue
                configuration += str(nf_fsm.state_id) + "$" + str(nf_fsm.control_state) + "$"
            configuration = configuration[:-1]
            command = command_worker_fsm_amac.with_argument(
                ["install_control_state_table", str(workfsm.id), configuration])
            return command
        else:
            red_print("install control state table onto the actor table...")
            id = parameters["id"]
            configuration_string = dic_to_configuration_string(parameters["state_id_to_control_state_id"])
            command = command_worker_fsm_amac.with_argument(
                ["install_control_state_table", str(id), configuration_string])
            return command

    @nflambda_send_commands
    def amac_fsm_control_states_init(self, workfsm: WorkerFSM = None, parameters=None) -> List[Command]:
        if workfsm is not None:
            red_print("amac_fsm_control_states_init...")
            # only init the top level fsm
            # print(workfsm.control_state_table)
            commands = []
            for control_state in workfsm.control_state_table:
                command = command_worker_fsm_amac.with_argument(
                    ["control_state_init", str(workfsm.id), str(control_state.get_name()),
                     str(workfsm.control_state_table.index(control_state)), control_state.to_config()])
                commands.append(command)
            return commands
        else:
            red_print("amac_fsm_control_states_init...")
            # only init the top level fsm
            # print(workfsm.control_state_table)
            commands = []
            id = parameters["id"]
            for nf_definition_name in parameters["control_state_table"]:
                parameter_list = parameters["control_state_table"][nf_definition_name]["parameters"]
                parameter_dict = {}
                for parameter in parameter_list:
                    parameter_dict[parameter.name] = parameters["control_state_table"][nf_definition_name][parameter.name]
                command = command_worker_fsm_amac.with_argument(
                    ["control_state_init", str(id), parameters["control_state_table"][nf_definition_name]["type"],
                     str(parameters["control_state_table"][nf_definition_name]["id"]),
                     dic_to_configuration_string(parameter_dict)])
                commands.append(command)
            return commands

    @nflambda_send_command
    def configure_control_state(self, workfsm: WorkerFSM, control_state_id):
        red_print("configure_control_state...")
        control_state = workfsm.control_state_table[control_state_id]
        control_state_name = control_state.get_name()
        command = command_worker_fsm_amac.with_argument(
            ["configure_control_state", str(workfsm.id), control_state_name, str(control_state_id),
             control_state.to_config()])
        return command

    @nflambda_send_commands
    def install_classifier(self, workfsm: WorkerFSM):
        red_print("install_classifier...")
        commands = []
        for i in workfsm.ancestor_actor_list:
            if i.type == NFType.MATCH:
                print(i)
                print(i.control_state)
                print(i.level)
                classifier_name = i.name.split("*")[0]
                classifier_level = str(i.level)
                control_state_id = str(i.control_state)
                command = command_worker_fsm_amac.with_argument(
                    ["worker_fsm_amac_classifier_init", str(workfsm.id), classifier_name, classifier_level,
                     control_state_id])
                commands.append(command)
        return commands

    @nflambda_send_command
    def install_nflow(self, worker_fsm: WorkerFSM):
        red_print("install_nflow...")
        command = command_worker_fsm_amac.with_argument(
            ["install_nflow", str(worker_fsm.id), str(worker_fsm.data_layout.get_entry_num()),
             worker_fsm.data_layout.to_config()])
        return command

    @nflambda_send_command
    def get_total_packet(self, worker_fsm: WorkerFSM):
        red_print("install_nflow...")
        command = command_worker_fsm_amac.with_argument(
            ["worker_fsm_amac_total_packet", str(worker_fsm.id)])
        return command

    @nflambda_send_command
    def run_amac_fsm(self, worker_fsm):
        red_print("run_amac_fsm...")
        command = command_worker_fsm_amac.with_argument(["run_amac_fsm", str(worker_fsm.id)])
        return command
