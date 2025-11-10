import ast
import re
from typing import Any, Dict, Tuple

from .tools import (
    load_dataframe,
    save_dataframe,
    describe_dataframe,
    plot_time_series,
    detect_anomalies_iqr,
)


_TOOL_REGISTRY = {
    "load_dataframe": load_dataframe,
    "save_dataframe": save_dataframe,
    "describe_dataframe": describe_dataframe,
    "plot_time_series": plot_time_series,
    "detect_anomalies_iqr": detect_anomalies_iqr,
}


def parse_action(text: str) -> Tuple[str, Dict[str, Any]]:
    # Expected format: tool_name(arg1=value1, arg2=value2)
    m = re.match(r"\s*([a-zA-Z_][a-zA-Z0-9_]*)\((.*)\)\s*\Z", text, re.S)
    if not m:
        raise ValueError("Invalid action format")
    name, args_src = m.group(1), m.group(2).strip()
    if not args_src:
        return name, {}
    # Build a dict literal from kw args by wrapping into dict(...)
    # Safer: parse as AST call and extract keywords
    node = ast.parse(f"f({args_src})", mode="eval")
    if not isinstance(node.body, ast.Call):
        raise ValueError("Invalid action args")
    kwargs = {}
    for kw in node.body.keywords:
        kwargs[kw.arg] = ast.literal_eval(kw.value)
    return name, kwargs


def execute_action(action: str):
    name, kwargs = parse_action(action)
    if name not in _TOOL_REGISTRY:
        raise KeyError(f"Unknown tool: {name}")
    func = _TOOL_REGISTRY[name]
    return func(**kwargs)


