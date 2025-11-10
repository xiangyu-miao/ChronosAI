import pandas as pd

from .io_tools import get_dataframe, _register_df


def detect_anomalies_iqr(dataframe_id: str, value_column: str, iqr_multiplier: float = 1.5):
    df = get_dataframe(dataframe_id).copy()
    q1 = df[value_column].quantile(0.25)
    q3 = df[value_column].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - iqr_multiplier * iqr
    upper = q3 + iqr_multiplier * iqr
    df["is_anomaly"] = (df[value_column] < lower) | (df[value_column] > upper)
    new_id = _register_df(df)
    return new_id, int(df["is_anomaly"].sum())


