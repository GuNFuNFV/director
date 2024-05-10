from matplotlib.patches import Patch

from matplotlib import pyplot as plt

from experiments_analysis.upf_line_rate_analyis.upf_analysis import get_throughput, get_pps
from runtime_agent import exp_loader

if __name__ == "__main__":
    result = {}
    result["1512"] = {}
    result["1024"] = {}
    result["512"] = {}
    result["CAIDA"] = {}
    result["1512"]['result'] = exp_loader("upf_interleaved", timestamp=1694894585)
    result["1024"]['result'] = exp_loader("upf_interleaved", timestamp=1694911471)
    result["512"]['result'] = exp_loader("upf_interleaved", timestamp=1694907901)
    result["CAIDA"]['result'] = exp_loader("upf_interleaved", timestamp=1694910970)
    result["1512"]["core_list"] = [1, 2, 3, 4]
    result["1024"]["core_list"] = [3, 4, 5, 6]
    result["512"]["core_list"] = [7, 8, 9, 10]
    result["CAIDA"]["core_list"] = [3, 4, 5, 6]
    result["1512"]["packet_size"] = 1512
    result["1024"]["packet_size"] = 1024
    result["512"]["packet_size"] = 512
    result["CAIDA"]["packet_size"] = 900
    result["1512"]["x_label"] = "Packet Size = 1512 bytes"
    result["1024"]["x_label"] = "Packet Size = 1024 bytes"
    result["512"]["x_label"] = "Packet Size = 512 bytes"
    result["CAIDA"]["x_label"] = "CAIDA"
    # create 4 * 4 subplots, total figure size is 20 * 20

    plt.figure(figsize=(8, 6))
    # 4 groups
    subgroups = [4, 5, 6, 7]

    hatch_list = ['/', 'x', '\\', 'o', '.', 'O', '*', '0', '+', '-']
    color_list = ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F', '#EDC948', '#B07AA1', '#FF9DA7', '#9C755F',
                  '#BAB0AC']
    legend_handles = []
    legend_labels = []
    for i in range(len(result)):
        # create the subplot
        subplot_id = i + 1
        ax = plt.subplot(2, 2, subplot_id)
        key = list(result.keys())[i]
        df = result[key]['result']
        throughput_list = get_throughput(get_pps(df), result[key]["packet_size"])

        width = 4
        # create bar chart
        groups = result[key]["core_list"]
        for i in range(len(groups)):
            for j in range(len(subgroups)):
                # location depends on the group and subgroup
                # each group between has a gap of 1 width
                x = i * len(subgroups) * width + j * width + width * (i - 1)
                plt.bar(x, throughput_list[i * len(subgroups) + j], width=width,
                        label="{}".format(2**subgroups[j]), hatch=hatch_list[j], color=color_list[j], alpha=0.99)
        # create x ticks
        locations = [i * len(subgroups) * width + (len(subgroups) - 1) * width / 2 + width * (i - 1) for i in
                     range(len(groups))]
        plt.xticks(locations, groups, fontsize=10)
        # create x label
        x_label = result[key]["x_label"]
        print(x_label)
        ax.set_xlabel(x_label, fontsize=12)

    # collect legend handles and labels
    handles, labels = plt.gca().get_legend_handles_labels()
    legend_handles.extend(handles)
    legend_labels.extend(labels)
    # remove the duplicate legend
    by_label = dict(zip(legend_labels, legend_handles))
    legend_handles = list(by_label.values())
    legend_labels = list(by_label.keys())

    # Create a custom "title" patch
    title_patch = Patch(label='Number of PDRs', color='none')

    # Add the custom "title" patch to the list of handles and labels
    legend_handles = [title_patch] + legend_handles
    legend_labels = ['Number of PDRs'] + legend_labels  # Empty label for the title

    # Add a common legend for all subplots
    plt.figlegend(legend_handles, legend_labels, loc='upper center', ncol=len(legend_labels), fontsize=12)

    # make it shared by all subplots
    plt.ylim(0, 100)
    # Add a common y-label on the left side of the figure
    plt.figtext(0, 0.5, 'Throughput (Gbps)', va='center', rotation='vertical', fontsize=14)

    # Add a common x-label at the bottom of the figure
    plt.figtext(0.5, 0.1, 'Number of Cores', ha='center', fontsize=14)

    # Adjust layout to make room for the legend
    plt.tight_layout(rect=[0.02, 0.1, 1, 0.95])  # Adjust these numbers as needed
    # plt.show(block=False)

    plt.savefig("upf_line_rate.pdf")
