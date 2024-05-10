# read cuckoo_hash_interleaved.csv
import matplotlib
import pandas as pd

if __name__ == "__main__":

    df1 = pd.read_csv("cuckoo_hash_interleaved.csv")
    df2 = pd.read_csv("cuckoo_hash_rtc.csv")
    # df1.to_csv("cuckoo_hash_interleaved.csv")
    # df2.to_csv("cuckoo_hash_rtc.csv")
    packet_size_list = [64, 128, 256, 512, 1024, 1280, 1512]
    concurrency = [17, 18, 19, 20]
    for i in range(len(packet_size_list)):
        packet_size_list[i] = (packet_size_list[i] + 20) * 8

    interleaved_throughput = []
    for i in df1.values[7:14]:
        temp_list = eval(i[2])[:5]
        packet_size = packet_size_list[i[0] - 7]
        for j in range(len(temp_list)):
            for k in range(len(temp_list[j])):
                temp_list[j][k] = temp_list[j][k] * packet_size / 1000000000
        interleaved_throughput.append(temp_list)
    print(interleaved_throughput)

    rtc_throughput = []
    for i in df2.values[7:14]:
        temp_list = eval(i[2])[:5]
        packet_size = packet_size_list[i[0] - 7]
        for j in range(len(temp_list)):
            for k in range(len(temp_list[j])):
                temp_list[j][k] = temp_list[j][k] * packet_size / 1000000000
        rtc_throughput.append(temp_list)
    print(rtc_throughput)

    # plot the line chart of throughput of interleaved method and rtc
    # x axis: packet size (bytes)
    # y axis: throughput
    import matplotlib.pyplot as plt
    import numpy as np

    matplotlib.rcParams.update({'font.size': 35})
    matplotlib.rcParams.update({'legend.fontsize': 30})
    matplotlib.rcParams.update({'axes.labelsize': 32})
    matplotlib.rcParams.update({'xtick.labelsize': 35})
    matplotlib.rcParams.update({'ytick.labelsize': 35})
    matplotlib.rcParams.update({'lines.markersize': 15})
    packet_size_list = [64, 128, 256, 512, 1024, 1280, 1518]

    representative_rtc_throughput = []
    representative_interleaved_throughput = []
    for i in range(len(packet_size_list)):
        temp_rtc_throughput = [i[0] for i in rtc_throughput[i]]
        temp_interleaved_throughput = [i[0] for i in interleaved_throughput[i]]
        representative_rtc_throughput.append(np.mean(temp_rtc_throughput))
        representative_interleaved_throughput.append(np.mean(temp_interleaved_throughput))

    plt.plot(packet_size_list, representative_rtc_throughput, label="monolithic", color="blue")
    plt.plot(packet_size_list, representative_interleaved_throughput, label="interleaved", color="orange")
    # for each point in representative_rtc_throughput and representative_interleaved_throughput
    # plot a point with error bar
    for i in range(len(packet_size_list)):
        temp_rtc_throughput = [i[0] for i in rtc_throughput[i]]
        temp_interleaved_throughput = [i[0] for i in interleaved_throughput[i]]
        plt.errorbar(packet_size_list[i], representative_rtc_throughput[i], yerr=np.std(temp_rtc_throughput), fmt="o",
                     color="blue")
        plt.errorbar(packet_size_list[i], representative_interleaved_throughput[i],
                     yerr=np.std(temp_interleaved_throughput), fmt="o", color="orange")

    # for the last comparison, plot the improvement of interleaved method over rtc using text annotation below the point
    # the upper arrow points to the upper point
    # the lower arrow points to the lower point
    # the text is at the middle of the two points
    improvement = (representative_interleaved_throughput[-1] - representative_rtc_throughput[-1]) / \
                  representative_rtc_throughput[-1] * 100
    upper_point = max(representative_interleaved_throughput[-1], representative_rtc_throughput[-1])
    lower_point = min(representative_interleaved_throughput[-1], representative_rtc_throughput[-1])
    middle_point = (upper_point + lower_point) / 2
    # connect the two points with a line and arrows at two ends
    # plt.annotate("", xy=(packet_size_list[-1], representative_interleaved_throughput[-1]), xytext=(packet_size_list[-1], representative_rtc_throughput[-1]), arrowprops=dict(arrowstyle="<->"))
    # add text at the left of the line
    # plt.text(packet_size_list[-1] - 120, middle_point - 2, "{:.2f}%".format(improvement), color="red")
    plt.xlabel("Packet Size (bytes)")
    plt.ylabel("Throughput (Gbps)")
    plt.legend()
    plt.gcf().set_size_inches(10, 8)
    plt.tight_layout()
    plt.savefig("interleaved_vs_rtc_2.pdf")
    plt.show()
