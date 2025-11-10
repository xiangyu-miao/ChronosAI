# Agent使用指南

## 一、安装

### 1. 基础环境
```powershell
# 创建虚拟环境
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1

# 安装基础依赖
pip install -U pip
pip install -e .
```

### 2. 本地推理模式（可选）
如果要使用`--llm=local`，需要安装额外依赖：
```powershell
pip install -e ".[local]"
```
这会安装：transformers, torch, accelerate

## 二、三种模式使用

### 模式1：模拟模式（推荐初学者）

无需真实模型，通过规则匹配生成工具调用。

```powershell
python cli.py chat --data-dir "D:\agent\CRWU" --llm simulated
```

**使用示例：**
```
你: 请加载normal_0.mat文件
[Agent思考]
Thought: 需要加载数据文件
Action: load_dataframe(file_path='D:/agent/CRWU/Normal Baseline/normal_0.mat', file_type='mat')

[调用工具] load_dataframe(...)
[工具结果] <返回的dataframe_id>
```

### 模式2：本地推理

使用transformers加载开源模型（如Phi-3）。

**步骤1：安装依赖**
```powershell
pip install -e ".[local]"
```

**步骤2：运行**
```powershell
# 使用CPU（推荐，避免显存问题）
python cli.py chat --data-dir "D:\agent\CRWU" --llm local --device cpu

# 使用CUDA（需要NVIDIA GPU）
python cli.py chat --data-dir "D:\agent\CRWU" --llm local --device cuda
```

**首次运行会自动下载模型**（约7-8GB，取决于模型选择）。

### 模式3：API调用

调用云端LLM服务（OpenAI等）。

**步骤1：设置API密钥**
```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

**步骤2：运行**
```powershell
# 默认使用gpt-3.5-turbo
python cli.py chat --data-dir "D:\agent\CRWU" --llm api

# 自定义API配置
python cli.py chat --data-dir "D:\agent\CRWU" --llm api --api-url "https://api.openai.com/v1" --api-key YOUR_KEY --api-model gpt-4
```

## 三、完整对话示例

启动对话：
```powershell
python cli.py chat --data-dir "D:\agent\CRWU" --llm simulated
```

交互过程：
```
你: 加载normal_0.mat并查看统计信息

[Agent思考]
Thought: 需要先加载数据文件，然后查看统计信息
Action: load_dataframe(file_path='D:/agent/CRWU/Normal Baseline/normal_0.mat', file_type='mat')

[调用工具] load_dataframe(...)
[工具结果] dataframe_abc123

[Agent继续思考]
Thought: 数据已加载，现在查看统计信息
Action: describe_dataframe(dataframe_id='dataframe_abc123')

[调用工具] describe_dataframe(...)
[工具结果] shape: (121276, 2)
dtypes:
index    int64
value    float64
...
```

## 四、工具使用说明

### load_dataframe
加载数据文件到内存
- 支持格式：`csv`, `parquet`, `hdf5`, `mat`
- 返回：dataframe_id

### describe_dataframe
查看数据统计摘要
- 参数：dataframe_id
- 返回：统计文本（shape, dtypes, head, describe）

### plot_time_series
绘制时序图
- 参数：dataframe_id, time_column, value_column, title, xlabel, ylabel
- 返回：图像文件路径

### detect_anomalies_iqr
IQR异常检测
- 参数：dataframe_id, value_column, iqr_multiplier（默认1.5）
- 返回：新的dataframe_id（含is_anomaly列），异常值数量

### save_dataframe
保存DataFrame到文件
- 参数：dataframe_id, file_path, file_type
- 返回：成功消息

## 五、配置说明

### 环境变量配置
```powershell
# API密钥（用于--llm=api）
$env:OPENAI_API_KEY="sk-..."

# 数据目录
$env:AGENT_DATA_ROOT="D:\agent\CRWU"

# LLM类型
$env:AGENT_LLM_TYPE="simulated"  # 或 "local", "api"
```

### 配置文件
编辑`agentkit/config.py`可调整默认参数。

## 六、故障排除

### 问题1：本地推理内存不足
**解决**：
- 使用`--device cpu`而非`cuda`
- 选择更小的模型（如Phi-3-mini而非Phi-3-medium）
- 关闭其他占用GPU的程序

### 问题2：API调用失败
**检查**：
- API密钥是否正确：`echo $env:OPENAI_API_KEY`
- 网络连接是否正常
- API URL是否正确

### 问题3：工具执行错误
**常见错误**：
- `dataframe_id not found`: 需要先调用`load_dataframe`
- `Invalid action format`: LLM输出的action格式不正确
- 检查LLM输出是否包含正确的Action格式

## 七、开发与扩展

### 添加新工具
1. 在`agentkit/tools/`创建新工具文件
2. 实现工具函数
3. 在`tools/__init__.py`导出
4. 在`executor.py`注册工具
5. 更新`prompt.py`中的工具描述

### 切换LLM后端
```python
# 在chat.py中修改
from agentkit.llm import create_llm

llm = create_llm(
    llm_type="local",  # 或 "api", "simulated"
    model_path="your_model_path",
    device="cuda"
)
```

## 八、性能建议

- **模拟模式**：响应极快，适合测试
- **本地推理**：首次加载慢（需下载模型），后续调用正常
- **API模式**：依赖网络，延迟较高但准确性通常更好

---

如有问题，请查看`README.md`或issues。

