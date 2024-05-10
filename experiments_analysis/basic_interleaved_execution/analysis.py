import matplotlib
from matplotlib import pyplot as plt

from runtime_agent import exp_loader


def get_pps(df):
    throughput = df["0_throughput"]
    result = []
    for item in throughput:
        evaled = eval(item)[0]
        # sump it up
        evaled = sum(evaled)
        result.append(evaled)
    return result


def get_throughput(pps_list, packet_size):
    return [pps * packet_size * 8 / 1000000000 for pps in pps_list]



def get_l1_miss(df):
    data = df["l1d.replacement"]
    result = []
    for item in data:
        result.append(eval(item)[0])
    return result


def get_l2_miss(df):
    # data = df["l2_rqsts.all_demand_miss"]
    data = df["MEM_LOAD_RETIRED.L2_MISS"]
    result = []
    for item in data:
        result.append(eval(item)[0])
    return result


def get_l3_miss(df):
    data = df["LLC-load-misses"]
    result = []
    for item in data:
        result.append(eval(item)[0])

    data_2 = df["LLC-store-misses"]
    for item in range(len(data_2)):
        result[item] += eval(data_2[item])[0]
    return result

def get_ipc(df):
    data1 = df["instructions"]
    data2 = df["cycles"]
    result = []
    for i in range(len(data1)):
        instructions = eval(data1[i])[0]
        cycles = eval(data2[i])[0]
        result.append(instructions / cycles)
    return result



