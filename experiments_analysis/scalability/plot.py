import matplotlib
import pandas as pd
from matplotlib import pyplot as plt

if __name__ == "__main__":

    matplotlib.rcParams.update({'font.size': 20})
    matplotlib.rcParams.update({'legend.fontsize': 13})
    matplotlib.rcParams.update({'axes.labelsize': 18})
    matplotlib.rcParams.update({'xtick.labelsize': 18})
    matplotlib.rcParams.update({'ytick.labelsize': 18})
    matplotlib.rcParams.update({'lines.markersize': 8})

    # read cuckoo_hash_rtc.csv as a dataframe
    baseline = pd.read_csv("cuckoo_hash_rtc.csv")
    # read cuckoo_hash_interleaved.csv as a dataframe
    interleaved = pd.read_csv("cuckoo_hash_interleaved.csv")
    packet_size_list = [64, 128, 256, 512]
    core_list = [1, 2, 3, 4, 5, 6, 7]
    baseline_throughput_list_list = [
        [],
        [],
        [],
        []
    ]
    interleaved_throughput_list_list = [
        [],
        [],
        [],
        []
    ]
    for i in range(len(core_list)):
        for j in range(len(packet_size_list)):
            packet_size = packet_size_list[j]
            row_num = i * len(packet_size_list) + j
            baseline_throughput = eval(baseline.values[row_num][2])
            baseline_throughput_list_list[j].append(sum(baseline_throughput[0]) * 8 * (packet_size + 16) / 1000000000)
            interleaved_throughput = eval(interleaved.values[row_num][2])
            interleaved_throughput_list_list[j].append(
                sum(interleaved_throughput[0]) * 8 * (packet_size + 16) / 1000000000)
    print(baseline_throughput_list_list)
    print(interleaved_throughput_list_list)


    for i in range(len(baseline_throughput_list_list)):
        for j in range(len(baseline_throughput_list_list[i])):
            baseline_throughput = baseline_throughput_list_list[i][j]
            interleaved_throughput = interleaved_throughput_list_list[i][j]
            improvement = (interleaved_throughput - baseline_throughput) / baseline_throughput * 100
            print("packet size: " + str(packet_size_list[i]) + "B, core number: " + str(core_list[j]) + ", improvement: " + str(improvement) + "%")
    # plot the throughput
    # x axis: core number
    # y axis: throughput
    # legend: packet size
    # line plot
    color_list = ["b", "g", "r", "c"]
    # set the size of the figure
    # plt.gcf().set_size_inches(8, 8)
    plt.figure(figsize=(10, 5))

    for i in range(len(packet_size_list)):
        color = color_list[i]
        packet_size = packet_size_list[i]
        packet_size_str = str(packet_size) + "B"
        plt.plot(core_list, baseline_throughput_list_list[i], label=packet_size_str, marker="o", color=color , linestyle="--")
        plt.plot(core_list, interleaved_throughput_list_list[i], label=packet_size_str + " (interleaved)",
                 marker="^", linestyle="-", color=color)

    import matplotlib.patches as mpatches

    line_style_list = ["-", "--"]
    marker_list = ["^", "o"]
    color_lengend_list = ["b", "g", "r", "c"]
    exp_type = ["interleaved", "monolithic"]
    legend_list = []
    for i in range(len(packet_size_list)):
        packet_size = packet_size_list[i]
        packet_size_str = str(packet_size) + "B"
        legend_list.append(matplotlib.patches.Patch(color=color_lengend_list[i], label=packet_size_str))

    exp_type_lengend_list = []
    for i in range(len(exp_type)):
        exp_type_lengend_list.append(matplotlib.lines.Line2D([0], [0], color='black', marker=marker_list[i], linestyle=line_style_list[i], label=exp_type[i]))
    plt.ylim(0, 110)
    # lengend to figure below
    plt.legend(handles=legend_list + exp_type_lengend_list,
                loc='upper center', bbox_to_anchor=(0.45, 1), ncol=3, fancybox=True, shadow=True)
    # plt.gcf().set_size_inches(w = 7, h = 7)
    plt.xlabel("Number of Cores")
    plt.ylabel("Throughput (Gbps)")
    # make sure y label is not cut off
    plt.tight_layout()
    plt.savefig("scalability.pdf")
    plt.show()

