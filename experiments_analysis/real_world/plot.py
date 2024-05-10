import matplotlib

if __name__ == "__main__":
    import pandas as pd
    import matplotlib.pyplot as plt
    matplotlib.rcParams.update({'font.size': 20})
    matplotlib.rcParams.update({'legend.fontsize': 20})
    matplotlib.rcParams.update({'axes.labelsize': 20})
    matplotlib.rcParams.update({'xtick.labelsize': 20})
    matplotlib.rcParams.update({'ytick.labelsize': 20})
    # read real_world_rtc.csv as baseline
    baseline_df = pd.read_csv("real_world_rtc.csv")
    baseline_throughput = baseline_df["0_throughput"]
    # to list
    baseline_throughput_list = baseline_throughput.tolist()
    # for each one, evaluate the throughput
    for i in range(len(baseline_throughput_list)):
        baseline_throughput_list[i] = sum(eval(baseline_throughput_list[i])[0]) * 770 * 8 / 1000 / 1000 / 1000
    interleaved_df = pd.read_csv("real_world_interleaved.csv")
    interleaved_throughput = interleaved_df["0_throughput"]
    # to list
    interleaved_throughput_list = interleaved_throughput.tolist()
    # for each one, evaluate the throughput
    for i in range(len(interleaved_throughput_list)):
        interleaved_throughput_list[i] = sum(eval(interleaved_throughput_list[i])[0]) * 770 * 8 / 1000 / 1000 / 1000
    print(baseline_throughput_list)
    print(interleaved_throughput_list)

    # line plot
    # only plot the first 7 values
    # number of core from 1 to 7
    core_list = [1, 2, 3, 4, 5, 6, 7]
    # set the size of the figure
    plt.ylim(0, 110)
    plt.figure(figsize=(10, 5))
    plt.plot(core_list, interleaved_throughput_list[:7], label="interleaved", marker="^", linestyle="-")
    plt.plot(core_list, baseline_throughput_list[:7], label="monolithic", marker="o", linestyle="--")

    plt.xlabel("Number of Cores")
    plt.ylabel("Throughput (Gbps)")
    # size of the legend
    # one row of the paper
    # legent right low corner
    plt.legend(loc="lower right", ncol=1)
    # set size to rectangle
    plt.tight_layout()
    plt.savefig("real_world_rtc_interleaved.pdf")
    plt.show()