if __name__ == "__main__":

    matplotlib.rcParams.update({'font.size': 20})
    matplotlib.rcParams.update({'legend.fontsize': 20})
    matplotlib.rcParams.update({'axes.labelsize': 20})
    matplotlib.rcParams.update({'xtick.labelsize': 20})
    matplotlib.rcParams.update({'ytick.labelsize': 20})

    basic_interleaved = exp_loader("sfc_simulation")
    rtc = exp_loader("bess_nat", timestamp=1694992600)
    throughput_list_basic_interleaved = get_throughput(get_pps(basic_interleaved), 64)
    throughput_list_monolithic = get_throughput(get_pps(rtc), 64)
    pps_list_basic_interleaved = get_pps(basic_interleaved)
    pps_list_monolithic = get_pps(rtc)

    l1_miss_list_rtc = get_l1_miss(rtc)
    l1_miss_list_interleaved = get_l1_miss(basic_interleaved)
    l2_miss_list_rtc = get_l2_miss(rtc)
    l2_miss_list_interleaved = get_l2_miss(basic_interleaved)
    l3_miss_list_rtc = get_l3_miss(rtc)
    l3_miss_list_interleaved = get_l3_miss(basic_interleaved)

    l1_miss_list_rtc_per_packet = [l1_miss_list_rtc[i] / pps_list_monolithic[i] for i in range(len(l1_miss_list_rtc))]
    l1_miss_list_interleaved_per_packet = [l1_miss_list_interleaved[i] / pps_list_basic_interleaved[i] for i in range(len(l1_miss_list_interleaved))]
    l2_miss_list_rtc_per_packet = [l2_miss_list_rtc[i] / pps_list_monolithic[i] for i in range(len(l2_miss_list_rtc))]
    l2_miss_list_interleaved_per_packet = [l2_miss_list_interleaved[i] / pps_list_basic_interleaved[i] for i in range(len(l2_miss_list_interleaved))]
    l3_miss_list_rtc_per_packet = [l3_miss_list_rtc[i] / pps_list_monolithic[i] for i in range(len(l3_miss_list_rtc))]
    l3_miss_list_interleaved_per_packet = [l3_miss_list_interleaved[i] / pps_list_basic_interleaved[i] for i in range(len(l3_miss_list_interleaved))]

    ipc1 = get_ipc(rtc)
    ipc2 = get_ipc(basic_interleaved)
    print(l1_miss_list_rtc_per_packet)
    print(l1_miss_list_interleaved_per_packet)
    print(l2_miss_list_rtc_per_packet)
    print(l2_miss_list_interleaved_per_packet)
    print(l3_miss_list_rtc_per_packet)
    print(l3_miss_list_interleaved_per_packet)
    print(ipc1)
    print(ipc2)

    exp_data = {
        "baseline": {
            "throughput": throughput_list_monolithic,
            "l1_miss": l1_miss_list_rtc_per_packet,
            "l2_miss": l2_miss_list_rtc_per_packet,
            "l3_miss": l3_miss_list_rtc_per_packet,
            "x_ticks": ["BESS"],
            "ipc": ipc1,
        },
        "interleaved": {
            "throughput": throughput_list_basic_interleaved,
            "l1_miss": l1_miss_list_interleaved_per_packet,
            "l2_miss": l2_miss_list_interleaved_per_packet,
            "l3_miss": l3_miss_list_interleaved_per_packet,
            "x_ticks": ["1", "2", "4", "8", "16", "32", "64"],
            "ipc": ipc2,
        }
    }
    # create bar chart
    # first base line which is rtc
    # then interleaved

    hatch_list = ['/', 'x', '\\', 'o', '.', 'O', '*', '0', '+', '-']
    color_list = ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F', '#EDC948', '#B07AA1', '#FF9DA7', '#9C755F',
                  '#BAB0AC']

    plt.figure()

    width = 1.5
    # first baseline
    for i in range(len(exp_data["baseline"]["throughput"])):
        x = i * width
        plt.bar(x, exp_data["baseline"]["throughput"][i], width=width,
                hatch=hatch_list[i], color=color_list[i], label="{}".format(exp_data["baseline"]["x_ticks"][i]), alpha=0.99)
    # then interleaved
    for i in range(len(exp_data["interleaved"]["throughput"])):
        x = (i + 1) * width
        plt.bar(x, exp_data["interleaved"]["throughput"][i], width=width,
                hatch=hatch_list[i + 1], color=color_list[i + 1], label="{}".format(exp_data["interleaved"]["x_ticks"][i]), alpha=0.99)
    # only tick for interleaved
    locations = [(i + 1) * width for i in range(len(exp_data["interleaved"]["throughput"]))]
    # for the first baseline, tick is baseline
    locations = [0] + locations
    plt.xticks(locations, ["RTC\n(BESS)"] + exp_data["interleaved"]["x_ticks"], fontsize=20)
    plt.yticks(fontsize=20)
    plt.ylabel("Throughput (mpps)", fontsize=20)
    plt.xlabel("Number of NFTasks", fontsize=20)
    plt.ylim(1.5, 3)
    plt.tight_layout()
    # show legend
    plt.savefig("basic_throughput.pdf")
    plt.show()


    # plot for l1 miss per packet

    plt.figure()

    width = 1.5
    # first baseline
    for i in range(len(exp_data["baseline"]["l1_miss"])):
        x = i * width
        plt.bar(x, exp_data["baseline"]["l1_miss"][i], width=width,
                hatch=hatch_list[i], color=color_list[i], label="{}".format(exp_data["baseline"]["x_ticks"][i]), alpha=0.99)

    # then interleaved
    for i in range(len(exp_data["interleaved"]["l1_miss"])):
        x = (i + 1) * width
        plt.bar(x, exp_data["interleaved"]["l1_miss"][i], width=width,
                hatch=hatch_list[i + 1], color=color_list[i + 1], label="{}".format(exp_data["interleaved"]["x_ticks"][i]), alpha=0.99)

    # only tick for interleaved
    locations = [(i + 1) * width for i in range(len(exp_data["interleaved"]["l1_miss"]))]
    # for the first baseline, tick is baseline
    locations = [0] + locations
    plt.xticks(locations, ["RTC\n(BESS)"] + exp_data["interleaved"]["x_ticks"], fontsize=20)
    plt.yticks(fontsize=20)
    plt.ylabel("L1 Misses per Packet", fontsize=20)
    plt.xlabel("Number of NFTasks", fontsize=20)
    plt.ylim(15, 22)

    plt.tight_layout()
    # show legend
    plt.savefig("basic_l1_miss.pdf")
    plt.show()

    # plot for l2 miss per packet

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    width = 1.5
    # first baseline
    for i in range(len(exp_data["baseline"]["l2_miss"])):
        x = i * width
        ax1.bar(x, exp_data["baseline"]["l2_miss"][i], width=width,
                hatch=hatch_list[i], color=color_list[i], label="{}".format(exp_data["baseline"]["x_ticks"][i]), alpha=0.99)
        ax2.bar(x, exp_data["baseline"]["l2_miss"][i], width=width,
                hatch=hatch_list[i], color=color_list[i], label="{}".format(exp_data["baseline"]["x_ticks"][i]), alpha=0.99)

    # then interleaved
    for i in range(len(exp_data["interleaved"]["l2_miss"])):
        x = (i + 1) * width
        ax2.bar(x, exp_data["interleaved"]["l2_miss"][i], width=width,
                hatch=hatch_list[i + 1], color=color_list[i + 1], label="{}".format(exp_data["interleaved"]["x_ticks"][i]), alpha=0.99)


    # Set y-limits for each subplot to "break" the y-axis
    ax1.set_ylim(3.5, 4.5)  # upper part
    ax2.set_ylim(1.4, 1.8)  # lower part
    # Hide spines and ticks to make it look broken
    ax1.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax1.tick_params(axis='y', which='both', bottom=False, top=False, labelbottom=False)
    ax2.tick_params(axis='y', which='both', bottom=False, top=False, labelbottom=False)

    # Add broken axis lines
    d = 0.01  # line length
    ax1.plot((-d, +d), (-d, +d), transform=ax1.transAxes, color='black', clip_on=False)
    ax1.plot((1 - d, 1 + d), (-d, +d), transform=ax1.transAxes, color='black', clip_on=False)
    ax2.plot((-d, +d), (1 - d, 1 + d), transform=ax2.transAxes, color='black', clip_on=False)
    ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), transform=ax2.transAxes, color='black', clip_on=False)

    # only tick for interleaved
    locations = [(i + 1) * width for i in range(len(exp_data["interleaved"]["l2_miss"]))]
    # for the first baseline, tick is baseline
    locations = [0] + locations
    plt.xticks(locations, ["RTC\n(BESS)"] + exp_data["interleaved"]["x_ticks"], fontsize=20)
    plt.yticks(fontsize=20)
    ax1.set_ylabel("L2 Misses per Packet", fontsize=20)
    ax1.yaxis.set_label_coords(-0.15, -0.19)
    plt.xlabel("Number of NFTasks", fontsize=20)
    plt.tight_layout()

    # show legend
    plt.savefig("basic_l2_miss.pdf")
    plt.show()

    # plot for l3 miss per packet

    plt.figure()

    width = 1.5
    # first baseline
    for i in range(len(exp_data["baseline"]["l3_miss"])):
        x = i * width
        plt.bar(x, exp_data["baseline"]["l3_miss"][i], width=width,
                hatch=hatch_list[i], color=color_list[i], label="{}".format(exp_data["baseline"]["x_ticks"][i]), alpha=0.99)

    # then interleaved
    for i in range(len(exp_data["interleaved"]["l3_miss"])):
        x = (i + 1) * width
        plt.bar(x, exp_data["interleaved"]["l3_miss"][i], width=width,
                hatch=hatch_list[i + 1], color=color_list[i + 1], label="{}".format(exp_data["interleaved"]["x_ticks"][i]), alpha=0.99)

    # only tick for interleaved
    locations = [(i + 1) * width for i in range(len(exp_data["interleaved"]["l3_miss"]))]
    # for the first baseline, tick is baseline
    locations = [0] + locations
    plt.xticks(locations, ["RTC\n(BESS)"] + exp_data["interleaved"]["x_ticks"], fontsize=20)
    plt.yticks(fontsize=20)
    plt.ylabel("LLC Misses per Packet", fontsize=20)
    plt.xlabel("Number of NFTasks", fontsize=20)
    plt.ylim(1.5, 2.1)
    plt.tight_layout()
    # show legend
    plt.savefig("basic_llc_miss.pdf")
    plt.show()


 # plot for ipc per packet

    plt.figure()

    i = 0
    width = 1.5
    # first baseline
    for i in range(len(exp_data["baseline"]["ipc"])):
        x = i * width
        plt.bar(x, exp_data["baseline"]["ipc"][i], width=width,
                hatch=hatch_list[i], color=color_list[i], label="{}".format(exp_data["baseline"]["x_ticks"][i]), alpha=0.99)

    # then interleaved
    for i in range(len(exp_data["interleaved"]["ipc"])):
        x = (i + 1) * width
        plt.bar(x, exp_data["interleaved"]["ipc"][i], width=width,
                hatch=hatch_list[i + 1], color=color_list[i + 1], label="{}".format(exp_data["interleaved"]["x_ticks"][i]), alpha=0.99)

    # only tick for interleaved
    locations = [(i + 1) * width for i in range(len(exp_data["interleaved"]["ipc"]))]
    # for the first baseline, tick is baseline
    locations = [0] + locations
    plt.xticks(locations, ["RTC\n(BESS)"] + exp_data["interleaved"]["x_ticks"], fontsize=20)
    plt.yticks(fontsize=20)
    plt.ylabel("IPC", fontsize=20)
    plt.xlabel("Number of NFTasks", fontsize=20)
    plt.ylim(0.6, 0.9)
    plt.tight_layout()
    # show legend
    plt.savefig("basic_ipc.pdf")
    plt.show()