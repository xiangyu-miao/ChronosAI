import os
import requests

def test_openai_chat():
    # 从环境变量读取 API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("请先设置环境变量 OPENAI_API_KEY")

    # OpenAI Chat API 端点
    url = "https://api.openai.com/v1/chat/completions"

    # 请求头
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # 请求体
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "你好，你是谁？"}
        ]
    }

    # 发起请求
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        print("✅ 调用成功，返回内容：")
        print(result["choices"][0]["message"]["content"])
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP错误：{e}")
        print(response.text)
    except Exception as e:
        print(f"❌ 其他错误：{e}")

if __name__ == "__main__":
    test_openai_chat()
