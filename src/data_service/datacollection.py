import pandas as pd


class StreamingSimulator:

    def __init__(self, file_path):
        # Load the CSV file into a DataFrame
        self.data = pd.read_csv(file_path)

        # Start from the first record
        self.current_index = 0

    def nextDataPoint(self):
        # Check if there are any more records
        if self.current_index < len(self.data):

            # Get one record from the DataFrame (get one data row at a time)
            data_point = self.data.iloc[[self.current_index]]

            # Move to the next record
            self.current_index += 1

            return data_point

        # No more records
        return None