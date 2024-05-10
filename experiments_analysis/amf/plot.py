import matplotlib

if __name__ == "__main__":
    # read test_amf.csv
    # plot the throughput as bar chart
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np

    matplotlib.rcParams.update({'font.size': 20})
    matplotlib.rcParams.update({'legend.fontsize': 16})
    matplotlib.rcParams.update({'axes.labelsize': 20})
    matplotlib.rcParams.update({'xtick.labelsize': 20})
    matplotlib.rcParams.update({'ytick.labelsize': 20})


    df = pd.read_csv("test_amf.csv")
    df_throughput_list = df["0_throughput"]
    throughput_list = []
    packet_num_list = []
    for throughput in df_throughput_list:
        throughput = eval(throughput)
        packet_num_list.append(throughput[0][0])
        throughput_list.append(throughput[0][0] * 8 * 140 / 1000000000)

    print(throughput_list)
    df_baseline = pd.read_csv("test_amf_baseline.csv")
    df_baseline_throughput_list = df_baseline["0_throughput"]
    baseline_throughput = eval(df_baseline_throughput_list[0])[0][0] * 8 * 140 / 1000000000
    throughput_list = [throughput_list[1], throughput_list[0]]
    x_axis_list = [
        "monolithic", "CG-P", "FG-P",
    ]
    print(throughput_list)
    print(baseline_throughput)
    for i in range(len(throughput_list)):
        improvement = (throughput_list[i] - baseline_throughput) / baseline_throughput * 100
        print(f"{x_axis_list[i]}: {throughput_list[i]} Gbps, {improvement}%")

    x = np.arange(len(x_axis_list))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x, [baseline_throughput] + throughput_list, width, label='Throughput', color='black')
    # fill the rectangle with shape
    for rect in rects1:
        height = rect.get_height()
        # only show 2 decimal places
        # ax.text(rect.get_x() + rect.get_width() / 2., 1.0 * height,
        #         '%.2f' % float(height),
        #         ha='center', va='bottom')
        # ax.text(rect.get_x() + rect.get_width() / 2.,
        #         ha='center', va='bottom')
    # y range 0 to 50
    ax.set_ylim(0, 8)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Throughput (Gbps)')
    # ax.set_title('Simplified AMF Single Core Performance')
    ax.set_xticks(x)
    ax.set_xticklabels(x_axis_list)
    # make the x axis label slighly slanted to avoid overlapping
    plt.setp(ax.get_xticklabels())
    # ax.legend()

    fig.tight_layout()

    plt.savefig("amf_throughput_comparison.pdf")
    plt.show()

    # calculate L1 miss per packet
    df = pd.read_csv("test_amf.csv")
    df_l1_miss_list = df["L1-dcache-load-misses"]
    l1_miss_list = []
    for l1_miss in df_l1_miss_list:
        temp = eval(l1_miss)
        l1_miss_list.append(temp[0])
    l1_miss_per_packet_list = [l1_miss / packet_num for l1_miss, packet_num in zip(l1_miss_list, packet_num_list)]
    print(l1_miss_per_packet_list)
    cg_p_l1_miss_per_packet = l1_miss_per_packet_list[1]
    fg_p_l1_miss_per_packet = l1_miss_per_packet_list[0]
    non_temporal_l1_miss_per_packet = l1_miss_per_packet_list[3]
    baseline_l1_miss_per_packet = eval(df_baseline["L1-dcache-load-misses"][0])[0] / eval(df_baseline["0_throughput"][0])[0][0]
    print(baseline_l1_miss_per_packet)
    # plot the L1 miss per packet as bar chart
    x_axis_list = [
        "monolithic", "CG-P", "FG-P"
    ]

    x = np.arange(len(x_axis_list))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()

    rects1 = ax.bar(x, [baseline_l1_miss_per_packet, cg_p_l1_miss_per_packet, fg_p_l1_miss_per_packet], width, label='L1 Miss per Packet', color='black')
    # fill the rectangle with shape
    for rect in rects1:
        height = rect.get_height()
        # only show 2 decimal places
        # ax.text(rect.get_x() + rect.get_width() / 2., 1.0 * height,
        #         '%.2f' % float(height),
        #         ha='center', va='bottom')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('L1 Miss per Packet')
    # ax.set_title('Simplified AMF Single Core Performance')
    # y range from 0 - 25
    ax.set_ylim(0, 25)
    ax.set_xticks(x)
    ax.set_xticklabels(x_axis_list)
    # make the x axis label slighly slanted to avoid overlapping
    plt.setp(ax.get_xticklabels())
    # ax.legend()

    fig.tight_layout()
    plt.savefig("amf_l1_miss_per_packet.pdf")
    plt.show()





