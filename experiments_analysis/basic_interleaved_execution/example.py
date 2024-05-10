if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import numpy as np

    # Data
    labels = ['A', 'B', 'C', 'D']
    values = [4, 1.5, 1.8, 2]

    # Create figure and subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 8))

    # Plot data
    ax1.bar(labels, values, color='blue')
    ax2.bar(labels, values, color='blue')

    # Set y-limits for each subplot to "break" the y-axis
    ax1.set_ylim(3.5, 4.1)  # upper part
    ax2.set_ylim(0, 2.5)  # lower part

    # Hide spines and ticks to make it look broken
    ax1.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax1.tick_params(axis='y', which='both', bottom=False, top=False, labelbottom=False)
    ax2.tick_params(axis='y', which='both', bottom=False, top=False, labelbottom=False)

    # Add broken axis lines
    d = 0.015  # line length
    ax1.plot((-d, +d), (-d, +d), transform=ax1.transAxes, color='black', clip_on=False)
    ax1.plot((1 - d, 1 + d), (-d, +d), transform=ax1.transAxes, color='black', clip_on=False)
    ax2.plot((-d, +d), (1 - d, 1 + d), transform=ax2.transAxes, color='black', clip_on=False)
    ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), transform=ax2.transAxes, color='black', clip_on=False)

    plt.show()