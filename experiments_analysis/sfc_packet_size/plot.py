import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

if __name__ == "__main__":
    matplotlib.rcParams.update({'font.size': 20})
    matplotlib.rcParams.update({'legend.fontsize': 18})
    matplotlib.rcParams.update({'axes.labelsize': 20})
    matplotlib.rcParams.update({'xtick.labelsize': 20})
    matplotlib.rcParams.update({'ytick.labelsize': 20})
    # read optimized_sfc.csv
    df = pd.read_csv("optimized_sfc.csv")
    df2 = pd.read_csv("sfc_cuckoo_hash_rtc.csv")

    sfc_length_list = [1, 2, 3, 4, 5, 6]
    packet_size_list = [64, 128, 256, 512, 1024, 1280, 1518]

    throughput_list_list = []
    for i in range(len(sfc_length_list)):
        throughput_list = []
        for j in range(len(packet_size_list)):
            row_index = j * len(sfc_length_list) + i
            # get the throughput of row of index row_index
            throughput = df.values[row_index][2]
            throughput = eval(throughput)
            throughput = throughput[0][0] * packet_size_list[j] * 8 / 1000000000
            throughput_list.append(throughput)
        throughput_list_list.append(throughput_list)

    baseline_throughput_list = []
    for i in range(len(sfc_length_list)):
        throughput_list = []
        for j in range(len(packet_size_list)):
            row_index = j * len(sfc_length_list) + i
            # get the throughput of row of index row_index
            throughput = df2.values[row_index][2]
            throughput = eval(throughput)
            throughput = throughput[0][0] * packet_size_list[j] * 8 / 1000000000
            throughput_list.append(throughput)
        baseline_throughput_list.append(throughput_list)

    for i in range(len(sfc_length_list)):
        for j in range(len(packet_size_list)):
            sfc_throughput = throughput_list_list[i][j]
            baseline_throughput = baseline_throughput_list[i][j]
            improvement = (sfc_throughput - baseline_throughput) / baseline_throughput * 100
            print("sfc length: {}, packet size: {}, improvement: {:.2f}%".format(sfc_length_list[i], packet_size_list[j], improvement))
    # plot the throughput
    # x axis: packet size
    # y axis: throughput
    # legend: sfc length
    # matplotlib.rcParams.update({'font.size': 25})
    # matplotlib.rcParams.update({'legend.fontsize': 25})
    # matplotlib.rcParams.update({'axes.labelsize': 25})
    # matplotlib.rcParams.update({'xtick.labelsize': 25})
    # matplotlib.rcParams.update({'ytick.labelsize': 25})

    # plot
    import numpy as np

    # width = 0.1
    # x = np.arange(len(packet_size_list))
    # plt.bar(x - 3 * width, throughput_list_list[0], width, label="1", color="blue", hatch="\\\\\\\\")
    # plt.bar(x - 2 * width, throughput_list_list[1], width, label="2", color="orange", hatch="////")
    # plt.bar(x - width, throughput_list_list[2], width, label="3", color="green", hatch="....")
    # plt.bar(x, throughput_list_list[3], width, label="4", color="red", hatch="xxxx")
    # plt.bar(x + width, throughput_list_list[4], width, label="5", color="purple", hatch="++++")
    # plt.bar(x + 2 * width, throughput_list_list[5], width, label="6", color="brown", hatch="----")
    # plt.xticks(x, packet_size_list)
    # plt.xlabel("Packet Size (Bytes)")
    # plt.ylabel("Throughput (Gbps)")
    # plt.legend(title="SFC Length")
    # plt.show()
    plt.figure(figsize=(10, 5))

    # plot as line plot instead of bar plot
    # plt.plot(packet_size_list, throughput_list_list[0], label="1 (interleaved)", color="blue", marker="o")
    plt.plot(packet_size_list, throughput_list_list[1], label="2", color="orange", marker="^")
    # plt.plot(packet_size_list, throughput_list_list[2], label="3", color="green", marker="o")
    plt.plot(packet_size_list, throughput_list_list[3], label="4", color="red", marker="^")
    # plt.plot(packet_size_list, throughput_list_list[4], label="5", color="purple", marker="o")
    plt.plot(packet_size_list, throughput_list_list[5], label="6", color="brown", marker="^")

    # plot baseline using another marker and using dashed line, the same corresponding color
    # plt.plot(packet_size_list, baseline_throughput_list[0], label="1 (baseline)", color="blue", marker="^", linestyle="--")
    plt.plot(packet_size_list, baseline_throughput_list[1], label="2", color="orange", marker="o", linestyle="--")
    # plt.plot(packet_size_list, baseline_throughput_list[2], label="3", color="green", marker="^", linestyle="--")
    plt.plot(packet_size_list, baseline_throughput_list[3], label="4", color="red", marker="o", linestyle="--")
    # plt.plot(packet_size_list, baseline_throughput_list[4], label="5", color="purple", marker="^", linestyle="--")
    plt.plot(packet_size_list, baseline_throughput_list[5], label="6", color="brown", marker="o", linestyle="--")
    plt.xlabel("Packet Size (Bytes)")
    plt.ylabel("Throughput (Gbps)")
    plt.xlabel("Packet Size (Bytes)")
    plt.ylabel("Throughput (Gbps)")
    plt.legend(title="SFC Length")
    # concise legend
    # two rows
    # first row show the relationship between sfc length and color
    # second row show the relationship between line style, marker and experiment type
    # create legend handles
    # first row
    sfc_length_list = [2, 4, 6]
    color_list = ["orange", "green", "red", "purple", "brown"]
    sfc_length_color_list = []
    for i in range(len(sfc_length_list)):
        sfc_length_color_list.append(matplotlib.patches.Patch(color=color_list[i], label=str(sfc_length_list[i])))
    # second row
    line_style_list = ["-", "--"]
    marker_list = ["^", "o"]
    experiment_type_list = ["interleaved", "monolithic"]
    line_style_marker_experiment_type_list = []
    for i in range(len(line_style_list)):
        mark_style = marker_list[i]
        line_style = line_style_list[i]
        experiment_type = experiment_type_list[i]
        line_style_marker_experiment_type_list.append(matplotlib.lines.Line2D([], [], color='black', marker=mark_style, linestyle=line_style, label=experiment_type))
    # create legend
    # show at bottom
    # 7 columns
    # plt.legend(handles=sfc_length_color_list + line_style_marker_experiment_type_list, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3, fancybox=True, shadow=True, title="SFC Length")
    # show in the graph
    plt.legend(handles=sfc_length_color_list + line_style_marker_experiment_type_list, loc='upper center', bbox_to_anchor=(0.25, 1), ncol=2, fancybox=True, shadow=True, title="SFC Length")

    # plt.legend(title="SFC Length")
    # plt.gcf().set_size_inches(10, 8)
    plt.tight_layout()
    plt.savefig("sfc_packet_size.pdf")
    plt.show()
