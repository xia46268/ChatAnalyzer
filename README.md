# ChatAnalyzer

## 项目简介 / Project Overview

ChatAnalyzer 是一个用于分析聊天数据的工具，能够对聊天记录进行情绪分析、数据可视化以及用户行为统计。它特别适合需要从大量聊天记录中提取信息的用户，例如研究人员或数据分析师。

ChatAnalyzer is a tool designed to analyze chat data, providing sentiment analysis, data visualization, and user behavior statistics. It is ideal for users who need to extract insights from large amounts of chat records, such as researchers or data analysts.

---

## 功能简介 / Features

### 1. 数据预处理 / Data Preprocessing
- 处理聊天记录中的文本、图片和表情包。
- 支持过滤非文本消息，例如图片和表情包。
- 自动修正时间格式并解析相关字段。

Process chat logs, handling text, images, and emojis. 
- Supports filtering out non-text messages such as images and emojis.
- Automatically corrects time formats and parses relevant fields.

---

### 2. 情绪分析 / Sentiment Analysis
- 调用百度 NLP API，对每条聊天记录的情绪进行分类（正面、中性、负面）。
- 支持使用 API 返回的置信度加权情绪结果。

Utilize Baidu NLP API to classify the sentiment of each chat message (positive, neutral, negative). 
- Supports confidence-weighted sentiment results based on API feedback.

---

### 3. 数据可视化 / Data Visualization
- 生成用户情绪分布图，展示不同用户的情绪分类。
- 绘制用户在不同时间段的活跃度分布图。

Generate sentiment distribution plots by user, displaying sentiment categories.  
- Visualize user activity over different time periods.

---

### 4. 用户行为统计 / User Behavior Statistics
- 统计用户的消息数量、总字数、平均字数。
- 计算用户的情绪波动（正面与负面概率的标准差）。

Calculate message count, total word count, and average word count per user.  
- Measure user emotional variability (standard deviation of positive and negative probabilities).

---

## 使用指南 / Usage Guide

### 1. 安装依赖 / Install Dependencies
在虚拟环境中安装项目所需的依赖：
```bash
pip install -r requirements.txt
```

### 2. 使用方法 / How to Use
在 main.py 中设置聊天数据文件路径并运行：
```bash
python3 main.py
```
### 3. 输出结果 / Output
结果将保存为 `sentiment_analysis_results.csv`。
数据可视化图表将保存为 `.png` 文件，例如 `sentiment_distribution.png`。
Results will be saved as `sentiment_analysis_results.csv`.
Visualization charts will be saved as `.png` files, e.g., `sentiment_distribution.png`.



## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
