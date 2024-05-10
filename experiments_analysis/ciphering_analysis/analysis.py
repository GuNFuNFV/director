from experiments_analysis.exp_analysis_utility import get_pps, get_l1_miss, get_l2_miss, get_l3_miss, get_throughput
from runtime_agent import exp_loader

if __name__ == '__main__':
    result = exp_loader("ciphering_simulation", timestamp=1695658950)
    pps = get_pps(result)
    throughput_list = get_throughput(pps, 1024)
    l1_miss = get_l1_miss(result)
    l2_miss = get_l2_miss(result)

    l3_miss = get_l3_miss(result)
    l1_miss_per_packet = [l1_miss[i] / pps[i] for i in range(len(pps))]

    print(throughput_list)
    print(pps)
    print(l1_miss_per_packet)

    l2_miss_per_packet = [l2_miss[i] / pps[i] for i in range(len(pps))]
    print(l2_miss_per_packet)

    l3_miss_per_packet = [l3_miss[i] / pps[i] for i in range(len(pps))]
    print(l3_miss_per_packet)

    import matplotlib.pyplot as plt
    import numpy as np


    hatch_list = ['/', 'x', '\\', 'o', '.', 'O', '*', '0', '+', '-']
    color_list = ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F', '#EDC948', '#B07AA1', '#FF9DA7', '#9C755F',
                  '#BAB0AC']
    plt.rcParams.update({'font.size': 40})
    plt.rcParams.update({'legend.fontsize': 40})
    plt.rcParams.update({'axes.labelsize': 40})
    plt.rcParams.update({'xtick.labelsize': 40})
    plt.rcParams.update({'ytick.labelsize': 40})
    plt.figure(figsize=(8, 8))

    plt.ylabel("Throughput (Gbps)")
    # in the throuhgput list, the first one is offloaded
    # the second one is baseline

    plt.bar([1], [throughput_list[0]], color=color_list[0], hatch=hatch_list[0], label="offloaded", alpha=0.99)
    plt.bar([2], [throughput_list[1]], color=color_list[1], hatch=hatch_list[1], label="baseline", alpha=0.99)
    # font size 25
    plt.xticks([1, 2], ["Offloaded", "Baseline"], fontsize=40)
    # show plt
    plt.tight_layout()
    plt.savefig("ciphering_throughput.pdf")


    # plot the llc comparison
    plt.figure(figsize=(8, 8))
    plt.ylabel("LLC Misses Per Packet")
    plt.bar([1], [l3_miss_per_packet[0]], color=color_list[0], hatch=hatch_list[0], label="offloaded", alpha=0.99)
    plt.bar([2], [l3_miss_per_packet[1]], color=color_list[1], hatch=hatch_list[1], label="baseline", alpha=0.99)
    plt.xticks([1, 2], ["Offloaded", "Baseline"], fontsize=40)
    # y limit from 0.8 to 1.3
    plt.ylim(0.8, 1.3)
    plt.tight_layout()
    plt.savefig("ciphering_llc.pdf")

