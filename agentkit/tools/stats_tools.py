from typing import Tuple

import pandas as pd

from .io_tools import get_dataframe


def describe_dataframe(dataframe_id: str) -> str:
    df = get_dataframe(dataframe_id)
    lines = []
    lines.append(f"shape: {df.shape}")
    lines.append("dtypes:")
    lines.append(str(df.dtypes))
    lines.append("head:")
    lines.append(df.head(5).to_csv(index=False))
    lines.append("describe:")
    lines.append(df.describe(include="all").to_csv())
    return "\n".join(lines)


