import os
import uuid
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .io_tools import get_dataframe


def plot_time_series(dataframe_id: str, time_column: str, value_column: str,
                     title: str = "", xlabel: str = "", ylabel: str = "",
                     output_dir: str = "outputs") -> str:
    df = get_dataframe(dataframe_id)
    if time_column not in df.columns:
        # fallback: create pseudo time index
        df = df.copy()
        df[time_column] = range(len(df))
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"ts_{uuid.uuid4().hex[:8]}.png")
    plt.figure(figsize=(10, 4))
    plt.plot(df[time_column], df[value_column])
    plt.title(title or f"{value_column} over {time_column}")
    plt.xlabel(xlabel or time_column)
    plt.ylabel(ylabel or value_column)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    return path


