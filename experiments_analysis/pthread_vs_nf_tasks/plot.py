import matplotlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

if __name__ == "__main__":
    matplotlib.rcParams.update({'font.size': 20})
    matplotlib.rcParams.update({'legend.fontsize': 20})
    matplotlib.rcParams.update({'axes.labelsize': 20})
    matplotlib.rcParams.update({'xtick.labelsize': 20})
    matplotlib.rcParams.update({'ytick.labelsize': 20})
    # Read the data
    # Replace '/path/to/your/data.txt' with the actual path to your data file
    df_new = pd.read_csv('data.txt', delim_whitespace=True, header=None, names=['Concurrency', 'Pthread', 'NFTask', 'SpeedUp'])
    hatch_list = ['/', 'x', '\\', 'o', '.', 'O', '*', '0', '+', '-']
    color_list = ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F', '#EDC948', '#B07AA1', '#FF9DA7', '#9C755F',
                  '#BAB0AC']

    # Filter the DataFrame to only include rows with the specified concurrency levels
    selected_concurrencies = [2, 4, 8, 16, 32]
    df_filtered = df_new[df_new['Concurrency'].isin(selected_concurrencies)]

    # Create a new figure and set its size
    plt.figure(figsize=(8, 7))

    # Create the first subplot for the bar chart (context switching)
    ax1 = plt.subplot(1, 1, 1)

    # Plot bars for Pthread and NFTask
    bar_width = 0.4
    index = np.arange(len(df_filtered['Concurrency']))

    bar1 = ax1.bar(index - bar_width / 2, df_filtered['Pthread'], bar_width, label='Pthread', color = color_list[0], hatch = hatch_list[0], alpha=0.99)
    bar2 = ax1.bar(index + bar_width / 2, df_filtered['NFTask'], bar_width, label='NFTask', color = color_list[1], hatch = hatch_list[1], alpha=0.99)

    # Add labels, title, and legend
    ax1.set_xlabel('Concurrency')
    ax1.set_ylabel('# of Context Switching')
    # ax1.set_title('Context Switching and Speed-Up vs Selected Concurrency Levels')
    ax1.legend(loc='upper left')

    # Use log scale for y-axis if needed
    ax1.set_yscale('log')

    # Create the second subplot for the line plot (speed-up)
    ax2 = ax1.twinx()

    # Plot the line plot for speed-up
    line1, = ax2.plot(index, df_filtered['SpeedUp'], marker='o', linestyle='-', color='g', label='Speed-Up')

    # Add labels, title, and legend
    ax2.set_ylabel('Speed-Up')
    ax2.legend(loc='upper left', bbox_to_anchor=(0.0, 0.8))

    # Set the x-axis labels based on the selected concurrency levels
    ax1.set_xticks(index)
    ax1.set_xticklabels(df_filtered['Concurrency'])

    # Show grid
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Show the plot
    plt.tight_layout()
    # plt.show()
    plt.savefig("pthread_vs_nf_tasks.pdf")