from typing import Dict


TOOLS_DESCRIPTION = """
Tool: load_dataframe
Description: 加载CSV/Parquet/HDF5/MAT文件到内存并返回DataFrame ID。
Parameters:
  file_path (str)
  file_type (str, one of: csv, parquet, hdf5, mat)
Returns: dataframe_id (str)

Tool: describe_dataframe
Description: 输出DataFrame的维度、dtypes、head与统计摘要。
Parameters:
  dataframe_id (str)
Returns: description_text (str)

Tool: plot_time_series
Description: 绘制时序线图并返回图像路径。
Parameters:
  dataframe_id (str)
  time_column (str)
  value_column (str)
  title (str, optional)
  xlabel (str, optional)
  ylabel (str, optional)
Returns: plot_image_path (str)

Tool: detect_anomalies_iqr
Description: 使用IQR法检测异常，返回新DataFrame ID与异常数。
Parameters:
  dataframe_id (str)
  value_column (str)
  iqr_multiplier (float, optional)
Returns: modified_dataframe_id (str), anomaly_count (int)

Tool: save_dataframe
Description: 保存DataFrame到指定路径。
Parameters:
  dataframe_id (str)
  file_path (str)
  file_type (str, optional)
Returns: success_message (str)
""".strip()


def build_full_prompt(user_instruction: str, data_summary: str) -> str:
    system = (
        "你是一个基于AI-Agent的工程时序数据分析专家。你的任务是根据用户提供的自然语言指令和时序数据，通过调用合适的工具来执行数据分析、可视化、异常检测、预测等任务。\n\n"
        "工作流程:\n"
        "1. 理解用户指令和当前数据状态。\n"
        "2. 思考需要解决的问题，分解任务。\n"
        "3. 根据任务需求，选择合适的工具。\n"
        "4. 调用工具，并处理工具的输出。\n"
        "5. 根据工具输出，继续思考、选择工具，直到任务完成。\n"
        "6. 最后，以清晰、简洁的方式向用户呈现分析结果和洞察。\n\n"
        "核心原则:\n"
        "- 每次行动前，请先进行\"Thought\"（思考），说明你的决策逻辑。\n"
        "- 优先使用提供的工具，而不是直接生成代码或数据。\n"
        "- 如果工具调用失败，请分析原因并尝试修正。\n"
        "- 任务完成后，总结并提供最终答案或建议。\n"
    )
    template = (
        f"--- System Message ---\n{system}\n"
        f"--- Tools ---\n{TOOLS_DESCRIPTION}\n\n"
        f"--- Current Data Context ---\n{data_summary}\n\n"
        f"--- User Instruction ---\n{user_instruction}\n\n"
        f"--- Begin Task ---\nThought:"
    )
    return template


