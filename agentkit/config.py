"""
Agent配置文件管理
"""
import os
from typing import Optional
from pydantic import BaseModel


class AgentConfig(BaseModel):
    """Agent配置"""
    data_root: str
    max_preview_rows: int = 5
    max_files_per_folder: int = 2
    
    # LLM配置
    llm_type: str = "simulated"  # 'simulated', 'local', 'api'
    llm_model_path: str = "microsoft/Phi-3-mini-4k-instruct"  # 本地模型路径或HF模型名
    llm_device: str = "auto"  # 'cpu', 'cuda', 'auto'
    
    # API配置
    api_base_url: str = "https://api.openai.com/v1"
    api_key: Optional[str] = None
    api_model_name: str = "gpt-3.5-turbo"
    
    # 生成参数
    max_tokens: int = 1024
    temperature: float = 0.7


def load_config_from_env() -> AgentConfig:
    """从环境变量加载配置"""
    return AgentConfig(
        data_root=os.getenv("AGENT_DATA_ROOT", "D:\\agent\\CRWU"),
        llm_type=os.getenv("AGENT_LLM_TYPE", "simulated"),
        llm_model_path=os.getenv("AGENT_LLM_MODEL", "microsoft/Phi-3-mini-4k-instruct"),
        api_key=os.getenv("OPENAI_API_KEY") or os.getenv("AGENT_API_KEY"),
    )
