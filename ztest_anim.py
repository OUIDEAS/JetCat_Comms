import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Define the initial data for the plot
x_data = np.arange(10)
y_data = np.random.rand(10)

# Create the figure and axes for the plot
fig, ax = plt.subplots()
line, = ax.plot(x_data, y_data)

# Define the animation function
def update(frame):
    # Update the data for the two new points
    x_new = np.array([10, 11])
    y_new = np.random.rand(2)

    # Update the data for the line plot
    x_data_new = np.concatenate((x_data, x_new))
    y_data_new = np.concatenate((y_data, y_new))

    # Update the data for the line object
    line.set_data(x_data_new, y_data_new)

    # Redraw only the parts of the plot that have changed
    ax.draw_artist(line)

    # Return the line object so that it can be blitted
    return [line]

# Create the animation
ani = FuncAnimation(fig, update, frames=None, blit=True)

# Show the plot
plt.show()