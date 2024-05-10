import os
from dataclasses import dataclass

import matplotlib
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter
from numpy import mean
import ast
import matplotlib.pyplot as plt

from orchestration.resource_orchestration.resource_orchestration import get_exp_setup

matplotlib.rcParams.update({'font.size': 25})
matplotlib.rcParams.update({'legend.fontsize': 18})
matplotlib.rcParams.update({'axes.labelsize': 25})
matplotlib.rcParams.update({'xtick.labelsize': 25})
matplotlib.rcParams.update({'ytick.labelsize': 25})


def dfs_search_key(dic, key):
    if key in dic:
        return dic[key]
    for k, v in dic.items():
        if isinstance(v, dict):
            item = dfs_search_key(v, key)
            if item is not None:
                return item


def get_mean_throughput(througput_list):
    return [mean(j) for j in througput_list]


def return_latex_power(x):
    return "$2^{" + str(x) + "}$"


def plot_throughput_and_state_size(exp_name):
    file_name = exp_name + ".json"
    # load as pandas dataframe
    df = pd.read_json(file_name)
    # plot the relationship between throughput and state size
    # get the configuration
    config_dic = get_exp_setup(exp_name)["DistributedRuntimeSetting"]
    # plot the relationship
    throughput_list = []
    state_size_list = [14, 15, 16, 17, 18, 19, 20]
    for i in state_size_list:
        index = state_size_list.index(i)
        # state_size_list.append(dfs_search_key(config_dic[i], "cuckoo_hash_entry_num"))
        # get the throughput
        temp_list = df["0_throughput"][index]
        temp_temp_list = get_mean_throughput(temp_list)
        throughput_list.append(temp_temp_list)

    boxprops = dict(linestyle='-', linewidth=1, color='k')
    # throughput_list is a list of list
    # each list is multiple samples of the same state size
    # plot as boxplot
    # get rid of the outliers

    plt.boxplot(throughput_list, showfliers=False, boxprops=boxprops)
    plt.xticks(np.arange(1, len(state_size_list) + 1), state_size_list)
    plt.xlabel("Number of Entries")
    plt.ylabel("Throughput (Mpps)")
    # y axs shown as integer
    plt.gca().yaxis.set_ticklabels([str(int(int(x) / 1000000)) for x in plt.gca().get_yticks().tolist()])
    plt.xticks(np.arange(1, len(state_size_list) + 1), state_size_list)
    # format as latex of power of 2
    # from 14 to 20
    plt.gca().xaxis.set_ticklabels([return_latex_power(x + 13) for x in plt.gca().get_xticks().tolist()])

    # figure size
    plt.gcf().set_size_inches(8, 6)
    # tight layout
    plt.tight_layout()
    name = exp_name + "_" + "throughput" + ".pdf"
    folder = "exp_plot/"
    if not os.path.exists(folder):
        os.makedirs(folder)
    plt.savefig(folder + name, bbox_inches='tight')
    plt.show()


def plot_throughput_and_metrics_per_packet(exp_name, x, metrics):
    if metrics == "l1_miss":
        metrics = "L1-dcache-load-misses"
        label = "L1 Misses per Packet"
    elif metrics == "l2_miss":
        metrics = "l2_rqsts.demand_data_rd_miss"
        label = "L2 Misses per Packet"
    elif metrics == "llc_miss":
        metrics = "LLC-load-misses"
        label = "LLC Misses per Packet"
    elif metrics == "cycles":
        metrics = "cycles"
        label = "cycles per packet"
    file_name =  exp_name + ".json"
    # load as pandas dataframe
    df = pd.read_json(file_name)
    # plot the relationship between throughput and state size
    # get the configuration
    config_dic = get_exp_setup(exp_name)["DistributedRuntimeSetting"]
    # plot the relationship between throughput and l1 miss per packet
    metric_per_packet_list_list = []
    state_size_list = [14, 15, 16, 17, 18, 19, 20]
    for i in state_size_list:
        index = state_size_list.index(i)
        # state_size_list.append(dfs_search_key(config_dic[i], x))
        # get the throughput
        temp_list = df["0_throughput"][index]
        temp_temp_list = get_mean_throughput(temp_list)
        metric_list = df[metrics][index]
        metric_per_packet_list = [x / y for x, y in zip(metric_list, temp_temp_list)]
        metric_per_packet_list_list.append(metric_per_packet_list)

    boxprops = dict(linestyle='-', linewidth=1, color='k')
    # throughput_list is a list of list
    # each list is multiple samples of the same state size
    # plot as boxplot
    # get rid of the outliers
    plt.boxplot(metric_per_packet_list_list, showfliers=False, boxprops=boxprops)
    plt.xticks(np.arange(1, len(state_size_list) + 1), state_size_list)
    # format as latex of power of 2
    # from 14 to 20
    plt.gca().xaxis.set_ticklabels([return_latex_power(x + 13) for x in plt.gca().get_xticks().tolist()])


    # the gap between the two x axis labels
    plt.gca().xaxis.set_tick_params(pad=10)
    plt.xlabel("Number of Entries")
    plt.ylabel(label)
    # tight layout
    # figure size
    plt.gcf().set_size_inches(8, 6)
    plt.tight_layout()

    name = exp_name + "_" + metrics + ".pdf"
    folder = "exp_plot/"
    if not os.path.exists(folder):
        os.makedirs(folder)

    plt.savefig(folder + name, bbox_inches='tight')

    plt.show()

