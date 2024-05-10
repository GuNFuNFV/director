from typing import List

from utility import red_print


class Command:
    def __init__(self, command_str, argument_list=[]):
        self.space = " "
        self.enter = "\n"
        self.command = command_str
        self.argument_list = argument_list

    def with_argument(self, argument_list: List[str]) -> "Command":
        return Command(self.command, argument_list)

    def apply(self):
        result = self.command
        for arg in self.argument_list:
            result = result + self.space + arg
        # print(result)
        return (result + self.enter).encode()

    def __str__(self):
        return self.apply().decode()


def print_command_simulation(command):
    red_print("command:", end="")
    temp = str(command).split(" ")
    configuration_string = ""
    for i in temp:
        if "$" in i:
            configuration_string = i
        else:
            print(i, end=" ")
    if configuration_string == "":
        print()
        return
    print()
    key_value_pairs = configuration_string.split("$")
    state = "key"
    for i in key_value_pairs:
        if state == "key":
            print("\t", i, end=":")
            state = "value"
        else:
            print(i)
            state = "key"

command_config = Command("config")
command_mempool = Command("mempool")
command_em = Command("nf_model")
command_nf = Command("nf")
command_worker = Command("worker")
command_worker_fsm_amac = Command("worker_fsm_amac")
command_exit = Command("exit")
command_worker_fsm = Command("worker_fsm")
command_port = Command("port")
command_dump = Command("dump")
command_coordinator = Command("coordinator")
command_core = Command("core")
command_action = Command("action")
command_state = Command("state")
command_log = Command("log")
command_query = Command("query")
command_send = Command("send")
command_sendnat = Command("send_nat")
command_message = Command("message")

