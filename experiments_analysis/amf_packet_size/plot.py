import matplotlib

if __name__ == "__main__":
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np
    # read amf_monolithic.csv
    df1 = pd.read_csv("amf_monolithic.csv")
    df2 = pd.read_csv("test_amf.csv") # optimized

    packet_size_list = [64, 128, 256, 512, 1024, 1280, 1518]
    baseline_throughput_list = []
    row_index = 0
    for i in range(len(packet_size_list)):
        throughput = df1.values[row_index][2]
        throughput = eval(throughput)
        throughput = throughput[0][0] * packet_size_list[i] * 8 / 1000000000
        baseline_throughput_list.append(throughput)
        row_index += 1

    interleaved_throughput_list = []
    row_index = 0
    for i in range(len(packet_size_list)):
        throughput = df2.values[row_index][2]
        throughput = eval(throughput)
        throughput = throughput[0][0] * packet_size_list[i] * 8 / 1000000000
        interleaved_throughput_list.append(throughput)
        row_index += 1
    # plot
    matplotlib.rcParams.update({'font.size': 22})
    matplotlib.rcParams.update({'legend.fontsize': 18})
    matplotlib.rcParams.update({'axes.labelsize': 20})
    matplotlib.rcParams.update({'xtick.labelsize': 18})
    matplotlib.rcParams.update({'ytick.labelsize': 18})
    plt.plot(packet_size_list, baseline_throughput_list, label="baseline", color="blue", marker="o")
    plt.plot(packet_size_list, interleaved_throughput_list, label="interleaved", color="red", marker="o")
    plt.legend()
    plt.xlabel("Packet Size (Bytes)")
    plt.ylabel("Throughput (Gbps)")
    plt.tight_layout()
    plt.savefig("amf_packet_size.pdf")
    plt.show()


