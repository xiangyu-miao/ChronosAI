"""
快速开始示例：展示如何使用Agent框架
"""
import os
import sys

# 添加项目根目录到path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agentkit.chat import AgentSession
from agentkit.llm import create_llm
from agentkit.preprocessing import summarize_directory


def demo_simulated():
    """演示1：模拟模式（无需模型）"""
    print("=== 演示1：模拟模式 ===")
    
    llm = create_llm("simulated")
    data_summary = summarize_directory("D:\\agent\\CRWU", max_files_per_folder=1)
    session = AgentSession(llm, data_summary)
    
    # 测试几个对话回合
    queries = [
        "请加载normal_0.mat文件",
        "查看数据统计信息",
        "绘制时序曲线"
    ]
    
    for q in queries:
        print(f"\n用户: {q}")
        result = session.chat_turn(q)
        print(f"Agent输出: {result['llm_output']}")
        if result.get('action'):
            print(f"执行的工具: {result['action']}")


def demo_local():
    """演示2：本地推理（需要安装transformers和torch）"""
    print("=== 演示2：本地推理 ===")
    print("注意：需要先安装 pip install -e '.[local]'")
    
    try:
        llm = create_llm(
            "local",
            model_path="microsoft/Phi-3-mini-4k-instruct",
            device="cpu"  # 用CPU避免显存问题
        )
        print("模型加载成功！")
        
        # 简单测试
        response = llm.generate("你好，请回答：1+1等于几？", max_tokens=50)
        print(f"模型回复: {response.text}")
        
    except ImportError as e:
        print(f"未安装本地推理依赖: {e}")
        print("请运行: pip install -e '.[local]'")


def demo_api():
    """演示3：API调用"""
    print("=== 演示3：API调用 ===")
    print("需要配置API密钥")
    
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        print("请设置环境变量: $env:OPENAI_API_KEY='your_key'")
        return
    
    llm = create_llm(
        "api",
        base_url="https://api.openai.com/v1",
        api_key=api_key,
        model_name="gpt-3.5-turbo"
    )
    
    response = llm.generate("你好", max_tokens=50)
    print(f"API回复: {response.text}")


if __name__ == "__main__":
    print("Agent框架快速开始示例\n")
    print("选择演示模式：")
    print("1. 模拟模式（推荐新手）")
    print("2. 本地推理")
    print("3. API调用")
    
    choice = input("\n请输入1-3: ").strip()
    
    if choice == "1":
        demo_simulated()
    elif choice == "2":
        demo_local()
    elif choice == "3":
        demo_api()
    else:
        print("无效选择")

