import numpy as np
import matplotlib.pyplot as plt

# Generate some random data
num_xticks = 5
num_measurements = 10
x_tick_labels = ['A', 'B', 'C', 'D', 'E']
data = np.random.normal(10, 2, size=(num_xticks, num_measurements))
means = np.mean(data, axis=1)
stds = np.std(data, axis=1)

# Create the bar plot with error bars
fig, ax = plt.subplots()
ax.bar(x_tick_labels, means, yerr=stds, capsize=5)

# Add labels and title
ax.set_ylabel('Measurement Value')
ax.set_title('Bar plot with error bars')

plt.show()