import math
from pprint import pprint

import matplotlib
import numpy as np
from matplotlib import pyplot as plt

from runtime_agent import exp_loader
from runtime_agent.exp_result.exp_result_manager import read_file

matplotlib.rcParams.update({'font.size': 16})
matplotlib.rcParams.update({'legend.fontsize': 18})
matplotlib.rcParams.update({'axes.labelsize': 25})
matplotlib.rcParams.update({'xtick.labelsize': 20})
matplotlib.rcParams.update({'ytick.labelsize': 12})

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


if __name__ == "__main__":
    df = exp_loader("amf_free5gc", timestamp=1694846573)
    print(get_access_time(df))
    # calculate_state_access_time(result)
    print(get_throughput(df))
    print(df.columns)
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

    # List to store all the data arrays
    data_lists = [
        [i / 1000 for i in throughput_list],
        [i for i in state_acess_time_per_packet],
        [i for i in l1_miss_per_packet_list],
        [i for i in l2_miss_per_packet_list],
        [i for i in l3_miss_per_packet_list]
    ]

    # Number of bars per group
    bars_per_group = 4

    # Bar width
    bar_width = 2.5
    subplot_labels = ['Throughput', 'State Access Time', 'L1 Miss', 'L2 Miss', 'L3 Miss']
    hatch_list = ['/', 'x', '\\', 'o', '.']
    color_list = ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F', '#EDC948', '#B07AA1', '#FF9DA7', '#9C755F',
                  '#BAB0AC']
    # to 2^14, 2^15, 2^16, 2^17 in latex
    subgroups = ["$2^{14}$", "$2^{15}$", "$2^{16}$", "$2^{17}$"]

    # Calculate number of big groups
    num_big_groups = len(data_lists[0]) // bars_per_group

    # adjust the figure size
    plt.figure(figsize=(9, 10))

    # Create a subplot for each data array
    for idx, (data, label) in enumerate(zip(data_lists, subplot_labels)):
        ax = plt.subplot(len(data_lists), 1, idx + 1)

        # Create an index for each tick position
        index = np.arange(0, len(data), bars_per_group)

        for i in range(bars_per_group):
            bar_positions = index + i * bar_width / bars_per_group
            bar_values = data[i * len(index):(i + 1) * len(index)]
            bars = plt.bar(bar_positions,
                           bar_values,
                           bar_width / bars_per_group, hatch=hatch_list[i], color=color_list[i], label=subgroups[i], alpha=0.99)

        # remove xticks
        plt.xticks([])

        # add legend in the first subplot at the top in one row
        if idx == 0:
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.60), ncol=bars_per_group, fontsize=14,
                       title="Number of UEs", title_fontsize=14)

        # add grid
        plt.grid(axis='y', linestyle='--', linewidth=0.5)

        if idx == 0:
            ylabel_text = 'Throughput (kpps)'
        elif idx == 1:
            ylabel_text = 'State Access Time (ns)'
        elif idx == 2:
            ylabel_text = 'L1C Misses/Packet'
        elif idx == 3:
            ylabel_text = 'L2C Misses/Packet'
        elif idx == 4:
            ylabel_text = 'L3C Misses/Packet'

        ax.set_ylabel(ylabel_text, fontsize=11)
        ax.yaxis.set_label_coords(-0.065, 0.5)  # Adjust coordinates as needed

    # add xticks for the last subplot
    # two rows of xticks
    # first row is for each bar
    # second row is for each group
    # first row = ["2^4", "2^5", "2^6", "2^7"] for each group in latex
    # second row = ["2^15", "2^16", "2^17", "2^18"] in latex
    xticks = []
    for i in range(num_big_groups):
        xticks.append(f'$2^{{{i + 14}}}$')
    x_values = np.array(["Initial UE", "Authentication Response", "Security Mode Complete", "Registration Complete",
                         "Transport 5GSM"])  # Corresponding x-axis values
    plt.xticks(index + bar_width / 2, x_values, fontsize=12, rotation=10)
    # plt.xlabel('Number of Flows', fontsize=15)

    # Adjust layout to prevent clipping
    plt.tight_layout()
    # plt.show()
    plt.savefig("amf_per_packet_calculation.pdf", bbox_inches='tight')

    actual_state_accessed = np.array(
        [math.ceil(1467 / 64), math.ceil(470 / 64), math.ceil(729 / 64), math.ceil(267 / 64), math.ceil(225 / 64)])
    cache_line_list = np.array([23, 18, 18, 13, 11])
    optimized_cache_line_list = [20, 7, 11, 6, 6]
    plt.xticks(index + bar_width / 2, x_values, fontsize=12, rotation=10)
    x_values = np.array(["Initial UE", "Authentication Response", "Security Mode Complete", "Registration Complete","Transport 5GSM"])  # Corresponding x-axis values

    # create a bar chart with 5 groups, each of which containing 3 bars
    subgroup = ["actual accessed", "free5gc", "optimized"]
    bar_width = 0.2
    bar_positions = np.arange(len(x_values))
    bar_positions_1 = bar_positions - bar_width
    bar_positions_2 = bar_positions
    bar_positions_3 = bar_positions + bar_width
    plt.figure(figsize=(9, 4))
    plt.bar(bar_positions_1, cache_line_list, width=bar_width, label='Touched Cache Lines',
            hatch=hatch_list[0], alpha=0.99, color = color_list[1])
    plt.bar(bar_positions_2, actual_state_accessed, width=bar_width,label='Actual State Accessed',
            hatch=hatch_list[1], alpha=0.99, color = color_list[0])
    plt.bar(bar_positions_3, optimized_cache_line_list, width=bar_width, label='Optimized Cache Lines',
            hatch=hatch_list[2], alpha=0.99, color = color_list[2])
    plt.xticks(bar_positions, x_values, fontsize=12, rotation=10)
    plt.legend(loc='upper right')
    plt.ylabel('Cache Lines Number', fontsize=15)
    plt.tight_layout()
    plt.savefig("data_packing.pdf", bbox_inches='tight')
    plt.show()
    temp = {2: [0, 1, 2, 3, 4, 5, 6], 5: [0, 1, 6, 3, 7, 2], 6: [0, 1, 6, 3, 7, 2], 3: [0, 1, 2, 6, 7, 8, 9, 10, 3, 5, 11], 1: [14, 15, 16, 0, 1, 2, 3, 17, 18, 5, 19, 24, 25, 26, 27, 28, 4, 6, 29, 8]}
    for i in temp:
        print(i, len(temp[i]))