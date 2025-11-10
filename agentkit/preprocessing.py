import os
import json
from typing import List, Tuple

import numpy as np
import pandas as pd
from scipy.io import loadmat

from .config import AgentConfig


def _safe_read_mat(path: str) -> dict:
    try:
        return loadmat(path)
    except Exception as e:
        return {"__error__": str(e)}


def summarize_mat_file(path: str, max_preview_rows: int = 5) -> str:
    meta = {"file": path, "type": "mat"}
    data = _safe_read_mat(path)
    if "__error__" in data:
        meta["error"] = data["__error__"]
        return json.dumps(meta, ensure_ascii=False)

    keys = [k for k in data.keys() if not k.startswith("__")]
    meta["keys"] = keys
    previews = {}
    for k in keys:
        arr = data[k]
        if isinstance(arr, np.ndarray):
            shape = arr.shape
            dtype = str(arr.dtype)
            previews[k] = {
                "shape": shape,
                "dtype": dtype,
                "preview": arr.flatten()[:max_preview_rows].tolist(),
            }
    meta["previews"] = previews
    return json.dumps(meta, ensure_ascii=False)


def summarize_directory(data_root: str, max_files_per_folder: int = 2) -> str:
    cfg = AgentConfig(data_root=data_root, max_files_per_folder=max_files_per_folder)
    lines: List[str] = []
    for root, _dirs, files in os.walk(cfg.data_root):
        mat_files = [f for f in files if f.lower().endswith(".mat")]
        if not mat_files:
            continue
        lines.append(f"目录: {root}")
        for f in sorted(mat_files)[: cfg.max_files_per_folder]:
            path = os.path.join(root, f)
            lines.append(summarize_mat_file(path))
    return "\n".join(lines)


