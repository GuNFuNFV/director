from pprint import pprint

import matplotlib
import numpy as np
from matplotlib import pyplot as plt
from numpy import average

from runtime_agent import exp_loader
import pandas as pd

pd.set_option('display.max_columns', None)  # or a large integer like 1000

matplotlib.rcParams.update({'font.size': 25})
matplotlib.rcParams.update({'legend.fontsize': 18})
matplotlib.rcParams.update({'axes.labelsize': 25})
matplotlib.rcParams.update({'xtick.labelsize': 25})
matplotlib.rcParams.update({'ytick.labelsize': 25})


def return_latex_power(x):
    return "$2^{" + str(x) + "}$"


def load_result(latest=0):
    bess_result = exp_loader("bess_nat", latest=latest)
    # for all the setups, calculate l1-dcache-load-misses per packet, l2_rqsts.demand_data_rd_miss per packet, LLC-load-misses per packet, cycles per packet
    # rename as l1 miss per packet, l2 miss per packet, llc miss per packet, cycles per packet
    packet_size_list = [64, 128, 256, 512, 1024]
    l1_miss_per_packet = [[] for i in range(len(packet_size_list))]
    l2_miss_per_packet = [[] for i in range(len(packet_size_list))]
    llc_miss_per_packet = [[] for i in range(len(packet_size_list))]
    cycles_per_packet = [[] for i in range(len(packet_size_list))]
    throughput_list = [[] for i in range(len(packet_size_list))]
    for i in range(len(bess_result)):
        packet_size_index = i % len(packet_size_list)
        num_packets = bess_result.iloc[i]["0_throughput"]
        l1_miss = bess_result.iloc[i]["L1-dcache-load-misses"]
        l2_miss = bess_result.iloc[i]["l2_rqsts.demand_data_rd_miss"]
        llc_miss = bess_result.iloc[i]["LLC-load-misses"]
        cycles = bess_result.iloc[i]["cycles"]
        num_packets_value = eval(num_packets)[0][0]
        l1_miss_value = eval(l1_miss)[0]
        l2_miss_value = eval(l2_miss)[0]
        llc_miss_value = eval(llc_miss)[0]
        cycles_value = eval(cycles)[0]
        l1_miss_per_packet[packet_size_index].append(l1_miss_value / num_packets_value)
        l2_miss_per_packet[packet_size_index].append(l2_miss_value / num_packets_value)
        llc_miss_per_packet[packet_size_index].append(llc_miss_value / num_packets_value)
        cycles_per_packet[packet_size_index].append(cycles_value / num_packets_value)
        throughput_list[packet_size_index].append(num_packets_value / 1000000)  # convert to mpps

    return l1_miss_per_packet, l2_miss_per_packet, llc_miss_per_packet, cycles_per_packet, throughput_list


def recursive_fill(shape, indices, matrix_list, new_matrix):
    dim = len(shape)

    if dim == 1:
        for i in range(shape[0]):
            new_indices = indices + (i,)
            new_matrix[new_indices] = [matrix[new_indices] for matrix in matrix_list]
    else:
        for i in range(shape[0]):
            new_indices = indices + (i,)
            recursive_fill(shape[1:], new_indices, matrix_list, new_matrix)


def combine_matrices(matrix_list):
    # for each element in the list, convert it to a numpy array if it is not
    for i in range(len(matrix_list)):
        if not isinstance(matrix_list[i], np.ndarray):
            matrix_list[i] = np.array(matrix_list[i])
    if not matrix_list:
        return None

    # Get the shape of the first matrix in the list
    shape = matrix_list[0].shape

    # Initialize a new matrix with the same shape but with object type to store lists
    new_matrix = np.empty(shape, dtype=object)

    # Fill the new matrix
    recursive_fill(shape, tuple(), matrix_list, new_matrix)

    # convert to list
    return new_matrix.tolist()


def load_zipped_result():
    l1_miss_per_packet_list = []
    l2_miss_per_packet_list = []
    llc_miss_per_packet_list = []
    cycles_per_packet_list = []
    throughput_list = []
    for i in range(0, 20):
        l1_miss_per_packet, l2_miss_per_packet, llc_miss_per_packet, cycles_per_packet, througput = load_result(
            latest=i)
        l1_miss_per_packet_list.append(l1_miss_per_packet)
        l2_miss_per_packet_list.append(l2_miss_per_packet)
        llc_miss_per_packet_list.append(llc_miss_per_packet)
        cycles_per_packet_list.append(cycles_per_packet)
        throughput_list.append(througput)

    return combine_matrices(l1_miss_per_packet_list), combine_matrices(l2_miss_per_packet_list), combine_matrices(
        llc_miss_per_packet_list), combine_matrices(cycles_per_packet_list), combine_matrices(throughput_list)


def plot_exp_setup(exp_setup):
    y_label = exp_setup["y_label"]
    value  = exp_setup["value"]
    x_axis = [i for i in range(14, 21)]
    # first plot throughput
    packet_size_list = [64, 128, 256, 512, 1024]
    label_list = ["64B", "128B", "256B", "512B", "1024B"]

    fig, ax = plt.subplots(figsize=(8, 6))
    # set x axis to be power of 2 using latex
    ax.set_xticks(x_axis)
    ax.set_xticklabels([return_latex_power(i) for i in x_axis])
    for i in range(len(packet_size_list)):
        # bp = plt.boxplot(value[i], positions=x_axis, patch_artist=True, showfliers=False, boxprops=dict(linewidth=1.5, facecolor='white'),
        #                  whiskerprops=dict(linewidth=1.5), capprops=dict(linewidth=1.5),
        #                  medianprops=dict(linewidth=1.5))
        # remove outliers
        medium_value = [average(value[i][j]) for j in range(len(value[0]))]
        # plot the medium value
        ax.plot(x_axis, medium_value, label=label_list[i], marker='o')
    ax.set_xlabel("Number of Flows")
    ax.set_ylabel(y_label)
    plt.legend()
    plt.tight_layout()
    # plt.show()
    file_name = "nat_" + y_label.replace(" ", "_") + "_motivation.pdf"
    plt.savefig(file_name)

if __name__ == "__main__":

    l1_miss_per_packet, l2_miss_per_packet, llc_miss_per_packet, cycles_per_packet, throughput = load_zipped_result()

    exp_setup_list = {
        "throughput": {
            "y_label": "Throughput (Mpps)",
            "value": throughput
        },
        "l1_miss_per_packet": {
            "y_label": "L1 Miss per Packet",
            "value": l1_miss_per_packet
        },
        "l2_miss_per_packet": {
            "y_label": "L2 Miss per Packet",
            "value": l2_miss_per_packet
        },
        "llc_miss_per_packet": {
            "y_label": "LLC Miss per Packet",
            "value": llc_miss_per_packet
        },
        "cycles_per_packet": {
            "y_label": "Cycles per Packet",
            "value": cycles_per_packet
        },
    }
    for exp_setup in exp_setup_list:
        plot_exp_setup(exp_setup_list[exp_setup])

