# runner is the highest level of controller of the nflambda runtime_agent
# it receives a configuration file about the dut and tg
# about a series of set up (parameters) for the workers
# it runs each set up one by one and collects the results
import argparse as argparse
import copy
import os
import sys
import time
import pandas as pd
from runtime_agent.exp_result.exp_result_manager import exp_saver

# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))

# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)

# adding the parent directory to
# the sys.path.
sys.path.append(parent)

from orchestration.resource_orchestration.resource_orchestration import get_exp_setup
from nflambda_platform import NFlambda
from utility.perf_parsing import perf_parser
from utility.perf_utility import run_perf_command_in_background

if __name__ == "__main__":
    '''
    :arg exp_name: the name of the experiment
    python3 runner.py traffic_generator_testing -d -o
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument("exp_name", type=str, nargs='?', default="cuckoo_hash_interleaved")  # the name of the experiment
    # examle command: python3 runner.py bess_nat -d -o
    parser.add_argument("-d", "--debug", action="store_true", default=False)
    parser.add_argument("-o", "--offline", action="store_true", default=False)
    parser.add_argument("-r", "--run", action="store_true", default=False)  # run the setting
    parser.add_argument("-s", "--stop", action="store_true", default=False)  # stop the setting
    parser.add_argument("-df", "--debug_first", action="store_true", default=False)  # stop the setting
    parser.add_argument("-ds", "--debug_second", action="store_true", default=False)  # stop the setting
    parser.add_argument("-dh", "--debug_hotspot", action="store_true", default=False)  # stop the setting


    args = parser.parse_args()
    exp_name = args.exp_name
    debug_mode = args.debug
    offline_mode = args.offline
    run_mode = args.run
    debug_first = args.debug_first
    debug_second = args.debug_second
    debug_hotspot = args.debug_hotspot

    if debug_first:  # only debug the first setup
        config_dic = get_exp_setup(exp_name)
        DistributedRuntimeSetting_list: dict = config_dic["DistributedRuntimeSetting"]
        distributed_runtime_setting = DistributedRuntimeSetting_list[0]
        RunTimeSetting_list: dict = distributed_runtime_setting["RuntimeSetting"]
        runtime_setting = RunTimeSetting_list[0]
        nflambda = NFlambda(offline_mode=offline_mode, debug_mode=debug_mode,
                            runtime_setting=runtime_setting)
        nflambda.configure()
        print(nflambda.get_total_packet())
        exit(0)

    if debug_second:  # only debug the second setup
        config_dic = get_exp_setup(exp_name)
        DistributedRuntimeSetting_list: dict = config_dic["DistributedRuntimeSetting"]
        distributed_runtime_setting = DistributedRuntimeSetting_list[0]
        RunTimeSetting_list: dict = distributed_runtime_setting["RuntimeSetting"]
        runtime_setting = RunTimeSetting_list[1]
        nflambda = NFlambda(offline_mode=offline_mode, debug_mode=debug_mode,
                            runtime_setting=runtime_setting)
        nflambda.configure()
        print(nflambda.get_total_packet())
        exit(0)

    if debug_mode or run_mode:
        config_dic = get_exp_setup(exp_name)
        DistributedRuntimeSetting_list: dict = config_dic["DistributedRuntimeSetting"]
        throughput_list = []
        distributed_runtime_setting = DistributedRuntimeSetting_list[0]
        RunTimeSetting_list: dict = distributed_runtime_setting["RuntimeSetting"]
        for _, runtime_setting in RunTimeSetting_list.items():
            nflambda = NFlambda(offline_mode=offline_mode, debug_mode=debug_mode,
                                runtime_setting=runtime_setting)
            nflambda.configure()
        exit(0)

    if args.stop:
        config_dic = get_exp_setup(exp_name)
        DistributedRuntimeSetting_list: dict = config_dic["DistributedRuntimeSetting"]
        throughput_list = []
        for _, distributed_runtime_setting in DistributedRuntimeSetting_list.items():
            RunTimeSetting_list: dict = distributed_runtime_setting["RuntimeSetting"]
            for _, runtime_setting in RunTimeSetting_list.items():
                nflambda = NFlambda(offline_mode=offline_mode, debug_mode=debug_mode,
                                    runtime_setting=runtime_setting)
                nflambda.stop_runtime()

        exit(0)

    else:
        config_dic = get_exp_setup(exp_name)
        DistributedRuntimeSetting_list: dict = config_dic["DistributedRuntimeSetting"]
        throughput_list = []
        df = pd.DataFrame()
        for key, _distributed_runtime_setting in DistributedRuntimeSetting_list.items():
            # add a row
            series = pd.Series()
            while True:
                done = False
                try:
                    for i in range(1):
                        temp_throughput_list = []
                        distributed_runtime_setting = copy.deepcopy(_distributed_runtime_setting)
                        RunTimeSetting_list: dict = distributed_runtime_setting["RuntimeSetting"]
                        for _, runtime_setting in RunTimeSetting_list.items():
                            nflambda = NFlambda(offline_mode=offline_mode, debug_mode=debug_mode,
                                                runtime_setting=runtime_setting)
                            nflambda.configure()

                        # check whether debug_hotspot is true
                        if debug_hotspot:
                            # run sudo perf record -C 2
                            current_time = (int)(time.time())
                            os.system("sudo perf record -C 2 -o data.out sleep 5".format(current_time))
                            # change the privilege of the file to all users
                            os.system("sudo chmod 777 data.out".format(current_time))
                            # output to current_time.txt
                            os.system("sudo perf report -i data.out > {}.txt".format(current_time))
                            # get the path of the current folder
                            current_path = os.path.dirname(os.path.realpath(__file__))
                            # move the file to exp_result folder
                            os.system("sudo mv {}.txt {}/exp_result/".format(current_time, current_path))
                            # add the timestamp to the series
                            series["hotspot"] = current_time

                        run_perf_command_in_background()
                        current_time = time.time()

                        for runtime_id, runtime_setting in RunTimeSetting_list.items():
                            nflambda = NFlambda(offline_mode=offline_mode, debug_mode=debug_mode,
                                                runtime_setting=runtime_setting)
                            throughput_vector = nflambda.get_total_packet()
                            if 0 in throughput_vector:
                                raise Exception("Throughput is 0")
                            if str(runtime_id)+"_throughput" not in series:
                                series[str(runtime_id) + "_throughput"] = []
                            series[str(runtime_id)+"_throughput"].append(throughput_vector)

                        elapsed_time = time.time() - current_time
                        for _, runtime_setting in RunTimeSetting_list.items():
                            nflambda = NFlambda(offline_mode=offline_mode, debug_mode=debug_mode,
                                                runtime_setting=runtime_setting)
                            nflambda.stop_runtime()

                        time.sleep(1)
                        filename = "test_output.txt"
                        events = perf_parser(filename, elapsed_time)
                        os.system("sudo rm " + filename)
                        for event_key in events.keys():
                            if event_key not in series:
                                series[event_key] = []
                            series[event_key].append(events[event_key])
                    done = True
                    time.sleep(1)
                    # print progress
                    # print in red, current key and total number of keys
                    print("\033[91m" + str(key) + "/" + str(len(DistributedRuntimeSetting_list)) + "\033[0m")
                except Exception as e:
                    # if the throughput contains 0, then we need to rerun the experiment
                    print(e)
                    print("key: ", key)
                    if "Throughput is 0" in str(e):
                        print("Throughput is 0, rerun the experiment")
                        distributed_runtime_setting = copy.deepcopy(_distributed_runtime_setting)
                        RunTimeSetting_list: dict = distributed_runtime_setting["RuntimeSetting"]
                        for _, runtime_setting in RunTimeSetting_list.items():
                            nflambda = NFlambda(offline_mode=offline_mode, debug_mode=debug_mode,
                                                runtime_setting=runtime_setting)
                            nflambda.stop_runtime()
                        continue
                    else:
                        distributed_runtime_setting = copy.deepcopy(_distributed_runtime_setting)
                        RunTimeSetting_list: dict = distributed_runtime_setting["RuntimeSetting"]
                        for _, runtime_setting in RunTimeSetting_list.items():
                            nflambda = NFlambda(offline_mode=offline_mode, debug_mode=debug_mode,
                                                runtime_setting=runtime_setting)
                            nflambda.stop_runtime()
                        raise e

                if done:
                    # add the row
                    df = df.append(series, ignore_index=True)
                    break

        exp_saver(exp_name, df)
