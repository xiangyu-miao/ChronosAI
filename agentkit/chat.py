"""
对话式Agent入口，集成真实LLM交互循环
"""
import re
from typing import List, Dict, Optional

from .llm import LLMInterface, create_llm
from .preprocessing import summarize_directory
from .prompt import build_full_prompt
from .executor import execute_action, parse_action


class AgentSession:
    """Agent会话管理"""
    
    def __init__(self, llm: LLMInterface, data_summary: str):
        self.llm = llm
        self.data_summary = data_summary
        self.conversation_history: List[Dict] = []
        self._last_dataframe_id: Optional[str] = None
    
    def _extract_action(self, llm_output: str) -> Optional[str]:
        """从LLM输出中提取Action"""
        # 查找 Action: tool_name(...) 格式
        pattern = r"Action:\s*([a-zA-Z_][a-zA-Z0-9_]*\([^)]*\))"
        matches = re.findall(pattern, llm_output)
        if matches:
            return matches[-1]
        return None
    
    def _update_dataframe_id(self, action: str, result: str):
        """更新最近使用的dataframe_id（用于后续工具调用）"""
        # 简单启发：load_dataframe的结果通常是新的dataframe_id
        if action.startswith("load_dataframe"):
            self._last_dataframe_id = result
        # describe/plot等返回的可能是dataframe_id作为前缀
        if result.startswith("dataframe_") or result.startswith("uuid"):
            self._last_dataframe_id = result
    
    def _replace_placeholder(self, action: str) -> str:
        """替换action中的占位符"""
        if "<last_df_id>" in action or "dataframe_id=" not in action:
            # 如果有占位符但action没给dataframe_id，尝试推断
            if self._last_dataframe_id:
                action = action.replace("<last_df_id>", self._last_dataframe_id)
        return action
    
    def chat_turn(self, user_input: str) -> Dict:
        """
        执行一轮对话（用户输入 -> LLM输出 -> 工具调用 -> 结果反馈）
        
        Returns:
            {
                "llm_output": str,
                "action": str or None,
                "tool_result": str or None,
                "error": str or None
            }
        """
        # 1. 构建完整prompt（首次）
        if not self.conversation_history:
            full_prompt = build_full_prompt(user_input, self.data_summary)
            self.conversation_history.append({"role": "system", "content": full_prompt})
        
        # 添加用户输入
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # 2. 调用LLM
        try:
            llm_response = self.llm.chat(self.conversation_history.copy())
            llm_output = llm_response.text
        except Exception as e:
            return {"error": f"LLM调用失败: {e}"}
        
        # 3. 提取Action
        action = self._extract_action(llm_output)
        
        result = {
            "llm_output": llm_output,
            "action": action,
            "tool_result": None,
            "error": None
        }
        
        # 4. 如果提取到action，执行工具
        if action:
            action = self._replace_placeholder(action)
            try:
                tool_result = execute_action(action)
                result["tool_result"] = str(tool_result)
                
                # 记录本次对话与结果（供下一轮参考）
                self.conversation_history.append({
                    "role": "assistant",
                    "content": f"{llm_output}\n\nTool Result: {tool_result}"
                })
                
                # 更新dataframe_id
                self._update_dataframe_id(action, str(tool_result))
                
            except Exception as e:
                result["error"] = f"工具执行失败: {e}"
                self.conversation_history.append({
                    "role": "assistant",
                    "content": f"{llm_output}\n\nError: {e}"
                })
        else:
            # 没有提取到action，可能是最终回复或中间思考
            self.conversation_history.append({
                "role": "assistant",
                "content": llm_output
            })
        
        return result
    
    def chat_loop(self):
        """主对话循环"""
        print("=== Agent 对话模式（输入 'exit' 退出）===\n")
        print(f"数据目录摘要已加载（包含 {len(self.data_summary.split('目录:'))-1} 个子目录）\n")
        
        while True:
            user = input("你: ").strip()
            if user.lower() in {"exit", "quit", "退出"}:
                print("再见！")
                break
            
            # 执行对话回合
            result = self.chat_turn(user)
            
            # 显示LLM输出
            print("\n[Agent思考]")
            print(result["llm_output"])
            
            # 显示工具调用结果
            if result.get("action"):
                print(f"\n[调用工具] {result['action']}")
            
            if result.get("tool_result"):
                print(f"\n[工具结果] {result['tool_result']}")
            
            if result.get("error"):
                print(f"\n[错误] {result['error']}")
            
            print()


def run_chat(data_root: str, llm_type: str = "simulated", llm_config: dict = None):
    """
    启动对话式Agent
    
    Args:
        data_root: 数据根目录
        llm_type: 'simulated', 'local', 'api'
        llm_config: LLM配置字典（传递给create_llm）
    """
    # 生成数据摘要
    print(f"正在扫描数据目录: {data_root}...")
    data_summary = summarize_directory(data_root, max_files_per_folder=1)
    
    # 创建LLM实例
    llm = create_llm(llm_type=llm_type, **(llm_config or {}))
    
    # 创建会话
    session = AgentSession(llm, data_summary)
    
    # 启动对话循环
    session.chat_loop()
