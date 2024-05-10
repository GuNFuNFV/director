import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# Define the categories
categories = ['packet header', 'per-flow state']

if __name__ == "__main__":
    matplotlib.rcParams.update({'font.size': 25})
    matplotlib.rcParams.update({'legend.fontsize': 18})
    matplotlib.rcParams.update({'axes.labelsize': 25})
    matplotlib.rcParams.update({'xtick.labelsize': 25})
    matplotlib.rcParams.update({'ytick.labelsize': 25})

    # Data
    labels = [r'$2^{14}$', r'$2^{15}$', r'$2^{16}$', r'$2^{17}$', r'$2^{18}$', r'$2^{19}$', r'$2^{20}$']
    packet_header_time_pp = [20.20893036720126, 21.387870894381944, 21.504911721837267, 21.51938171982059,
                             21.017512761672076, 21.454297724920256, 21.380556004734782]
    per_flow_state_time_pp = [6.668190132398618, 9.22194668563645, 14.003198330498686, 18.895066875940028,
                              21.556423345304694, 23.47136845119481, 26.06927442682574]

    # Plot
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(labels, packet_header_time_pp, hatch='\\', label='Packet Header', color = 'orange')  # '*' pattern
    ax.bar(labels, per_flow_state_time_pp, hatch='o', bottom=packet_header_time_pp, color = 'green', label='Per Flow State')  # '\\' pattern
    # range of y from 0 to 60
    plt.ylim(0, 60)
    # Labels and title
    plt.xlabel('Number of Flows')
    plt.ylabel('Time (ns)')
    plt.legend(title='Access Time')

    # Show plot
    plt.tight_layout()
    # save as bas_nat_time_breakdown.pdf
    plt.savefig("fastclick_lb_time_breakdown.pdf")
    # plt.show()
