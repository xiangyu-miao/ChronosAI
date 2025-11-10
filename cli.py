"""
命令行入口
"""
import argparse
import os
from agentkit.chat import run_chat
from agentkit.preprocessing import summarize_directory


def main():
    parser = argparse.ArgumentParser(
        description="Prompt-driven Time-Series Agent (Stage 1)"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    
    # summarize 命令
    p_sum = sub.add_parser("summarize", help="Summarize a data directory")
    p_sum.add_argument("--data_dir", required=True, help="Data root directory")
    p_sum.add_argument("--max_files", type=int, default=2, help="Max files per leaf folder")
    
    # chat 命令
    p_chat = sub.add_parser("chat", help="Interactive chat demo")
    p_chat.add_argument("--data_dir", required=True, help="Data root directory")
    
    # LLM配置选项
    p_chat.add_argument(
        "--llm",
        choices=["simulated", "local", "api"],
        default="simulated",
        help="LLM类型: simulated(模拟), local(本地推理), api(API调用)"
    )
    p_chat.add_argument(
        "--model",
        default="microsoft/Phi-3-mini-4k-instruct",
        help="本地模型路径或HF模型名（仅--llm=local时有效）"
    )
    p_chat.add_argument(
        "--device",
        choices=["cpu", "cuda", "auto"],
        default="auto",
        help="计算设备（仅--llm=local时有效）"
    )
    p_chat.add_argument(
        "--api_url",
        help="API基础URL（仅--llm=api时有效，如 https://api.openai.com/v1）"
    )
    p_chat.add_argument(
        "--api_key",
        help="API密钥（仅--llm=api时有效，也可用OPENAI_API_KEY环境变量）"
    )
    p_chat.add_argument(
        "--api_model",
        default="gpt-3.5-turbo",
        help="API模型名称（仅--llm=api时有效）"
    )
    
    args = parser.parse_args()
    
    if args.command == "summarize":
        text = summarize_directory(args.data_dir, args.max_files)
        print(text)
    
    elif args.command == "chat":
        # 构建LLM配置
        llm_config = {}
        if args.llm == "local":
            llm_config = {
                "model_path": args.model,
                "device": args.device
            }
        elif args.llm == "api":
            llm_config = {
                "base_url": args.api_url or os.getenv("OPENAI_API_URL", "https://api.openai.com/v1"),
                "api_key": args.api_key or os.getenv("OPENAI_API_KEY", ""),
                "model_name": args.api_model
            }
        
        run_chat(
            data_root=args.data_dir,
            llm_type=args.llm,
            llm_config=llm_config
        )


if __name__ == "__main__":
    main()
