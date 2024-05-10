import matplotlib

if __name__ == "__main__":
    # read optimized_sfc_bk.csv
    import pandas as pd

    df = pd.read_csv("optimized_sfc.csv")
    sfc_length_list = [1, 2, 3, 4, 5, 6]
    interleaved_threads_list = [1, 2, 4, 8, 16, 32]
    throughput_list = []
    for i, sfc_length in enumerate(sfc_length_list):
        for j, interleaved_threads in enumerate(interleaved_threads_list):
            row_index = i * len(interleaved_threads_list) + j
            # get the throughput of row of index row_index
            throughput = df.values[row_index][2]
            throughput = eval(throughput)
            throughput_list.append(
                throughput[0][0]/1000000)  # we only care about the first measurement of the first core for now
    # 6 lines of throughput for each sfc length for different number of interleaved threads
    # each line has 6 elements, each element is the throughput of different length of sfc
    # each line corresponds to a different number of interleaved threads
    throughput_list = [throughput_list[i:i + 6] for i in range(0, len(throughput_list), 6)]
    # plot the line chart of throughput of interleaved method and rtc
    # x axis: sfc length
    # y axis: throughput
    import matplotlib.pyplot as plt

    matplotlib.rcParams.update({'font.size': 25})
    matplotlib.rcParams.update({'legend.fontsize': 20})
    matplotlib.rcParams.update({'axes.labelsize': 25})
    matplotlib.rcParams.update({'xtick.labelsize': 25})
    matplotlib.rcParams.update({'ytick.labelsize': 25})

    import numpy as np

    # plot as bar chart instead
    # with different patterns
    # total 9 bars
    width = 0.1
    x = np.arange(len(sfc_length_list) -1)

    # read sfc_cuckoo_hash_rtc_bk.csv as the baseline
    df_baseline = pd.read_csv("sfc_cuckoo_hash_rtc.csv")
    sfc_length_list = [1, 2, 3, 4, 5, 6]
    baseline_throughput_list = []
    for i, sfc_length in enumerate(sfc_length_list):
        row_index = i
        throughput = df_baseline.values[row_index][2]
        throughput = eval(throughput)
        throughput = throughput[0][0]/1000000
        baseline_throughput_list.append(throughput)
    # plot as a dashed line
    # plt.plot(sfc_length_list, throughput_list, label="RTC", color="black", linestyle="--")

    hatch_list = ['/', 'x', '\\', 'o', '.', 'O', '*', '0', '+', '-']
    color_list = ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F', '#EDC948', '#B07AA1', '#FF9DA7', '#9C755F',
                  '#BAB0AC']
    i = 0
    plt.bar(x - 4 * width, baseline_throughput_list[1:], width, label="RTC BESS",
            color=color_list[i], hatch=hatch_list[i], alpha=0.99)
    i += 1
    plt.bar(x - 3 * width, throughput_list[0][1:], width, label="1 NFTask", color = color_list[i], hatch=hatch_list[i], alpha=0.99)
    i += 1

    plt.bar(x - 2 * width, throughput_list[1][1:], width, label="2 NFTasks", color = color_list[i], hatch=hatch_list[i], alpha=0.99)
    i += 1

    plt.bar(x - width, throughput_list[2][1:], width, label="4 NFTasks",
            color=color_list[i], hatch=hatch_list[i], alpha=0.99)
    i += 1

    plt.bar(x, throughput_list[3][1:], width, label="8 NFTasks",
            color=color_list[i], hatch=hatch_list[i], alpha=0.99)
    i += 1

    plt.bar(x + width, throughput_list[4][1:], width, label="16 NFTasks",
            color=color_list[i], hatch=hatch_list[i], alpha=0.99)
    i += 1

    plt.bar(x + 2 * width, throughput_list[5][1:], width, label="32 NFTasks",
            color=color_list[i], hatch=hatch_list[i], alpha=0.99)

    print(baseline_throughput_list)
    print(throughput_list[0][1:])
    print(throughput_list[1][1:])
    print(throughput_list[2][1:])
    print(throughput_list[3][1:])
    print(throughput_list[4][1:])
    print(throughput_list[5][1:])


    # show numbers on top of bars
    plt.xticks(x, sfc_length_list[1:])
    plt.xlabel("SFC length")
    plt.ylabel("Throughput (Mpps)")

    # plot the line of 16 threads with data packing
    base_index = len(interleaved_threads_list) * len(sfc_length_list) + interleaved_threads_list.index(16) * len(
        sfc_length_list)
    row_num_list = [base_index + i for i in range(len(sfc_length_list))]

    throughput_list = []
    for row_index in row_num_list:
        throughput = df.values[row_index][2]
        throughput = eval(throughput)
        throughput = throughput[0][0] / 1000000
        throughput_list.append(throughput)

    # skip the first bar
    # plt.plot(sfc_length_list, throughput_list, label="16 threads +DP", color="pink")
    i += 1
    plt.bar(x + 3 * width, throughput_list[:-1], width, label="16 NFTasks+DP", color=color_list[i], hatch=hatch_list[i], alpha=0.99)


    # plot the line of 16 threads with data packing and with redundant matching removal
    base_index = len(interleaved_threads_list) * len(sfc_length_list) * 2 + interleaved_threads_list.index(16) * len(
        sfc_length_list)
    row_num_list = [base_index + i for i in range(len(sfc_length_list))]
    throughput_list = []
    for row_index in row_num_list:
        throughput = df.values[row_index][2]
        throughput = eval(throughput)
        throughput = throughput[0][0] / 1000000
        throughput_list.append(throughput)
    # plt.plot(sfc_length_list, throughput_list, label="16 threads +DP + MR", color="pink")

    i += 1
    plt.bar(x + 4 * width, throughput_list[:-1], width, label="16 NFTasks+DP+MR", color=color_list[i], hatch=hatch_list[i], alpha=0.99)
    print(throughput_list[:-1])
    # put legend inside the box at the top
    # with three rows and three columns
    plt.legend(loc="upper center", bbox_to_anchor=(0.5, 1), ncol=4, fancybox=True, shadow=True)
    plt.ylim(0, 10)
    # size of the figure
    plt.gcf().set_size_inches(w = 18, h = 6)
    plt.tight_layout()
    plt.savefig("sfc_comparison_throughput.pdf")
    plt.show()


    matplotlib.rcParams.update({'font.size': 22})
    matplotlib.rcParams.update({'legend.fontsize': 20})
    matplotlib.rcParams.update({'axes.labelsize': 22})
    matplotlib.rcParams.update({'xtick.labelsize': 22})
    matplotlib.rcParams.update({'ytick.labelsize': 22})


    # plot the bar chart of l1 miss per packet of optimal one and the baseline
    # plot the line of 16 threads with data packing and with redundant matching removal

    x = np.arange(len(sfc_length_list) - 1)
    base_index = len(interleaved_threads_list) * len(sfc_length_list) * 2 + interleaved_threads_list.index(16) * len(
        sfc_length_list)
    row_num_list = [base_index + i for i in range(len(sfc_length_list))]
    throughput_list = []
    for row_index in row_num_list:
        throughput = df.values[row_index][2]
        throughput = eval(throughput)
        throughput = throughput[0][0]
        throughput_list.append(throughput)

    df = pd.read_csv("optimized_sfc.csv")
    l1_miss_list = []
    for row_index in row_num_list:
        l1_miss = df["L1-dcache-load-misses"][row_index]
        l1_miss = eval(l1_miss)
        l1_miss_list.append(l1_miss[0])

    l1_miss_per_packet_list = [l1_miss / throughput for l1_miss, throughput in zip(l1_miss_list, throughput_list)]
    # bar chart of l1 miss per packet
    width = 0.2



    # read sfc_cuckoo_hash_rtc.csv as the baseline
    df_baseline = pd.read_csv("sfc_cuckoo_hash_rtc.csv")
    sfc_length_list = [2, 3, 4, 5, 6]
    baseline_l1_miss_list = []
    for i, sfc_length in enumerate(sfc_length_list):
        l1_miss = df_baseline["L1-dcache-load-misses"][i]
        l1_miss = eval(l1_miss)
        baseline_l1_miss_list.append(l1_miss[0])
    baseline_throughput_list = []
    for i, sfc_length in enumerate(sfc_length_list):
        throughput = df_baseline["0_throughput"][i]
        throughput = eval(throughput)
        throughput = throughput[0][0]
        baseline_throughput_list.append(throughput)

    baseline_l1_miss_per_packet_list = [l1_miss / throughput for l1_miss, throughput in
                                        zip(baseline_l1_miss_list, baseline_throughput_list)]
    i = 0
    plt.bar(x - width / 2, baseline_l1_miss_per_packet_list, width, label="RTC BESS",
            color=color_list[i], hatch=hatch_list[i], alpha=0.99)
    i = 1
    plt.bar(x + width / 2, l1_miss_per_packet_list[1:], width, label="16 NFTasks+DP+MR", color=color_list[i], hatch=hatch_list[i], alpha=0.99)
    plt.xticks(x, sfc_length_list)
    plt.xlabel("SFC length")
    plt.ylabel("L1 miss per packet")
    # plt.legend(loc="upper center", bbox_to_anchor=(0.5, 1.35), ncol=4, fancybox=True, shadow=True)
    # size of the figure
    # plt.gcf().set_size_inches(8, 3.5)
    # y show every 10
    plt.legend()
    plt.yticks(np.arange(0, 50, 10))
    plt.tight_layout()
    plt.savefig("sfc_comparison_l1_miss_per_packet.pdf")
    plt.show()

    # plot the bar chart of ipc of optimal one and the baseline
    # plot the line of 16 threads with data packing and with redundant matching removal
    sfc_length_list = [1, 2, 3, 4, 5, 6]
    x = np.arange(len(sfc_length_list))
    base_index = len(interleaved_threads_list) * len(sfc_length_list) * 2 + interleaved_threads_list.index(16) * len(
        sfc_length_list)
    row_num_list = [base_index + i for i in range(len(sfc_length_list))]
    ipc_interleaved_list = []
    df = pd.read_csv("optimized_sfc.csv")
    for row_index in row_num_list:
        ipc = df["ipc"][row_index]
        ipc = eval(ipc)
        ipc_interleaved_list.append(ipc[0])


    df = pd.read_csv("sfc_cuckoo_hash_rtc.csv")
    row_num_list = [i for i in range(6)]
    ipc_list = []
    for row_index in row_num_list:
        ipc = df["ipc"][row_index]
        ipc = eval(ipc)
        ipc_list.append(ipc[0])

    # bar chart of ipc
    x = np.arange(len(sfc_length_list) - 1)
    width = 0.2

    i = 0

    plt.bar(x - width / 2, ipc_list[1:], width, label="RTC BESS",
            color=color_list[i], hatch=hatch_list[i], alpha=0.99)

    i = 1
    plt.bar(x + width / 2, ipc_interleaved_list[1:], width, label="16 NFTasks+DP+MR",  color=color_list[i], hatch=hatch_list[i], alpha=0.99)

    plt.xticks(x, sfc_length_list[1:])
    plt.xlabel("SFC length")
    plt.ylabel("IPC")
    # y show every 0.25
    # y range from 0.5 to 1
    plt.ylim(0.5, 1.2)

    # plt.legend(loc="upper center", bbox_to_anchor=(0.5, 1.35), ncol=4, fancybox=True, shadow=True)
    # size of the figure
    # plt.gcf().set_size_inches(8, 3.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig("sfc_comparison_ipc.pdf")
    plt.show()


