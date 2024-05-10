import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt

# Define the categories
categories = ['packet header', 'per-flow state', 'others']

# Annotate function
def annotate_bars(ax, bars, text_format='{:.2f}', **kwargs):
    """
    Annotates the bars with the height value.
    """
    # for bar in bars:
    #     text = text_format.format(bar.get_height())
    #     ax.annotate(text, xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
    #                 xytext=(0, 5),  # 5 points vertical offset
    #                 textcoords="offset points",
    #                 ha='center', va='bottom',
    #                 **kwargs)
    pass


if __name__ == "__main__":
    matplotlib.rcParams.update({'font.size': 20})
    matplotlib.rcParams.update({'legend.fontsize': 18})
    matplotlib.rcParams.update({'xtick.labelsize': 25})
    matplotlib.rcParams.update({'ytick.labelsize': 18})
    # Data
    labels = [r'$2^{14}$', r'$2^{15}$', r'$2^{16}$', r'$2^{17}$', r'$2^{18}$', r'$2^{19}$', r'$2^{20}$']
    pps = [7927872, 7690700, 6874097, 5844241, 5253108, 4949372, 4813457]
    matching_time_pp = [34.60, 37.31, 44.19, 53.49, 60.66, 67.04, 72.09]
    packet_header_time_pp = [20.74, 20.29, 21.70, 21.47, 21.26, 21.75, 22.13]
    per_flow_state_time_pp = [9.93, 11.24, 14.40, 17.58, 18.46, 17.96, 17.33]
    l1_miss_list = [17.332942675093964, 17.58668898813827, 17.98193670989426, 18.761510543644025, 19.002633185491632,
     19.084687469631454, 19.015689964983483]
    l2_miss_list = [3.9494229526318136, 4.034488879504517, 4.1650373831549805, 4.2316737697617395, 4.262494450029106,
     4.266074931277722, 4.298026634841397]
    llc_miss_list = [0.11687465703561394, 0.17700902068556473, 0.5018198729569892, 0.9321259967932031, 1.2779810305439832,1.4703980569551232, 1.5475808652508443]
    # Plot
    fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(nrows=5, ncols=1, figsize=(14, 16), sharex=True)
    ax1.bar(labels, [i/1000000 for i in pps], hatch='/', label='Throughput', alpha = 0.99)  # '/' pattern
    annotate_bars(ax1, ax1.containers[0], text_format='{:.2f}')
    ax1.set_ylabel('Throughput (mpps)', size=18)
    ax1.set_ylim([4, 9])
    ax2.bar(labels, matching_time_pp, hatch='/', label='Flow Matching', alpha = 0.99)  # '*' pattern
    ax2.bar(labels, per_flow_state_time_pp, hatch='\\',
           bottom= matching_time_pp, label='Per-flow State Access', alpha = 0.99)  # 'o' pattern
    # annotate_bars(ax2, ax2.containers[0], text_format='{:.2f}')
    # annotate_bars(ax2, ax2.containers[1], text_format='{:.2f}')
    ax2.legend(title='State Access Time Components')
    ax2.set_ylabel('Time (ns)', size=18)
    ax2.set_ylim([25, 100])
    ax3.bar(labels, l1_miss_list, hatch='/', label='L1 Miss', alpha = 0.99)  # '*' pattern
    annotate_bars(ax3, ax3.containers[0], text_format='{:.2f}')
    ax3.set_ylabel('L1C Misses/Packet', size=18)
    # y from 16 to 20
    ax3.set_ylim([17, 19.5])
    ax4.bar(labels, l2_miss_list, hatch='/', label='L2 Miss', alpha = 0.99)  # '\\' pattern
    annotate_bars(ax4, ax4.containers[0], text_format='{:.2f}')
    # y from 3 to 5
    ax4.set_ylim([3.75, 4.5])
    ax4.set_ylabel('L2C Misses/Packet', size=18)
    ax5.bar(labels, llc_miss_list, hatch='/', label='LLC Miss', alpha = 0.99)  # 'o' pattern
    annotate_bars(ax5, ax5.containers[0], text_format='{:.2f}')
    # y from 0 to 2
    ax5.set_ylim([0, 2])
    ax5.set_ylabel('LLC Misses/Packet', size=18)
    # set x label to be number of flows
    ax5.set_xlabel('Number of Flows', size=18)
    # plt.title('Comparison of Time Components')
    # Show plot
    plt.tight_layout()
    # save as bas_nat_time_breakdown.pdf
    # plt.savefig("bess_nat_time_breakdown.pdf")
    plt.show()