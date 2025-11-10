"""
快速测试脚本：验证Agent所有模块是否正常工作
"""
import sys
import os

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    try:
        from agentkit.llm import create_llm, LLMResponse
        from agentkit.chat import AgentSession
        from agentkit.preprocessing import summarize_directory
        from agentkit.prompt import build_full_prompt
        from agentkit.executor import execute_action
        print("✓ 所有模块导入成功")
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_simulated_llm():
    """测试模拟LLM"""
    print("\n测试模拟LLM...")
    try:
        from agentkit.llm import create_llm
        llm = create_llm("simulated")
        response = llm.generate("test", max_tokens=50)
        print(f"✓ 模拟LLM测试成功，输出: {response.text[:50]}")
        return True
    except Exception as e:
        print(f"✗ 模拟LLM测试失败: {e}")
        return False

def test_preprocessing():
    """测试数据预处理"""
    print("\n测试数据预处理...")
    try:
        from agentkit.preprocessing import summarize_directory
        summary = summarize_directory("data/CWRU", max_files_per_folder=1)
        if len(summary) > 0:
            print("✓ 数据预处理成功，摘要长度:", len(summary))
            return True
        else:
            print("✗ 数据预处理返回空结果")
            return False
    except Exception as e:
        print(f"✗ 数据预处理失败: {e}")
        return False

def test_tools():
    """测试工具库"""
    print("\n测试工具库...")
    try:
        from agentkit.tools import load_dataframe, describe_dataframe
        
        # 测试加载（需要真实文件存在）
        test_file = "data/CWRU/Normal Baseline/normal_0.mat"
        if os.path.exists(test_file):
            df_id = load_dataframe(test_file, "mat")
            print(f"✓ 工具load_dataframe成功，返回ID: {df_id[:20]}")
            
            desc = describe_dataframe(df_id)
            print(f"✓ 工具describe_dataframe成功，输出长度: {len(desc)}")
            return True
        else:
            print(f"⚠ 测试文件不存在: {test_file}")
            print("  跳过工具执行测试")
            return True
    except Exception as e:
        print(f"✗ 工具测试失败: {e}")
        return False

def main():
    print("=" * 50)
    print("Agent模块测试")
    print("=" * 50)
    
    results = []
    results.append(("模块导入", test_imports()))
    results.append(("模拟LLM", test_simulated_llm()))
    results.append(("数据预处理", test_preprocessing()))
    results.append(("工具库", test_tools()))
    
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！可以开始使用Agent了")
    else:
        print("\n⚠ 部分测试失败，请检查错误信息")

if __name__ == "__main__":
    main()

