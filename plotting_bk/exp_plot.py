import sys

import matplotlib
import numpy as np
from numpy import mean

from data_extraction import *
import matplotlib.pyplot as plt

matplotlib.rcParams.update({'font.size': 22})
matplotlib.rcParams.update({'legend.fontsize': 18})
matplotlib.rcParams.update({'axes.labelsize': 20})
matplotlib.rcParams.update({'xtick.labelsize': 20})
matplotlib.rcParams.update({'ytick.labelsize': 20})


# chech whether exp_name.csv exists in data folder
import os



import pandas as pd

def load_df(exp_name):
    if not os.path.exists("data/" + exp_name + ".csv"):
        print("data/" + exp_name + ".csv does not exist")
        print("call load_exp_result.py to load the data")
        # call load_exp_result.py exp_name to load the data
        os.system("python3 load_exp_result.py " + exp_name)
        print("data/" + exp_name + ".csv is loaded")
    file_name = "data/" + exp_name + ".csv"
    df = pd.read_csv(file_name)
    return df

def save_file(plt, file_name):
    # create folder if not exist
    if not os.path.exists("plots"):
        os.mkdir("plots")
    plt.savefig(file_name)


def plot_relationship(df, variable_1, variable_2):
    x = []
    y = []
    x_extractor = key_to_extractor[variable_1]
    y_extractor = key_to_extractor[variable_2]
    # reinitialize plt
    plt.clf()
    for i in range(len(df)):
        row = df.iloc[i]
        x.append(x_extractor(row))
        y.append(y_extractor(row))
    plt.bar(x, y)
    xlabel = variable_1.replace("_", " ")
    ylabel = variable_2.replace("_", " ")
    variation = 0.1
    ylimit = (min(y) - variation * (max(y) - min(y)), max(y) + variation * (max(y) - min(y)))
    plt.ylim(ylimit)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt_file_name = "plots/" + exp_name + "_" + variable_1 + "_" + variable_2 + ".pdf"
    save_file(plt, plt_file_name)


def plot_relationship(df, plot_config: PlotConfiguration):
    x_axis_variable = plot_config.x_axis
    y_axis_variable_list = plot_config.y_axis_list
    x_label = key_to_label[x_axis_variable]
    y_label = key_to_label[y_axis_variable_list[0]]
    y_len = len(y_axis_variable_list)
    x_extractor = key_to_extractor[x_axis_variable]
    x = []
    y = []
    for i in range(len(df)):
        row = df.iloc[i]
        x.append(x_extractor(row))
    for i in range(y_len):
        y.append([])
        y_extractor = key_to_extractor[y_axis_variable_list[i]]
        for j in range(len(df)):
            row = df.iloc[j]
            y[i].append(y_extractor(row))

    # calculate the bar width
    bar_width = 0.8 / y_len
    # reinitialize plt
    plt.clf()
    #
    # for i in range(y_len):
    #     plt.bar([x[j] + i * bar_width for j in range(len(x))], y[i], width=bar_width)
    # xticks
    xticks = [i for i in range(len(x))]
    # use lambda function from key_to_x_tick
    xticks_label = [key_to_x_tick[x_axis_variable](x[i]) for i in range(len(x))]
    plt.xticks(xticks, xticks_label)
    # plot
    for i in range(y_len):
        plt.bar(np.array(xticks) + i * bar_width, y[i], width=bar_width, label=y_axis_variable_list[i])

    # move xticks to the center of the bar
    plt.xticks([i + bar_width * (y_len - 1) / 2 for i in xticks], xticks_label)

    variation = 0.1
    ylimit = (min([min(y[i]) for i in range(y_len)]) - variation * (
            max([max(y[i]) for i in range(y_len)]) - min([min(y[i]) for i in range(y_len)])),
              max([max(y[i]) for i in range(y_len)]) + variation * (
                      max([max(y[i]) for i in range(y_len)]) - min([min(y[i]) for i in range(y_len)])))
    plt.ylim(ylimit)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    # legend
    # only show if there are more than one y_axis_variable
    if len(y_axis_variable_list) > 1:
        plt.legend(y_axis_variable_list)
    plt_file_name = "plots/" + exp_name + "_" + x_axis_variable + "_" + "_".join(y_axis_variable_list) + ".pdf"
    # replace space with underscore
    plt_file_name = plt_file_name.replace(" ", "_")
    # tighten the layout
    plt.tight_layout()
    save_file(plt, plt_file_name)
    # plt.show()


for exp_name in exp_name_to_list_of_plot_configuration:
    exp = exp_name_to_list_of_plot_configuration[exp_name]
    df = load_df(exp_name)
    for plot_config in exp:
        plot_relationship(df, plot_config)
