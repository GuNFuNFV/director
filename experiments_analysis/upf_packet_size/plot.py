if __name__ == "__main__":

    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np
    import matplotlib

    matplotlib.rcParams.update({'font.size': 22})
    matplotlib.rcParams.update({'legend.fontsize': 18})
    matplotlib.rcParams.update({'axes.labelsize': 20})
    matplotlib.rcParams.update({'xtick.labelsize': 18})
    matplotlib.rcParams.update({'ytick.labelsize': 18})

    df = pd.read_csv("upf_monolithic.csv")
    df2 = pd.read_csv("upf_interleaved.csv")

    packet_size_list = [64, 128, 256, 512, 1024, 1280, 1518]
    tree_depth_list = [4,5,6,7]

    throughput_list_list = []
    for i in range(len(tree_depth_list)):
        throughput_list = []
        for j in range(len(packet_size_list)):
            row_index = i * len(packet_size_list) + j
            # get the throughput of row of index row_index
            throughput = df2.values[row_index][2]
            throughput = eval(throughput)[0][0] * packet_size_list[j] * 8 / 1000000000
            throughput_list.append(throughput)
        throughput_list_list.append(throughput_list)

    baseline_throughput_list = []
    for i in range(len(tree_depth_list)):
        throughput_list = []
        for j in range(len(packet_size_list)):
            row_index = i * len(packet_size_list) + j
            # get the throughput of row of index row_index
            throughput = df.values[row_index][2]
            throughput = eval(throughput)[0][0] * packet_size_list[j] * 8 / 1000000000
            throughput_list.append(throughput)
        baseline_throughput_list.append(throughput_list)

    # plot the throughput
    # x axis: packet size
    # y axis: throughput
    # legend: number of rules
    # number of rules = 2 ^ tree_depth
    # line plot
    color_list = ["b", "g", "r", "c"]
    for i in range(len(tree_depth_list)):
        color = color_list[i]
        plt.plot(packet_size_list, throughput_list_list[i], label=str(2 ** tree_depth_list[i]), marker="o", color=color)
        plt.plot(packet_size_list, baseline_throughput_list[i], label=str(2 ** tree_depth_list[i]) + " (baseline)", marker="^", linestyle="--", color=color)

    number_of_rules_list = [2 ** i for i in tree_depth_list]
    color_list = ["b", "g", "r", "c"]
    number_of_rule_color_list = []
    # sfc_length_color_list.append(matplotlib.patches.Patch(color=color_list[i], label=str(sfc_length_list[i])))
    for i in range(len(number_of_rules_list)):
        number_of_rule_color_list.append(matplotlib.patches.Patch(color=color_list[i], label=str(number_of_rules_list[i])))
    # second row
    line_style_list = ["-", "--"]
    marker_list = ["o", "^"]
    experiment_type_list = ["optimized", "baseline"]
    line_style_marker_experiment_type_list = []
    for i in range(len(line_style_list)):
        marker_style = marker_list[i]
        line_style = line_style_list[i]
        experiment_type = experiment_type_list[i]
        line_style_marker_experiment_type_list.append(matplotlib.lines.Line2D([0], [0], color='black', marker=marker_style, linestyle=line_style, label=experiment_type))
    # create legend
    # show at bottom
    # 7 columns
    plt.legend(handles=number_of_rule_color_list + line_style_marker_experiment_type_list, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3,fancybox=True, shadow=True, title="Number of Rules")


    plt.xlabel("Packet Size (Bytes)")
    plt.ylabel("Throughput (Gbps)")
    # plt.legend(title="Number of Rules")
    plt.title("Throughput vs Packet Size")
    plt.gcf().set_size_inches(8, 8)
    plt.tight_layout()
    plt.savefig("upf_packet_size.png")
    plt.show()