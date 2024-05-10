import math
from pprint import pprint

import matplotlib
import numpy as np
from matplotlib import pyplot as plt

from runtime_agent import exp_loader
from runtime_agent.exp_result.exp_result_manager import read_file

matplotlib.rcParams.update({'font.size': 25})
matplotlib.rcParams.update({'legend.fontsize': 18})
matplotlib.rcParams.update({'axes.labelsize': 25})
matplotlib.rcParams.update({'xtick.labelsize': 20})
matplotlib.rcParams.update({'ytick.labelsize': 18})



# Index(['Unnamed: 0', 'hotspot', '0_throughput', '1_throughput',
#        'LLC-load-misses', 'LLC-loads', 'l2_rqsts.demand_data_rd_miss',
#        'l2_rqsts.all_demand_data_rd', 'L1-dcache-load-misses',
#        'L1-dcache-loads', 'instructions', 'cycles', 'l1d.replacement',
#        'llc_miss_rate', 'l1_miss_rate', 'l2_miss_rate', 'ipc'],
#       dtype='object')

result = {
    1: {
        "num_datablock": 23
    },

    2: {
        "num_datablock": 18
    },

    3: {
        "num_datablock": 18
    },
    5: {
        "num_datablock": 13

    },
    6: {
        "num_datablock": 11
    }
}


def calculate_state_access_time(result):
    for item in result:
        state_access_total_time = result[item]["state_access_time"]
        pps = result[item]["pps"]
        state_access_per_packet = state_access_total_time / pps / 60 * 1000000
        print("state_access_per_packet", state_access_per_packet)


def get_throughput(df):
    throughput = df["0_throughput"]
    result = []
    for item in throughput:
        evaled = eval(item)[0][0]
        result.append(evaled)
    return result


def get_l1_miss(df):
    data = df["l1d.replacement"]
    result = []
    for item in data:
        result.append(eval(item)[0])
    return result


def get_l2_miss(df):
    # data = df["l2_rqsts.all_demand_miss"]
    data = df["MEM_LOAD_RETIRED.L2_MISS"]
    result = []
    for item in data:
        result.append(eval(item)[0])
    return result


def get_l3_miss(df):
    data = df["LLC-load-misses"]
    result = []
    for item in data:
        result.append(eval(item)[0])

    data_2 = df["LLC-store-misses"]
    for item in range(len(data_2)):
        result[item] += eval(data_2[item])[0]
    return result


def get_access_time(df):
    data = df["hotspot"]
    result = []
    for i in data:
        filename = str((int(i)))
        lines = read_file(filename)
        temp_result = 0
        for line in lines:
            if "write_variable" in line:
                # print(line.split("%")[0])
                temp_result += float(line.split("%")[0])
            if "read_variable" in line:
                # print(line.split("%")[0])
                temp_result += float(line.split("%")[0])
        result.append(temp_result)
    return result

#{2: [0, 1, 2, 3, 4, 5, 6], 5: [0, 1, 6, 3, 7, 2], 6: [0, 1, 6, 3, 7, 2], 3: [0, 1, 2, 6, 7, 8, 9, 10, 3, 5, 11], 1: [14, 15, 16, 0, 1, 2, 3, 17, 18, 5, 19, 24, 25, 26, 27, 28, 4, 6, 29, 8]}
    # actual_state_accessed = np.array([math.ceil(1467 / 64), math.ceil(470 / 64), math.ceil(729 / 64), math.ceil(267 / 64), math.ceil(225 / 64)])
