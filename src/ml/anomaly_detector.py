import pandas as pd


class AnomalyDetector:

    def __init__(
        self,
        axis_columns,
        thresholds,
        duration_threshold
    ):
        self.axis_columns = axis_columns
        self.thresholds = thresholds
        self.duration_threshold = duration_threshold

        self.active_events = {}

        for axis in axis_columns:

            self.active_events[axis] = {
                "start_time": None,
                "level": None
            }

        self.event_log = []


    def check_reading(
        self,
        elapsed_seconds,
        axis,
        residual
    ):
        """Check one residual for Alert/Error conditions."""

        min_c = (
            self.thresholds[axis]["MinC"]
        )

        max_c = (
            self.thresholds[axis]["MaxC"]
        )

        event = self.active_events[axis]

        if residual >= max_c:

            current_level = "ERROR"

        elif residual >= min_c:

            current_level = "ALERT"

        else:

            self.active_events[axis] = {
                "start_time": None,
                "level": None
            }

            return None


        if event["start_time"] is None:

            self.active_events[axis] = {
                "start_time": elapsed_seconds,
                "level": current_level
            }

            return None


        if current_level == "ERROR":

            self.active_events[axis][
                "level"
            ] = "ERROR"


        duration = (
            elapsed_seconds
            - self.active_events[axis][
                "start_time"
            ]
        )


        if duration >= self.duration_threshold:

            detected_event = {
                "axis": axis,
                "event_type":
                    self.active_events[axis]["level"],
                "start_time":
                    self.active_events[axis]["start_time"],
                "detected_time":
                    elapsed_seconds,
                "duration_seconds":
                    duration,
                "residual":
                    residual
            }

            self.event_log.append(
                detected_event
            )

            self.active_events[axis] = {
                "start_time": None,
                "level": None
            }

            return detected_event

        return None


    def get_event_log(self):
        """Return detected events as a DataFrame."""

        return pd.DataFrame(
            self.event_log
        )