import matplotlib
import pandas as pd

if __name__ == "__main__":
    matplotlib.rcParams.update({'font.size': 30})
    matplotlib.rcParams.update({'legend.fontsize': 25})
    matplotlib.rcParams.update({'axes.labelsize': 30})
    matplotlib.rcParams.update({'xtick.labelsize': 30})
    matplotlib.rcParams.update({'ytick.labelsize': 30})

    # read upf_monolithic.csv
    df1 = pd.read_csv("upf_monolithic.csv")
    # read upf_interleaved.csv
    df2 = pd.read_csv("upf_interleaved.csv")

    number_of_interleaved_threads = [1, 2, 4, 8, 16, 32, 64, 128]
    number_of_rules = [16, 32, 64, 128]

    monotlithic_throughput = []
    for i in df1.values:
        throughput = eval(i[2])
        monotlithic_throughput.append(throughput[0][0] / 1000000)
    interleaved_throughput = []
    row_number = 0
    for i in number_of_interleaved_threads:
        temp_list = []
        for j in number_of_rules:
            throughput = eval(df2.values[row_number][2])
            temp_list.append(throughput[0][0] / 1000000)
            row_number += 1
        interleaved_throughput.append(temp_list)

    # plot the throughput as bar chart
    # 8 types of bars
    # each type corresponds to 4 choices of number of rules

    import matplotlib.pyplot as plt
    import numpy as np

    width = 0.1
    x = np.arange(len(number_of_rules))
    fig, ax = plt.subplots()
    # use the same setup as
    # plt.bar(x - 4 * width, baseline_throughput_list, width, label="RTC", color="black", hatch="....")
    #
    # plt.bar(x - 3 * width, throughput_list[0], width, label="1 thread", color="blue", hatch="\\\\\\\\")
    # plt.bar(x - 2 * width, throughput_list[1], width, label="2 threads", color="orange", hatch="////")
    # plt.bar(x - width, throughput_list[2], width, label="4 threads", color="green", hatch="....")
    # plt.bar(x, throughput_list[3], width, label="8 threads", color="red", hatch="xxxx")
    # plt.bar(x + width, throughput_list[4], width, label="16 threads", color="purple", hatch="----")
    # plt.bar(x + 2 * width, throughput_list[5], width, label="32 threads", color="brown", hatch="++++")

    hatch_list = ['/', 'x', '\\', 'o', '.', 'O', '*', '0', '+', '-']
    color_list = ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F', '#EDC948', '#B07AA1', '#FF9DA7', '#9C755F',
                  '#BAB0AC']
    i = 0
    rects1 = ax.bar(x - 7 * width / 2, monotlithic_throughput, width, label='L25GC', color=color_list[i],
                    hatch=hatch_list[i], alpha=0.99)
    i += 1
    rects2 = ax.bar(x - 5 * width / 2, interleaved_throughput[0], width, label='1 NFTasks',
                    color=color_list[i], hatch=hatch_list[i], alpha=0.99)
    i += 1
    rects3 = ax.bar(x - 3 * width / 2, interleaved_throughput[1], width, label='2 NFTasks', color=color_list[i],
                    hatch=hatch_list[i], alpha=0.99)
    i += 1
    rects4 = ax.bar(x - width / 2, interleaved_throughput[2], width, label='4 NFTasks', color=color_list[i],
                    hatch=hatch_list[i], alpha=0.99)
    i += 1
    rects5 = ax.bar(x + width / 2, interleaved_throughput[3], width, label='8 NFTasks', color=color_list[i],
                    hatch=hatch_list[i], alpha=0.99)
    i += 1
    rects6 = ax.bar(x + 3 * width / 2, interleaved_throughput[4], width, label='16 NFTasks', color=color_list[i],
                    hatch=hatch_list[i], alpha=0.99)
    i += 1
    rects7 = ax.bar(x + 5 * width / 2, interleaved_throughput[5], width, label='32 NFTasks', color=color_list[i],
                    hatch=hatch_list[i], alpha=0.99)
    i += 1
    rects8 = ax.bar(x + 7 * width / 2, interleaved_throughput[6], width, label='64 NFTasks', color=color_list[i],
                    hatch=hatch_list[i], alpha=0.99)
    i += 1
    ax.set_ylabel('throughput (Mpps)', fontsize=30)
    ax.set_xlabel('number of PDRs', fontsize=30)
    ax.set_xticks(x)
    ax.set_xticklabels(number_of_rules)
    ax.legend()
    plt.ylim(0, 5)
    plt.legend(loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=4, fancybox=True, shadow=True)
    # size of the figure
    # don't change h
    plt.gcf().set_size_inches(w=18, h=6)
    fig.tight_layout()
    plt.savefig("upf_interleaved_vs_monolithic.pdf")
    plt.show()

    # plot the bar chart of l1 miss per packet of optimal one and the baseline

    matplotlib.rcParams.update({'font.size': 22})
    matplotlib.rcParams.update({'legend.fontsize': 20})
    matplotlib.rcParams.update({'axes.labelsize': 22})
    matplotlib.rcParams.update({'xtick.labelsize': 22})
    matplotlib.rcParams.update({'ytick.labelsize': 22})

    # read upf_monolithic.csv
    df1 = pd.read_csv("upf_monolithic.csv")
    # read upf_interleaved.csv
    df2 = pd.read_csv("upf_interleaved.csv")

    throughput_list = []
    monolithic_l1_miss = []
    for i in range(len(df1.values)):
        throughput = eval(df1.values[i][2])
        throughput_list.append(throughput[0][0])
        l1_miss = eval(df1["L1-dcache-load-misses"][i])[0]
        monolithic_l1_miss.append(l1_miss)
    monolithic_l1_miss_per_packet = [i / j for i, j in zip(monolithic_l1_miss, throughput_list)]

    interleaved_l1_miss = []
    throughput_list = []
    row_number = 0
    base_row_number = len(number_of_rules) * number_of_interleaved_threads.index(16)
    for i in number_of_rules:
        l1_miss = df2["L1-dcache-load-misses"][base_row_number + row_number]
        l1_miss = eval(l1_miss)[0]
        throughput = eval(df2.values[base_row_number + row_number][2])
        throughput_list.append(throughput[0][0])
        row_number += 1
        interleaved_l1_miss.append(l1_miss)
    interleaved_l1_miss_per_packet = [i / j for i, j in zip(interleaved_l1_miss, throughput_list)]

    # plot the l1 miss per packet as bar chart

    import matplotlib.pyplot as plt
    import numpy as np

    width = 0.2
    x = np.arange(len(number_of_rules))
    fig, ax = plt.subplots()
    i = 0
    rects1 = ax.bar(x - width / 2, monolithic_l1_miss_per_packet, width, label='L25GC', color=color_list[i],
                    hatch=hatch_list[i], alpha=0.99)
    i += 1
    rects2 = ax.bar(x + width / 2, interleaved_l1_miss_per_packet, width, label='16 NFTasks', color=color_list[i],
                    hatch=hatch_list[i], alpha=0.99)

    # y range 0 to 40
    ax.set_ylim(0, 40)
    ax.set_ylabel('L1 miss per packet', fontsize=30)
    ax.set_xlabel('number of PDRs', fontsize=30)
    ax.set_xticks(x)
    ax.set_xticklabels(number_of_rules)
    ax.legend()
    # plt.legend(loc="upper center", bbox_to_anchor=(0.5, 1.5), ncol=2, fancybox=True, shadow=True)
    # size of the figure
    # plt.gcf().set_size_inches(8, 8)
    ax.set_ylim(15, 40)
    fig.tight_layout()
    plt.savefig("upf_interleaved_vs_monolithic_l1_miss.pdf")
    plt.show()

    # plot the bar chart of ipc
    # read upf_monolithic.csv

    df1 = pd.read_csv("upf_monolithic.csv")
    # read upf_interleaved.csv
    df2 = pd.read_csv("upf_interleaved.csv")

    monolithic_ipc = []
    for i in range(len(df1.values)):
        ipc = eval(df1["ipc"][i])[0]
        monolithic_ipc.append(ipc)

    interleaved_ipc = []
    row_number = 0
    base_row_number = len(number_of_rules) * number_of_interleaved_threads.index(16)
    for i in number_of_rules:
        ipc = df2["ipc"][base_row_number + row_number]
        interleaved_ipc.append(eval(ipc)[0])
        row_number += 1

    # plot ipc as bar chart

    import matplotlib.pyplot as plt
    import numpy as np

    width = 0.2
    x = np.arange(len(number_of_rules))
    fig, ax = plt.subplots()

    i = 0
    rects1 = ax.bar(x - width / 2, monolithic_ipc, width, label='L25GC',
                    color=color_list[i], hatch=hatch_list[i], alpha=0.99)
    i += 1
    rects2 = ax.bar(x + width / 2, interleaved_ipc, width, label='16 NFTasks', color=color_list[i], hatch=hatch_list[i],
                    alpha=0.99)

    ax.set_ylabel('IPC', fontsize=30)
    ax.set_xlabel('number of PDRs', fontsize=30)
    ax.set_xticks(x)
    ax.set_xticklabels(number_of_rules)
    # y range 0 to 1
    ax.set_ylim(0, 1)
    # show every 0.25
    ax.set_ylim(0.4, 0.8)
    ax.legend()
    # size of the figure
    # plt.gcf().set_size_inches(6, 6)
    fig.tight_layout()
    plt.savefig("upf_interleaved_vs_monolithic_ipc.pdf")
    plt.show()

    # plot the l2 miss per packet as bar chart

    # read upf_monolithic.csv
    df1 = pd.read_csv("upf_monolithic.csv")
    # read upf_interleaved.csv
    df2 = pd.read_csv("upf_interleaved.csv")

    throughput_list = []
    monolithic_l2_miss = []
    for i in range(len(df1.values)):
        throughput = eval(df1.values[i][2])
        throughput_list.append(throughput[0][0])
        l2_miss = eval(df1["l2_rqsts.demand_data_rd_miss"][i])[0]
        monolithic_l2_miss.append(l2_miss)

    monolithic_l2_miss_per_packet = [i / j for i, j in zip(monolithic_l2_miss, throughput_list)]

    interleaved_l2_miss = []
    throughput_list = []
    row_number = 0
    base_row_number = len(number_of_rules) * number_of_interleaved_threads.index(16)
    for i in number_of_rules:
        l2_miss = df2["l2_rqsts.demand_data_rd_miss"][base_row_number + row_number]
        l2_miss = eval(l2_miss)[0]
        throughput = eval(df2.values[base_row_number + row_number][2])
        throughput_list.append(throughput[0][0])
        row_number += 1
        interleaved_l2_miss.append(l2_miss)
    interleaved_l2_miss_per_packet = [i / j for i, j in zip(interleaved_l2_miss, throughput_list)]

    # plot the l2 miss per packet as bar chart

    import matplotlib.pyplot as plt
    import numpy as np

    width = 0.2
    x = np.arange(len(number_of_rules))
    fig, ax = plt.subplots()
    i = 0
    rects1 = ax.bar(x - width / 2, monolithic_l2_miss_per_packet, width, label='L25GC', color=color_list[i],
                    hatch=hatch_list[i], alpha=0.99)
    i += 1
    rects2 = ax.bar(x + width / 2, interleaved_l2_miss_per_packet, width, label='16 NFTasks', color=color_list[i],
                    hatch=hatch_list[i], alpha=0.99)

    # y range 0 to 40
    # ax.set_ylim(0, 40)
    ax.set_ylabel('L2 miss per packet', fontsize=30)
    ax.set_xlabel('number of PDRs', fontsize=30)
    ax.set_xticks(x)
    ax.set_xticklabels(number_of_rules)
    ax.legend()

    # plt.legend(loc="upper center", bbox_to_anchor=(0.5, 1.5), ncol=2, fancybox=True, shadow=True)
    # size of the figure
    # plt.gcf().set_size_inches(8, 8)
    # ax.set_ylim(15, 40)
    fig.tight_layout()
    plt.savefig("upf_interleaved_vs_monolithic_l2_miss.pdf")
    plt.show()

    # plot the L1/L2 miss per packet in one figure with two y axis
    # already have the data
    fig, ax = plt.subplots(figsize=(10, 10))
    ax2 = ax.twinx()
    i = 0
    rects1 = ax.bar(x - width / 2 - width, monolithic_l1_miss_per_packet, width, label='L1C L25GC',
                    color=color_list[i],
                    hatch=hatch_list[i], alpha=0.99)
    i = 1
    rects3 = ax.bar(x -  width / 2, interleaved_l1_miss_per_packet, width, label='L1C 16 NFTasks',
                    color=color_list[i],
                    hatch=hatch_list[i], alpha=0.99)


    i =  2
    rects2 = ax2.bar(x + width / 2, monolithic_l2_miss_per_packet, width, label='L2C L25GC',
                     color=color_list[i],
                     hatch=hatch_list[i], alpha=0.99)

    i = 3
    rects4 = ax2.bar(x + 3 * width / 2, interleaved_l2_miss_per_packet, width, label='L2C 16 NFTasks',
                     color=color_list[i],
                     hatch=hatch_list[i], alpha=0.99)

    ax.set_ylabel('L1 miss per packet')
    ax2.set_ylabel('L2 miss per packet')
    ax.set_xlabel('number of PDRS')
    ax.set_xticks(x)
    ax.set_xticklabels(number_of_rules)
    # legend at the top
    # two rows
    # first row for L25GC L1C and L2C
    # second row for 16 NFTasks L1C and L2C
    legend1 = ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.6), ncol=2, fancybox=True, shadow=True, fontsize=10)
    legend2 = ax2.legend(loc="upper center", bbox_to_anchor=(0.5, 1.5), ncol=2, fancybox=True, shadow=True, fontsize=10)
    # y range 0 to 40
    # ax.set_ylim(0, 40)
    # ax.set_ylim(15, 40)
    fig.tight_layout()
    plt.savefig("upf_interleaved_vs_monolithic_l1_l2_miss.pdf")
