from sklearn.linear_model import LinearRegression


class RegressionModel:

    def __init__(self, axis_columns):
        self.axis_columns = axis_columns
        self.models = {}

    def train(self, data):
        model_information = {}

        for axis in self.axis_columns:

            axis_data = data[
                ["elapsed_seconds", axis]
            ].dropna()

            X = axis_data[["elapsed_seconds"]]
            y = axis_data[axis]

            model = LinearRegression()
            model.fit(X, y)

            self.models[axis] = model

            model_information[axis] = {
                "slope": model.coef_[0],
                "intercept": model.intercept_
            }

        return model_information

    def predict(self, data):
        result = data.copy()

        X = result[["elapsed_seconds"]]

        for axis in self.axis_columns:
            model = self.models[axis]

            result[f"{axis}_predicted"] = model.predict(X)

        return result

    def calculate_residuals(self, data):

        result = self.predict(data)

        for axis in self.axis_columns:

            result[f"{axis}_residual"] = (
            result[axis]
            - result[f"{axis}_predicted"]
            )

        return result