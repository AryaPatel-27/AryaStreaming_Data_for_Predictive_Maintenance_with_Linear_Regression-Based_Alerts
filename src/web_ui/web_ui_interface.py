import matplotlib.pyplot as plt
from IPython.display import display, clear_output


class RobotDashboard:

    def __init__(self):
        # Store streaming data
        self.times = []
        self.axis1_values = []

        # Create the chart
        self.fig, self.ax = plt.subplots()

    def updateDashboard(self, data_point):

        # Get values from the new record
        time_value = data_point["Time"].iloc[0]
        axis1_value = data_point["Axis #1"].iloc[0]

        # Add the new values
        self.times.append(time_value)
        self.axis1_values.append(axis1_value)

        # Clear the previous chart
        self.ax.clear()

        # Plot the data
        self.ax.plot(
            self.times,
            self.axis1_values,
            marker="o"
        )

        # Add labels
        self.ax.set_title("Robot Axis #1 Streaming Data")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Axis #1")

        # Rotate time labels
        self.ax.tick_params(axis="x", rotation=45)

        # Update the chart
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.01)

        # Show only the latest version of the chart
        clear_output(wait=True)
        display(self.fig)