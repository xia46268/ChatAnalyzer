# ChatAnalyzer

## 项目简介 / Project Overview

ChatAnalyzer 是一个用于分析中文聊天数据的工具，能够对聊天记录进行情绪分析、数据可视化以及用户行为统计。它特别适合需要从大量聊天记录中提取信息的用户，例如研究人员或数据分析师。

ChatAnalyzer is a tool designed to analyze Chinese chat data, providing sentiment analysis, data visualization, and user behavior statistics. It is ideal for users who need to extract insights from large amounts of chat records, such as researchers or data analysts.

---

## 功能简介 / Features

### 1. 数据预处理 / Data Preprocessing
- 支持随机抽取聊天记录中的100条（可自定义）进行小样本分析。
- 过滤非文本消息，例如图片和表情包。
- 自动修正时间格式并解析相关字段。

Supports random sampling of 100 chat records (customizable) for small-sample analysis.  
- Filters non-text messages such as images and emojis.  
- Automatically corrects time formats and parses relevant fields.

---

### 2. 情绪分析 / Sentiment Analysis
- 调用百度 NLP API，对每条聊天记录的情绪进行分类（正面、中性、负面）。
- 支持对整个样本或小样本进行情绪分析。
- 使用 API 返回的置信度对情绪结果进行加权。

Utilizes Baidu NLP API to classify the sentiment of each chat message (positive, neutral, negative).  
- Supports sentiment analysis for both full and small sample datasets.  
- Confidence-weighted sentiment results based on API feedback.

---

### 3. 数据可视化 / Data Visualization
- 绘制用户情绪趋势图，展示特定时间内情绪波动。
- 生成用户情绪分布图，直观展示用户的情绪类别分布。
- 绘制用户在不同时间段的活跃度分布图。
- 生成用户的月度消息分布图。

Plots user sentiment trends, showing sentiment volatility over time.  
- Generates sentiment distribution charts to visualize user sentiment categories.  
- Visualizes user activity during different time periods.  
- Displays monthly message distribution for each user.

---

### 4. 用户行为统计 / User Behavior Statistics
- 统计用户的消息数量、总字数、平均字数。
- 计算用户的情绪波动（正面与负面概率的标准差）。
- 分析用户的消息时间间隔，识别“破冰者”和“消失者”。

Calculates message count, total word count, and average word count per user.  
- Measures user emotional variability (standard deviation of positive and negative probabilities).  
- Analyzes message time intervals to identify "Ice Breakers" and "Vanishers."

---

## 使用指南 / Usage Guide

### 1. 安装依赖 / Install Dependencies
在虚拟环境中安装项目所需的依赖：
```bash
pip install -r requirements.txt
```
---

### 2. 使用方法 / How to Use
在 main.py 中设置聊天数据文件路径并运行：
```bash
python3 main.py
```

---

### 3. 输出结果 / Output
结果将保存为 `sentiment_analysis_results.csv`。
数据可视化图表将保存为 `.png` 文件，例如 `sentiment_distribution.png`。

Results will be saved as `sentiment_analysis_results.csv`.
Visualization charts will be saved as `.png` files, e.g., `sentiment_distribution.png`.

---

## 许可 / License
该项目已获得MIT许可——详情请参阅[许可](LICENSE)文件。
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
