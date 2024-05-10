# read cuckoo_hash_interleaved.csv
import matplotlib
import pandas as pd
if __name__ == "__main__":


    matplotlib.rcParams.update({'font.size': 20})
    matplotlib.rcParams.update({'legend.fontsize': 20})
    matplotlib.rcParams.update({'axes.labelsize': 20})
    matplotlib.rcParams.update({'xtick.labelsize': 20})
    matplotlib.rcParams.update({'ytick.labelsize': 20})


    df1 = pd.read_csv("cuckoo_hash_interleaved.csv")
    df2 = pd.read_csv("cuckoo_hash_rtc.csv")

    number_of_interleaved_threads = [1, 2, 4, 8, 16, 32, 64]
    # get the last row of df2
    df2 = df2.tail(1)
    # get 0_throughput of df2 as a string
    df2 = df2["0_throughput"].values[0]
    # evaluate the string as a python expression
    rtc = eval(df2)

    interleaved_throughput = []
    for i in df1.values:
        temp_list = eval(i[2])[:5]
        interleaved_throughput.append(temp_list)
    # print(interleaved_throughput)

    # calculate the improvement of interleaved method over rtc
    improvement = []
    for i in interleaved_throughput:
        temp_list = []
        for j in range(len(i)):
            temp_list.append( (i[j][0] - rtc[j][0]) / rtc[j][0] * 100)
        improvement.append(temp_list)

    # plot the improvement
    # x axis: number of interleaved threads
    # y axis: improvement, each item represents 5 measurements
    # use boxplot to show the improvement
    # remove outliers
    import matplotlib.pyplot as plt
    plt.boxplot(improvement, showfliers=False)
    plt.xticks(range(1, len(number_of_interleaved_threads) + 1), number_of_interleaved_threads)
    plt.xlabel("number of interleaved threads")
    plt.ylabel("improvement over rtc (%)")
    # plt.title("effectiveness of interleaved methods")
    plt.tight_layout()
    plt.savefig("interleaved_improvement.pdf")
    plt.show()


    # flatten rtc and interleaved_throughput
    rtc = [i[0] for i in rtc]
    interleaved_throughput = [[j[0] for j in i] for i in interleaved_throughput]
    # print(rtc)
    # print(interleaved_throughput)
    l1_misses_rtc= df1["L1-dcache-load-misses"].values[-1]
    # evaluate the string as a python expression
    l1_misses_rtc = eval(l1_misses_rtc)
    l1_misses_per_packet = [l1_misses_rtc[i] / rtc[i] for i in range(len(rtc))]
    print(l1_misses_per_packet)

    df2 = pd.read_csv("cuckoo_hash_rtc.csv")
    l1_misses_interleaved_col = df2["L1-dcache-load-misses"].values
    l1_misses_interleaved_per_packet = []
    for i in range(len(l1_misses_interleaved_col)):
        temp_l1_misses_interleaved = eval(l1_misses_interleaved_col[i])
        # print(temp_l1_misses_interleaved)
        throughput_interleaved = interleaved_throughput[i]
        temp_l1_misses_interleaved_per_packet = [temp_l1_misses_interleaved[j] / throughput_interleaved[j] for j in range(len(throughput_interleaved))]
        l1_misses_interleaved_per_packet.append(temp_l1_misses_interleaved_per_packet)


    # plot the improvement
    # x axis: number of interleaved threads
    # y axis: improvement, each item represents 5 measurements
    # first plot the l1 misses per packet of rtc
    # get the average of l1 misses per packet of rtc
    l1_misses_per_packet = sum(l1_misses_per_packet) / len(l1_misses_per_packet)
    # plot a horizontal line
    plt.axhline(y=l1_misses_per_packet, color='r', linestyle='-')
    # plot the l1 misses per packet of interleaved methods
    plt.boxplot(l1_misses_interleaved_per_packet, showfliers=False)
    plt.xticks(range(1, len(number_of_interleaved_threads) + 1), number_of_interleaved_threads)
    # annotation of the baseline
    # an arrow with text that points to the horizontal line
    # at the center of the plot
    plt.annotate("baseline", xy=(4, l1_misses_per_packet), xytext=(3.6, l1_misses_per_packet + 2), arrowprops=dict(facecolor='black', shrink=0.05), size=10)
    plt.xlabel("number of interleaved threads")
    plt.ylabel("l1 misses per packet")
    # plt.title("l1 misses per packet of interleaved methods")
    plt.tight_layout()
    plt.savefig("interleaved_method_l1_misses_per_packet.pdf")
    plt.show()


    llc_misses_rtc= df1["LLC-load-misses"].values[-1]
    # evaluate the string as a python expression
    llc_misses_rtc = eval(llc_misses_rtc)
    llc_misses_per_packet = [llc_misses_rtc[i] / rtc[i] for i in range(len(rtc))]
    print(llc_misses_per_packet)

    df2 = pd.read_csv("cuckoo_hash_rtc.csv")
    llc_misses_interleaved_col = df2["LLC-load-misses"].values
    llc_misses_interleaved_per_packet = []
    for i in range(len(llc_misses_interleaved_col)):
        temp_llc_misses_interleaved = eval(llc_misses_interleaved_col[i])
        # print(temp_l1_misses_interleaved)
        throughput_interleaved = interleaved_throughput[i]
        temp_llc_misses_interleaved_per_packet = [temp_llc_misses_interleaved[j] / throughput_interleaved[j] for j in range(len(throughput_interleaved))]
        llc_misses_interleaved_per_packet.append(temp_llc_misses_interleaved_per_packet)

    # plot the improvement
    # x axis: number of interleaved threads
    # y axis: improvement, each item represents 5 measurements
    # first plot the llc misses per packet of rtc
    # get the average of llc misses per packet of rtc
    llc_misses_per_packet = sum(llc_misses_per_packet) / len(llc_misses_per_packet)
    # plot a horizontal line
    plt.axhline(y=llc_misses_per_packet, color='r', linestyle='-')
    # plot the llc misses per packet of interleaved methods
    plt.boxplot(llc_misses_interleaved_per_packet, showfliers=False)
    plt.xticks(range(1, len(number_of_interleaved_threads) + 1), number_of_interleaved_threads)
    # annotation of the baseline
    # an arrow with text that points to the horizontal line
    # at the center of the plot
    plt.annotate("baseline", xy=(4, llc_misses_per_packet), xytext=(3.6, llc_misses_per_packet - 0.3), arrowprops=dict(facecolor='black', shrink=0.05), size=10)
    plt.xlabel("number of interleaved threads")
    plt.ylabel("llc misses per packet")
    # plt.title("llc misses per packet of interleaved methods")
    plt.tight_layout()

    plt.savefig("interleaved_llc_misses_per_packet.pdf")
    plt.show()

    instructions_rtc= df1["cycles"].values[-1]
    # evaluate the string as a python expression
    intructions_rtc = eval(instructions_rtc)
    cycles_per_packet = [intructions_rtc[i] / rtc[i] for i in range(len(rtc))]
    print(cycles_per_packet)

    df2 = pd.read_csv("cuckoo_hash_rtc.csv")
    instructions_interleaved_col = df2["cycles"].values
    instructions_interleaved_per_packet = []
    for i in range(len(instructions_interleaved_col)):
        temp_instructions_interleaved = eval(instructions_interleaved_col[i])
        # print(temp_l1_misses_interleaved)
        throughput_interleaved = interleaved_throughput[i]
        temp_instructions_interleaved_per_packet = [temp_instructions_interleaved[j] / throughput_interleaved[j] for j in range(len(throughput_interleaved))]
        instructions_interleaved_per_packet.append(temp_instructions_interleaved_per_packet)

    # plot the improvement
    # x axis: number of interleaved threads

    # y axis: improvement, each item represents 5 measurements
    # first plot the instructions per packet of rtc
    # get the average of instructions per packet of rtc
    cycles_per_packet = sum(cycles_per_packet) / len(cycles_per_packet)
    # plot a horizontal line
    plt.axhline(y=cycles_per_packet, color='r', linestyle='-')
    # plot the instructions per packet of interleaved methods
    plt.boxplot(instructions_interleaved_per_packet, showfliers=False)
    plt.xticks(range(1, len(number_of_interleaved_threads) + 1), number_of_interleaved_threads)
    # annotation of the baseline
    # an arrow with text that points to the horizontal line
    # at the center of the plot
    plt.annotate("baseline", xy=(4, cycles_per_packet), xytext=(3.6, cycles_per_packet - 80), arrowprops=dict(facecolor='black', shrink=0.05), size=10)
    plt.xlabel("number of interleaved threads")
    plt.ylabel("cycles per packet")
    # plt.title("instructions per packet of interleaved methods")
    plt.tight_layout()

    plt.savefig("interleaved_cycles_per_packet.pdf")
    plt.show()







