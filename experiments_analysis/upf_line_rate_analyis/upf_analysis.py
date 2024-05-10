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


if __name__ == "__main__":
    df = exp_loader("upf_interleaved", timestamp=1694894585)
    print(get_throughput(get_pps(df), 1512))
    # 6 groups numbes
    groups = [1, 2, 3, 4]
    subgroups = [4, 5, 6, 7]
    # transform to 2**n
    subgroups = [2 ** i for i in subgroups]
    throughput_list = get_throughput(get_pps(df), 1518)

    # create bar chart
    # 6 groups
    # 4 subgroups
    # 4 bars per group
    # 2.5 bar width

    hatch_list = ['/', 'x', '\\', 'o', '.', 'O', '*', '0', '+', '-']
    color_list = ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F', '#EDC948', '#B07AA1', '#FF9DA7', '#9C755F',
                  '#BAB0AC']

    plt.figure(figsize=(7, 5))

    width = 4
    for i in range(len(groups)):
        for j in range(len(subgroups)):
            # location depends on the group and subgroup
            # each group between has a gap of 1 width
            x = i * len(subgroups) * width + j * width + width * (i - 1)
            plt.bar(x, throughput_list[i * len(subgroups) + j], width=width,
                    hatch=hatch_list[j], color=color_list[j], label="{}".format(subgroups[j]))
    # only tick at the center of each group
    locations = [i * len(subgroups) * width + (len(subgroups) - 1) * width / 2 + width * (i - 1) for i in
                 range(len(groups))]
    plt.xticks(locations, groups, fontsize=20)
    plt.yticks(fontsize=20)
    # legend is for each subgroup
    # remove the duplicate legend
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), fontsize=20)
    plt.ylabel("Throughput (Gbps)", fontsize=20)
    plt.ylim(0, 100)
    # plt.legend()
    plt.tight_layout()

    plt.show()

    df = exp_loader("upf_interleaved", timestamp=1694911471)
    # print(get_throughput(get_pps(df), 1024))
    # 6 groups numbes
    groups = [3, 4, 5, 6]
    subgroups = [4, 5, 6, 7]
    # transform to 2**n
    subgroups = [2 ** i for i in subgroups]
    throughput_list = get_throughput(get_pps(df), 1024)

    # create bar chart
    # 6 groups
    # 4 subgroups
    # 4 bars per group
    # 2.5 bar width

    hatch_list = ['/', 'x', '\\', 'o', '.', 'O', '*', '0', '+', '-']
    color_list = ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F', '#EDC948', '#B07AA1', '#FF9DA7', '#9C755F',
                  '#BAB0AC']

    plt.figure(figsize=(7, 5))

    width = 4
    for i in range(len(groups)):
        for j in range(len(subgroups)):
            # location depends on the group and subgroup
            # each group between has a gap of 1 width
            x = i * len(subgroups) * width + j * width + width * (i - 1)
            throughput_list_id = (i) * len(subgroups) + j
            plt.bar(x, throughput_list[throughput_list_id], width=width,
                    hatch=hatch_list[j], color=color_list[j], label="{}".format(subgroups[j]), alpha=0.99)
    # only tick at the center of each group
    locations = [i * len(subgroups) * width + (len(subgroups) - 1) * width / 2 + width * (i - 1) for i in
                 range(len(groups))]
    plt.xticks(locations, groups, fontsize=20)
    plt.yticks(fontsize=20)
    # y limit from 40 to 100
    plt.ylim(0, 100)
    # legend is for each subgroup
    # remove the duplicate legend
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), fontsize=20)
    plt.ylabel("Throughput (Gbps)", fontsize=20)
    # plt.legend()
    plt.tight_layout()
    plt.show()

    df = exp_loader("upf_interleaved", timestamp=1694907901)
    # print(get_throughput(get_pps(df), 1024))
    # 6 groups numbes
    groups = [7, 8, 9, 10]
    subgroups = [4, 5, 6, 7]
    # transform to 2**n
    subgroups = [2 ** i for i in subgroups]
    throughput_list = get_throughput(get_pps(df), 512)

    # create bar chart
    # 6 groups
    # 4 subgroups
    # 4 bars per group
    # 2.5 bar width

    hatch_list = ['/', 'x', '\\', 'o', '.', 'O', '*', '0', '+', '-']
    color_list = ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F', '#EDC948', '#B07AA1', '#FF9DA7', '#9C755F',
                  '#BAB0AC']

    plt.figure(figsize=(7, 5))

    width = 4
    for i in range(len(groups)):
        for j in range(len(subgroups)):
            # location depends on the group and subgroup
            # each group between has a gap of 1 width
            x = i * len(subgroups) * width + j * width + width * (i - 1)
            throughput_list_id = (i) * len(subgroups) + j
            plt.bar(x, throughput_list[throughput_list_id], width=width,
                    hatch=hatch_list[j], color=color_list[j], label="{}".format(subgroups[j]))
    # only tick at the center of each group
    locations = [i * len(subgroups) * width + (len(subgroups) - 1) * width / 2 + width * (i - 1) for i in
                 range(len(groups))]
    plt.xticks(locations, groups, fontsize=20)
    plt.yticks(fontsize=20)
    # y limit from 40 to 100
    plt.ylim(0, 100)
    # legend is for each subgroup
    # remove the duplicate legend
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), fontsize=20)
    plt.ylabel("Throughput (Gbps)", fontsize=20)
    # plt.legend()
    plt.tight_layout()
    plt.show()

    df = exp_loader("upf_interleaved", timestamp = 1694910970)
    # print(get_throughput(get_pps(df), 1024))
    # 6 groups numbes
    groups = [3, 4, 5, 6]
    subgroups = [4, 5, 6, 7]
    # transform to 2**n
    subgroups = [2 ** i for i in subgroups]
    throughput_list = get_throughput(get_pps(df), 900)

    # create bar chart
    # 6 groups
    # 4 subgroups
    # 4 bars per group
    # 2.5 bar width

    hatch_list = ['/', 'x', '\\', 'o', '.', 'O', '*', '0', '+', '-']
    color_list = ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F', '#EDC948', '#B07AA1', '#FF9DA7', '#9C755F',
                  '#BAB0AC']

    plt.figure(figsize=(7, 5))

    width = 4
    for i in range(len(groups)):
        for j in range(len(subgroups)):
            # location depends on the group and subgroup
            # each group between has a gap of 1 width
            x = i * len(subgroups) * width + j * width + width * (i - 1)
            throughput_list_id = (i) * len(subgroups) + j
            plt.bar(x, throughput_list[throughput_list_id], width=width,
                    hatch=hatch_list[j], color=color_list[j], label="{}".format(subgroups[j]))
    # only tick at the center of each group
    locations = [i * len(subgroups) * width + (len(subgroups) - 1) * width / 2 + width * (i - 1) for i in
                 range(len(groups))]
    plt.xticks(locations, groups, fontsize=20)
    plt.yticks(fontsize=20)
    # y limit from 40 to 100
    plt.ylim(0, 100)
    # legend is for each subgroup
    # remove the duplicate legend
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), fontsize=20)
    plt.ylabel("Throughput (Gbps)", fontsize=20)
    # create shared legend
    # remove the duplicate legend
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    # at the top
    plt.legend(by_label.values(), by_label.keys(), fontsize=20)

    plt.tight_layout()
    plt.show()
