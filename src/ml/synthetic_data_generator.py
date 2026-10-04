import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


class SyntheticDataGenerator:
    """
    Generate synthetic robot-axis data using statistics
    learned from the historical training dataset.
    """

    def __init__(self, axis_columns, random_state=42):

        self.axis_columns = axis_columns

        # Random generator makes results reproducible
        self.random_generator = np.random.default_rng(
            random_state
        )

        # Scaler will be fitted only on training data
        self.scaler = StandardScaler()

        # Store training statistics
        self.training_means = {}
        self.training_stds = {}


    def learn_statistics(self, training_data):
        """
        Learn the mean and standard deviation
        of every robot axis from training data.
        """

        for axis in self.axis_columns:

            self.training_means[axis] = (
                training_data[axis].mean()
            )

            self.training_stds[axis] = (
                training_data[axis].std()
            )

        return {
            "mean": self.training_means,
            "std": self.training_stds
        }


    def fit_scaler(self, training_data):
        """
        Fit StandardScaler using training data only.
        """

        clean_training_data = (
            training_data[self.axis_columns]
            .dropna()
        )

        self.scaler.fit(
            clean_training_data
        )


    def generate(
        self,
        regression_models,
        number_of_rows,
        sampling_interval
    ):
        """
        Generate synthetic testing data using the
        regression trend and training-data variation.
        """

        synthetic_data = pd.DataFrame()

        # Generate elapsed time
        synthetic_data["elapsed_seconds"] = (
            np.arange(number_of_rows)
            * sampling_interval
        )

        X = synthetic_data[
            ["elapsed_seconds"]
        ]

        # Generate synthetic values for each axis
        for axis in self.axis_columns:

            model = regression_models[axis]

            # Expected value from regression model
            predicted_values = model.predict(X)

            # Standard deviation learned from training data
            training_std = self.training_stds[axis]

            # Generate random variation
            noise = self.random_generator.normal(
                loc=0,
                scale=training_std,
                size=number_of_rows
            )

            # Synthetic measurement
            synthetic_data[axis] = (
                predicted_values + noise
            )

        return synthetic_data


    def standardize(self, synthetic_data):
        """
        Standardize synthetic testing data using
        the scaler fitted on training data.
        """

        standardized_data = synthetic_data.copy()

        standardized_values = (
            self.scaler.transform(
                synthetic_data[
                    self.axis_columns
                ]
            )
        )

        standardized_columns = [
            f"{axis}_zscore"
            for axis in self.axis_columns
        ]

        standardized_data[
            standardized_columns
        ] = standardized_values

        return standardized_data


    def inject_anomaly(
        self,
        data,
        regression_models,
        axis,
        start_row,
        duration_rows,
        threshold,
        multiplier=1.5
    ):
        """
        Inject a controlled anomaly above a specified
        residual threshold.

        The abnormal values are created relative to the
        regression prediction so that the residual remains
        above the selected threshold.
        """

        result = data.copy()

        end_row = (
            start_row + duration_rows
        )

        # Select rows where anomaly will be injected
        anomaly_rows = result.loc[
            start_row:end_row - 1
        ]

        X = anomaly_rows[
            ["elapsed_seconds"]
        ]

        # Get expected regression values
        predicted_values = (
            regression_models[axis]
            .predict(X)
        )

        # Create controlled residual above threshold
        controlled_residual = (
            threshold * multiplier
        )

        # Replace normal measurements with
        # controlled abnormal measurements
        result.loc[
            start_row:end_row - 1,
            axis
        ] = (
            predicted_values
            + controlled_residual
        )

        return result