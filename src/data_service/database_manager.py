import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv


class Database:

    def __init__(self):
        """Connect to the Neon PostgreSQL database."""

        load_dotenv()

        self.database_url = os.getenv("DATABASE_URL")

        if not self.database_url:
            raise ValueError(
                "DATABASE_URL was not found in the .env file."
            )

        self.connection = psycopg2.connect(
            self.database_url
        )

        self.cursor = self.connection.cursor()

        # Historical training-data table
        self.table_name = "robot_data"

        # Synthetic testing-data table
        self.synthetic_table_name = "synthetic_stream_data"



    def createTable(self, data_point):
        """Create the historical robot training table."""

        sql_columns = []

        for column in data_point.columns:

            safe_column = self._clean_column_name(
                column
            )

            sql_columns.append(
                f'"{safe_column}" TEXT'
            )

        query = f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id SERIAL PRIMARY KEY,
                {", ".join(sql_columns)}
            )
        """

        self.cursor.execute(query)
        self.connection.commit()


    def insertDataPoint(self, data_point):
        """Insert one historical robot measurement."""

        safe_columns = [
            self._clean_column_name(column)
            for column in data_point.columns
        ]

        values = self._convert_values(
            data_point.iloc[0].tolist()
        )

        placeholders = ", ".join(
            ["%s"] * len(values)
        )

        query = f"""
            INSERT INTO {self.table_name}
            ({", ".join(safe_columns)})
            VALUES ({placeholders})
        """

        self.cursor.execute(
            query,
            values
        )

        self.connection.commit()


    def insertBulkData(self, data):
        """Insert the complete historical training dataset."""

        safe_columns = [
            self._clean_column_name(column)
            for column in data.columns
        ]

        records = []

        for _, row in data.iterrows():

            values = self._convert_values(
                row.tolist()
            )

            records.append(
                tuple(values)
            )

        placeholders = ", ".join(
            ["%s"] * len(data.columns)
        )

        query = f"""
            INSERT INTO {self.table_name}
            ({", ".join(safe_columns)})
            VALUES ({placeholders})
        """

        batch_size = 500

        for i in range(
            0,
            len(records),
            batch_size
        ):

            batch = records[
                i:i + batch_size
            ]

            self.cursor.executemany(
                query,
                batch
            )

            self.connection.commit()

            inserted = min(
                i + batch_size,
                len(records)
            )

            print(
                f"{inserted} records inserted..."
            )

        print("Bulk insertion completed.")

        print(
            "Total records inserted:",
            len(data)
        )


    def fetch_all(self):
        """Retrieve all historical training data."""

        return pd.read_sql(
            f"""
            SELECT *
            FROM {self.table_name}
            ORDER BY id
            """,
            self.connection
        )


    def fetch_latest(self, n=50):
        """Retrieve the latest historical records."""

        data = pd.read_sql(
            f"""
            SELECT *
            FROM {self.table_name}
            ORDER BY id DESC
            LIMIT {n}
            """,
            self.connection
        )

        return data.iloc[::-1]

    def create_synthetic_stream_table(self):
        """Create the table for synthetic testing data."""

        query = f"""
            CREATE TABLE IF NOT EXISTS {self.synthetic_table_name} (
                id SERIAL PRIMARY KEY,
                elapsed_seconds DOUBLE PRECISION,
                axis_1 DOUBLE PRECISION,
                axis_2 DOUBLE PRECISION,
                axis_3 DOUBLE PRECISION,
                axis_4 DOUBLE PRECISION,
                axis_5 DOUBLE PRECISION,
                axis_6 DOUBLE PRECISION,
                axis_7 DOUBLE PRECISION,
                axis_8 DOUBLE PRECISION
            )
        """

        self.cursor.execute(query)
        self.connection.commit()


    def insert_synthetic_data(self, data_point):
        """Insert one synthetic streaming measurement."""

        query = f"""
            INSERT INTO {self.synthetic_table_name} (
                elapsed_seconds,
                axis_1,
                axis_2,
                axis_3,
                axis_4,
                axis_5,
                axis_6,
                axis_7,
                axis_8
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
        """

        values = (
            float(data_point["elapsed_seconds"].iloc[0]),
            float(data_point["axis_1"].iloc[0]),
            float(data_point["axis_2"].iloc[0]),
            float(data_point["axis_3"].iloc[0]),
            float(data_point["axis_4"].iloc[0]),
            float(data_point["axis_5"].iloc[0]),
            float(data_point["axis_6"].iloc[0]),
            float(data_point["axis_7"].iloc[0]),
            float(data_point["axis_8"].iloc[0])
        )

        self.cursor.execute(
            query,
            values
        )

        self.connection.commit()


    def clear_synthetic_data(self):
        """Remove previous synthetic testing records."""

        self.cursor.execute(
            f"DELETE FROM {self.synthetic_table_name}"
        )

        self.connection.commit()


    def count_synthetic_data(self):
        """Return the number of synthetic records."""

        self.cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM {self.synthetic_table_name}
            """
        )

        return self.cursor.fetchone()[0]


    def fetch_synthetic_data(self):
        """Retrieve all synthetic streaming data."""

        return pd.read_sql(
            f"""
            SELECT *
            FROM {self.synthetic_table_name}
            ORDER BY id
            """,
            self.connection
        )




    def _clean_column_name(self, column):
        """Convert CSV column names to database-friendly names."""

        return (
            column.lower()
            .replace(" ", "_")
            .replace("#", "")
        )


    def _convert_values(self, values):
        """Convert pandas/numpy values for PostgreSQL."""

        converted_values = []

        for value in values:

            if pd.isna(value):

                converted_values.append(
                    None
                )

            else:

                converted_values.append(
                    value.item()
                    if hasattr(value, "item")
                    else value
                )

        return converted_values


   

    def close(self):
        """Close the database connection."""

        self.cursor.close()
        self.connection.close()