def plot_throughput_and_metrics_per_packet_access_size(exp_name, x, metrics):
    if metrics == "l1_miss":
        metrics = "L1-dcache-load-misses"
        label = "L1 Misses per Packet"
    elif metrics == "l2_miss":
        metrics = "l2_rqsts.demand_data_rd_miss"
        label = "L2 Misses per Packet"
    elif metrics == "llc_miss":
        metrics = "LLC-load-misses"
        label = "LLC Misses per Packet"
    elif metrics == "cycles":
        metrics = "cycles"
        label = "cycles per packet"
    file_name = exp_name + ".json"
    # load as pandas dataframe
    df = pd.read_json(file_name)
    # plot the relationship between throughput and state size
    # get the configuration
    config_dic = get_exp_setup(exp_name)["DistributedRuntimeSetting"]
    # plot the relationship between throughput and l1 miss per packet
    metric_per_packet_list_list = []
    state_size_list = [1,2,3,4,5,6,7,8]
    for i in state_size_list:
        index = state_size_list.index(i)
        # state_size_list.append(dfs_search_key(config_dic[i], x))
        # get the throughput
        temp_list = df["0_throughput"][index]
        temp_temp_list = get_mean_throughput(temp_list)
        metric_list = df[metrics][index]
        metric_per_packet_list = [x / y for x, y in zip(metric_list, temp_temp_list)]
        metric_per_packet_list_list.append(metric_per_packet_list)

    boxprops = dict(linestyle='-', linewidth=1, color='k')
    # throughput_list is a list of list
    # each list is multiple samples of the same state size
    # plot as boxplot
    # get rid of the outliers
    plt.boxplot(metric_per_packet_list_list, showfliers=False, boxprops=boxprops)
    plt.xticks(np.arange(1, len(state_size_list) + 1), state_size_list)
    # format as latex of power of 2
    # from 14 to 20
    # plt.gca().xaxis.set_ticklabels([return_latex_power(x + 13) for x in plt.gca().get_xticks().tolist()])

    # the gap between the two x axis labels
    plt.gca().xaxis.set_tick_params(pad=10)
    plt.xlabel("State Size (# of Cache Lines)")
    plt.ylabel(label)
    # tight layout
    plt.tight_layout()
    # figure size
    plt.gcf().set_size_inches(8, 6)

    name = exp_name + "_" + metrics + ".pdf"
    folder = "exp_plot/"
    if not os.path.exists(folder):
        os.makedirs(folder)

    plt.savefig(folder + name, bbox_inches='tight')

    plt.show()


def plot_x_y(exp_name, x, y):
    if y == "throughput":
        y = "0_throughput"
        label = "Throughput (Mpps)"
    # get exp setup
    config_dic = get_exp_setup(exp_name)["DistributedRuntimeSetting"]
    # get exp_result
    file_name = exp_name + ".json"
    # load as pandas dataframe
    df = pd.read_json(file_name)
    # print(config_dic)
    x_list = []
    y_list_list = []
    for i in config_dic:
        index = i
        # get the throughput
        temp_list = df["0_throughput"][index]
        temp_temp_list = get_mean_throughput(temp_list)
        # get the x
        x_list.append(dfs_search_key(config_dic[i], x))
        # get the y
        y_list_list.append(temp_temp_list)

    boxprops = dict(linestyle='-', linewidth=1, color='k')
    # throughput_list is a list of list
    # each list is multiple samples of the same state size
    # plot as boxplot
    # get rid of the outliers
    plt.boxplot(y_list_list, showfliers=False, boxprops=boxprops)
    plt.xticks(np.arange(1, len(x_list) + 1), x_list)
    plt.xlabel("State Size (# of Cache Lines)")
    plt.ylabel(label)
    # y axs shown as integer
    plt.gca().yaxis.set_ticklabels([str((int(x) / 1000000)) for x in plt.gca().get_yticks().tolist()])
    # latex 2^x

    plt.gca().xaxis.set_ticklabels([x for x in x_list])

    # the gap between the two x axis labels
    plt.gca().xaxis.set_tick_params(pad=10)

    # figure size
    plt.gcf().set_size_inches(6, 4)
    # tight layout
    plt.tight_layout()
    name = exp_name + "_" + x + "_" + y + ".pdf"
    folder = "exp_plot/"
    if not os.path.exists(folder):
        os.makedirs(folder)

    plt.savefig(folder + name, bbox_inches='tight')

    plt.show()


if __name__ == "__main__":
    exp_name = "cuckoo_hash_rtc_state_size"
    if exp_name == "cuckoo_hash_rtc":
        plot_throughput_and_state_size(exp_name)
        plot_throughput_and_metrics_per_packet(exp_name, "cuckoo_hash_entry_size", "l1_miss")
        plot_throughput_and_metrics_per_packet(exp_name, "cuckoo_hash_entry_size", "l2_miss")
        plot_throughput_and_metrics_per_packet(exp_name, "cuckoo_hash_entry_size", "llc_miss")
        plot_throughput_and_metrics_per_packet(exp_name, "cuckoo_hash_entry_size", "cycles")
    if exp_name == "cuckoo_hash_rtc_state_size":
        plot_x_y(exp_name, "generic_access_size", "throughput")
        plot_throughput_and_metrics_per_packet_access_size(exp_name, "generic_access_size", "l1_miss")
        plot_throughput_and_metrics_per_packet_access_size(exp_name, "generic_access_size", "l2_miss")
        plot_throughput_and_metrics_per_packet_access_size(exp_name, "generic_access_size", "llc_miss")
        plot_throughput_and_metrics_per_packet_access_size(exp_name, "generic_access_size", "cycles")
