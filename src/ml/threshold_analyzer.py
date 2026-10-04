import pandas as pd


class ThresholdAnalyzer:

    def __init__(
        self,
        axis_columns,
        alert_percentile=0.95,
        error_percentile=0.99
    ):
        self.axis_columns = axis_columns
        self.alert_percentile = alert_percentile
        self.error_percentile = error_percentile


    def calculate_residual_summary(self, data):

        summary = []

        for axis in self.axis_columns:

            residuals = data[
                f"{axis}_residual"
            ].dropna()

            summary.append({
                "axis": axis,
                "mean": residuals.mean(),
                "std": residuals.std(),
                "95th_percentile":
                    residuals.quantile(0.95),
                "99th_percentile":
                    residuals.quantile(0.99),
                "max": residuals.max()
            })

        return pd.DataFrame(summary)


    def calculate_thresholds(self, data):

        thresholds = {}

        for axis in self.axis_columns:

            residuals = data[
                f"{axis}_residual"
            ].dropna()

            thresholds[axis] = {
                "MinC": residuals.quantile(
                    self.alert_percentile
                ),
                "MaxC": residuals.quantile(
                    self.error_percentile
                )
            }

        return thresholds


    def calculate_sampling_interval(self, data):

        time_differences = (
            data["time"]
            .sort_values()
            .diff()
            .dt.total_seconds()
        )

        return time_differences.median()