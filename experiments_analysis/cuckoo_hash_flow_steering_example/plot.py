import matplotlib

if __name__ == "__main__":

    matplotlib.rcParams.update({'font.size': 20})
    matplotlib.rcParams.update({'legend.fontsize': 16})
    matplotlib.rcParams.update({'axes.labelsize': 18})
    matplotlib.rcParams.update({'xtick.labelsize': 18})
    matplotlib.rcParams.update({'ytick.labelsize': 18})


    proportion = [10*i for i in range(1, 30)]
    proportion_to_percent = [p/300 for p in proportion]

    # read cuckoo_hash_flow_steering_example
    import pandas as pd
    df = pd.read_csv("cuckoo_hash_flow_steering_example.csv")

    # first row is the baseline, proportion is 200
    # second to the last row are the results with flow steering, proportion is 10, 20, ..., 290

    # get the baseline
    baseline = df.iloc[0]
    # get the results with flow steering with proportion 200
    result = df.iloc[1:]
    # get the row with proportion 200
    index_200 = proportion.index(200)
    result_200 = result.iloc[index_200]
    baseline_throughput = eval(baseline["0_throughput"])[0]
    core_0_throughput = baseline_throughput[0] / 10**6
    core_1_throughput = baseline_throughput[1] / 10**6
    result_200_throughput = eval(result_200["0_throughput"])[0]
    core_0_throughput_200 = result_200_throughput[0] / 10**6
    core_1_throughput_200 = result_200_throughput[1] / 10**6
    # bar chart
    import matplotlib.pyplot as plt
    import numpy as np
    width = 0.3
    x = np.arange(3)
    # three
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width /2, [core_0_throughput, core_1_throughput, core_0_throughput + core_1_throughput], width, label='w/o flow steering', color='black', hatch='....')
    rects2 = ax.bar(x + width/2, [core_0_throughput_200, core_1_throughput_200, core_0_throughput_200 + core_1_throughput_200], width, label='flow steering', color='blue', hatch='\\\\\\\\')
    ax.set_ylabel('Throughput (Mpps)')
    ax.set_xticks(x)
    ax.set_xlabel('Improvement')
    ax.set_xticklabels(['core 0', 'core 1', 'total'])
    ax.legend()
    fig.tight_layout()
    plt.savefig("cuckoo_hash_flow_steering_example_throughput.pdf")
    plt.show()


    # line plot, relationship between proportion and core 0 throughput,
    # core 1 throughput, and total throughput
    core_0_throughput = []
    core_1_throughput = []
    total_throughput = []
    for i in range(len(proportion)):
        index = proportion.index(proportion[i])
        result = df.iloc[index + 1]
        throughput = eval(result["0_throughput"])[0]
        core_0_throughput.append(throughput[0] / 10**6)
        core_1_throughput.append(throughput[1] / 10**6)
        total_throughput.append((throughput[0] + throughput[1]) / 10**6)
    import matplotlib.pyplot as plt
    import numpy as np
    fig, ax = plt.subplots()
    ax.plot(proportion_to_percent, total_throughput, label='total', color='red', marker='o')
    ax.plot(proportion_to_percent, core_0_throughput, label='core 0', color='black', marker='o')
    ax.plot(proportion_to_percent, core_1_throughput, label='core 1', color='blue', marker='o')

    ax.set_xlabel('Proportion (%)')
    ax.set_ylabel('Throughput (Mpps)')
    # show legent in one line
    # ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
    ax.legend()
    fig.tight_layout()
    plt.savefig("cuckoo_hash_flow_steering_example_throughput_line.pdf")
    plt.show()

