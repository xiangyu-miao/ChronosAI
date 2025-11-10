import os
import uuid
from typing import Dict, Optional

import pandas as pd
import numpy as np
from scipy.io import loadmat


_DATAFRAMES: Dict[str, pd.DataFrame] = {}


def _register_df(df: pd.DataFrame) -> str:
    df_id = str(uuid.uuid4())
    _DATAFRAMES[df_id] = df
    return df_id


def load_dataframe(file_path: str, file_type: str = "csv") -> str:
    if file_type == "csv":
        df = pd.read_csv(file_path)
        return _register_df(df)
    if file_type == "parquet":
        df = pd.read_parquet(file_path)
        return _register_df(df)
    if file_type == "hdf5":
        df = pd.read_hdf(file_path)
        return _register_df(df)
    if file_type == "mat":
        mat = loadmat(file_path)
        # Heuristic: pick first ndarray as a series
        keys = [k for k in mat.keys() if not k.startswith("__")]
        if not keys:
            raise ValueError("No arrays in .mat file")
        arr = None
        for k in keys:
            if isinstance(mat[k], np.ndarray):
                arr = mat[k]
                break
        if arr is None:
            raise ValueError("No ndarray in .mat file")
        series = pd.Series(arr.flatten(), name=keys[0])
        df = pd.DataFrame({"index": range(len(series)), "value": series.values})
        return _register_df(df)
    raise ValueError(f"Unsupported file_type: {file_type}")


def get_dataframe(df_id: str) -> pd.DataFrame:
    if df_id not in _DATAFRAMES:
        raise KeyError("dataframe_id not found")
    return _DATAFRAMES[df_id]


def save_dataframe(dataframe_id: str, file_path: str, file_type: str = "csv") -> str:
    df = get_dataframe(dataframe_id)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if file_type == "csv":
        df.to_csv(file_path, index=False)
        return f"saved: {file_path}"
    if file_type == "parquet":
        df.to_parquet(file_path, index=False)
        return f"saved: {file_path}"
    if file_type == "hdf5":
        df.to_hdf(file_path, key="data", mode="w")
        return f"saved: {file_path}"
    raise ValueError(f"Unsupported file_type: {file_type}")