if __name__ == "__main__":
    #df = exp_loader("amf_free5gc", timestamp=1694283577)
    #df = exp_loader("amf_free5gc", timestamp=1695223348)
    df = exp_loader("amf_free5gc")

    # df = exp_loader("amf_free5gc")
    print(get_access_time(df))
    # calculate_state_access_time(result)
    print(get_throughput(df))
    print(get_l1_miss(df))
    print(get_l2_miss(df))
    print(get_l3_miss(df))
    state_access_time = get_access_time(df)
    throughput_list = get_throughput(df)
    per_packet_processing_time = [1 / throughput_list[i] for i in range(len(throughput_list))]
    state_acess_time_per_packet = [state_access_time[i] * per_packet_processing_time[i] / 100 * 1000000000 for i in
                                   range(len(state_access_time))]

    l1_miss_list = get_l1_miss(df)
    l1_miss_per_packet_list = [l1_miss_list[i] / throughput_list[i] for i in range(len(l1_miss_list))]
    l2_miss_list = get_l2_miss(df)
    l2_miss_per_packet_list = [l2_miss_list[i] / throughput_list[i] for i in range(len(l2_miss_list))]
    l3_miss_list = get_l3_miss(df)
    l3_miss_per_packet_list = [l3_miss_list[i] / throughput_list[i] for i in range(len(l3_miss_list))]

    index = 0
    state_access_time_list = []
    cache_lines_list = []
    for item in result:
        if result[item]["num_datablock"] == 0:
            continue
        print(
            "item {}, n_blocks {}, pps {}, l1_miss_per_packet {}, l2_miss_per_packet {}, l3_miss_per_packet {}, state_access_per_packet {}".format(
                item,
                result[item]["num_datablock"],
                throughput_list[index],
                l1_miss_per_packet_list[index],
                l2_miss_per_packet_list[index],
                l3_miss_per_packet_list[index],
                state_acess_time_per_packet[index]

            ))
        state_access_time_list.append(state_acess_time_per_packet[index])
        cache_lines_list.append(result[item]["num_datablock"])
        index += 1

    # Create some sample data
    time_ns = np.array(state_access_time_list)  # Time in nanoseconds
    cache_lines = np.array(cache_lines_list)  # Number of cache lines
    actual_state_accessed = np.array([1467, 470, 729, 267, 225])

    x_values = np.array(["Initial UE", "Authentication Response", "Security Mode Complete", "Registration Complete",
                         "Transport 5GSM"])  # Corresponding x-axis values

    # Create a figure and a set of subplots (axes)
    fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(nrows=5, ncols=1, figsize=(14, 16), sharex=True)

    # Common settings
    width = 0.2
    x_indices = np.arange(len(x_values))
    bar_width = width + width / 2
    # First subplot for time_ns
    ax1.set_ylabel('Time (ns)', size=20)
    ax1.bar(x_indices + width, time_ns, width=bar_width, color='tab:blue', label='State Access Time', hatch='//')
    ax1.tick_params(axis='y')
    ax1.legend(loc='upper left', bbox_to_anchor=(0.65, 1.0), ncol=1, fancybox=True, shadow=True)
    # plot pps

    # the second y axis is pps
    # set the second y axis
    # ax1_2 = ax1.twinx()
    # ax1_2.set_ylabel('Throughput (pps)', size=20)
    # ax1_2.plot(x_indices + width, throughput_list, color='tab:orange', label='Throughput (pps)', marker='o')
    #
    # ax1_2.tick_params(axis='y')
    # ax1_2.set_ylim([0, 1000000])

    # Second subplot for cache_lines
    ax2.set_ylabel('Size in Cache Lines', size=20)
    ax2.bar(x_indices + width - bar_width/4, cache_lines, width=bar_width / 2, color='tab:green', label='Touched Cache Lines',
            hatch='//', alpha = 0.99)

    # plot llc miss per packet
    # ax2.plot(x_indices + width - bar_width/4, l3_miss_per_packet_list, color='tab:orange', label='LLC Miss Per Packet', marker='o')
    # the second y axis is llc miss per packet
    # set the second y axis
    # ax2_2 = ax2.twinx()
    # ax2_2.set_ylabel('LLC Miss Per Packet', size=20)
    # ax2_2.tick_params(axis='y')
    # ax2_2.set_ylim([5, 25])

    actual_state_accessed = np.array([math.ceil(1467 / 64), math.ceil(470 / 64), math.ceil(729 / 64), math.ceil(267 / 64), math.ceil(225 / 64)])

    ax2.bar(x_indices + width + bar_width/4, actual_state_accessed, width=bar_width / 2, color='tab:red', label='Actual State Accessed', hatch='\\', alpha = 0.99)

    legend = ax2.legend(loc='upper left', bbox_to_anchor=(0.65, 1.0), ncol=1, fancybox=True, shadow=True)

    ax3.set_ylabel('L1C Misses/Packet', size=20)
    ax3.bar(x_indices + width, l1_miss_per_packet_list, width=bar_width, color='tab:blue', label='L1 Miss Per Packet', hatch='//', alpha = 0.99)
    ax4.set_ylabel('L2C Misses/Packet', size=20)
    ax4.bar(x_indices + width, l2_miss_per_packet_list, width=bar_width, color='tab:blue', label='L2 Miss Per Packet', hatch='//', alpha = 0.99)
    ax5.set_ylabel('LLC Misses/Packet', size=20)
    ax5.bar(x_indices + width, l3_miss_per_packet_list, width=bar_width, color='tab:blue', label='LLC Miss Per Packet', hatch='//', alpha = 0.99)
    ax5.set_xticks(x_indices + width)
    ax5.set_xticklabels(x_values, rotation=10)
    ax5.set_xlabel('AMF Message Type')
    plt.tight_layout()
    # plt.savefig("amf_per_packet_calculation.pdf")
    plt.show()



