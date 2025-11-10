"""
LLM接口抽象层，支持本地推理和API调用两种模式。
"""
import json
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

from pydantic import BaseModel


class LLMResponse(BaseModel):
    """LLM响应封装"""
    text: str
    finish_reason: str = "stop"
    metadata: Dict = {}


class LLMInterface(ABC):
    """LLM抽象接口"""
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> LLMResponse:
        """生成回复"""
        pass
    
    @abstractmethod
    def chat(self, messages: List[Dict], max_tokens: int = 1024, temperature: float = 0.7) -> LLMResponse:
        """对话接口（历史上下文）"""
        pass


class TransformersLLM(LLMInterface):
    """基于transformers库的本地推理"""
    
    def __init__(self, model_path: str = "microsoft/Phi-3-mini-4k-instruct", device: str = "auto"):
        """
        Args:
            model_path: HuggingFace模型名或本地路径
            device: 'cpu', 'cuda', 'auto'
        """
        self.model_path = model_path
        self.device = device
        self._model = None
        self._tokenizer = None
    
    def _lazy_load(self):
        """延迟加载模型"""
        if self._model is not None:
            return
        
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
        except ImportError as e:
            raise ImportError("请安装transformers和torch: pip install transformers torch") from e
        
        print(f"正在加载本地模型: {self.model_path}...")
        self._tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            trust_remote_code=True
        )
        
        if self.device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self._model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map=self.device if self.device == "cuda" else "cpu",
            trust_remote_code=True
        )
        print("模型加载完成")
    
    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> LLMResponse:
        self._lazy_load()
        
        import torch
        inputs = self._tokenizer(prompt, return_tensors="pt").to(self._model.device)
        with torch.no_grad():
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                pad_token_id=self._tokenizer.eos_token_id
            )
        
        text = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
        # 移除原始prompt部分
        text = text[len(prompt):].strip()
        
        return LLMResponse(text=text, finish_reason="stop")
    
    def chat(self, messages: List[Dict], max_tokens: int = 1024, temperature: float = 0.7) -> LLMResponse:
        """将messages格式化为单一prompt后调用generate"""
        prompt = self._format_chat_messages(messages)
        return self.generate(prompt, max_tokens, temperature)
    
    def _format_chat_messages(self, messages: List[Dict]) -> str:
        """将对话历史格式化为prompt"""
        parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                parts.append(f"System: {content}")
            elif role == "user":
                parts.append(f"User: {content}")
            elif role == "assistant":
                parts.append(f"Assistant: {content}")
        return "\n\n".join(parts)


class APILLM(LLMInterface):
    """通用API调用接口（兼容OpenAI格式）"""
    
    def __init__(self, base_url: str, api_key: str = "", model_name: str = "gpt-3.5-turbo"):
        """
        Args:
            base_url: API基础URL（如 https://api.openai.com/v1）
            api_key: API密钥
            model_name: 模型名称
        """
        self.base_url = base_url
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model_name = model_name
    
    def _make_request(self, endpoint: str, payload: Dict) -> Dict:
        """发起HTTP请求"""
        try:
            import requests
        except ImportError:
            raise ImportError("请安装requests: pip install requests")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
        }
        
        url = f"{self.base_url}/{endpoint}"
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        return resp.json()
    
    def chat(self, messages: List[Dict], max_tokens: int = 1024, temperature: float = 0.7) -> LLMResponse:
        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        data = self._make_request("chat/completions", payload)
        choice = data["choices"][0]
        
        return LLMResponse(
            text=choice["message"]["content"],
            finish_reason=choice.get("finish_reason", "stop"),
            metadata={"usage": data.get("usage", {})}
        )
    
    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> LLMResponse:
        """将单一prompt包装为messages格式调用chat"""
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, max_tokens, temperature)


class SimulatedLLM(LLMInterface):
    """模拟LLM（用于测试，不需要实际模型）"""
    
    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> LLMResponse:
        # 简单的规则匹配演示
        if "load" in prompt.lower() or "加载" in prompt:
            return LLMResponse(text="Thought: 需要加载数据文件\nAction: load_dataframe(file_path='D:/agent/CRWU/Normal Baseline/normal_0.mat', file_type='mat')")
        elif "describe" in prompt.lower() or "描述" in prompt or "统计" in prompt:
            return LLMResponse(text="Thought: 查看数据基本信息\nAction: describe_dataframe(dataframe_id='<last_df_id>')")
        elif "plot" in prompt.lower() or "图表" in prompt or "可视化" in prompt:
            return LLMResponse(text="Thought: 生成时序图\nAction: plot_time_series(dataframe_id='<last_df_id>', time_column='index', value_column='value')")
        elif "anomal" in prompt.lower() or "异常" in prompt:
            return LLMResponse(text="Thought: 检测异常值\nAction: detect_anomalies_iqr(dataframe_id='<last_df_id>', value_column='value')")
        else:
            return LLMResponse(text="Thought: 我理解了你的需求，让我开始处理\nAction: load_dataframe(file_path='D:/agent/CRWU/Normal Baseline/normal_0.mat', file_type='mat')")
    
    def chat(self, messages: List[Dict], max_tokens: int = 1024, temperature: float = 0.7) -> LLMResponse:
        last_msg = messages[-1].get("content", "") if messages else ""
        return self.generate(last_msg, max_tokens, temperature)


def create_llm(llm_type: str = "simulated", **kwargs) -> LLMInterface:
    """
    工厂函数创建LLM实例
    
    Args:
        llm_type: 'simulated', 'local', 'api'
        **kwargs: 传递给对应LLM构造函数的参数
        
    Examples:
        # 模拟模式（测试用）
        llm = create_llm("simulated")
        
        # 本地推理
        llm = create_llm("local", model_path="microsoft/Phi-3-mini-4k-instruct")
        
        # API调用
        llm = create_llm("api", base_url="https://api.openai.com/v1", api_key="xxx")
    """
    if llm_type == "simulated":
        return SimulatedLLM()
    elif llm_type == "local":
        return TransformersLLM(**kwargs)
    elif llm_type == "api":
        return APILLM(**kwargs)
    else:
        raise ValueError(f"Unknown llm_type: {llm_type}")

