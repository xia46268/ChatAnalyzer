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
- 使用词云展示聊天中高频词汇。

Plots user sentiment trends, showing sentiment volatility over time.  
- Generates sentiment distribution charts to visualize user sentiment categories.  
- Visualizes user activity during different time periods.  
- Displays monthly message distribution for each user.  
- Generates word clouds to display high-frequency words in chats.

---

### 4. 用户行为统计 / User Behavior Statistics
- 统计用户的消息数量、总字数、平均字数。
- 计算用户的情绪波动（正面与负面概率的标准差）。
- 分析用户的消息时间间隔，识别“破冰者”和“消失者”。
- 对特定关键词进行频率统计，例如“哈”。

Calculates message count, total word count, and average word count per user.  
- Measures user emotional variability (standard deviation of positive and negative probabilities).  
- Analyzes message time intervals to identify "Ice Breakers" and "Vanishers."  
- Counts specific keywords' frequency, such as "ha."

---

## 使用指南 / Usage Guide

### 1. 选择模式 / Select Mode
ChatAnalyzer 提供以下三种模式，用户可以根据需求选择不同的分析模式：

ChatAnalyzer provides the following three modes, and users can choose different analysis modes according to their needs:

- `sample`

  进行小样本数据分析（随机抽取 100 条聊天记录）。A small sample of data was analyzed (100 randomly selected chat logs).
  
  ```bash
  chatanalyzer sample
  ```
- `request`
  
  进行全量数据分析，将数据批量发送至百度 API。Perform full data analysis and send data to the Baidu API in batches.
  
  ```bash
  chatanalyzer request
  ```
- `analyze`
  
  分析从 API 返回的结果并生成数据统计和可视化。Analyze the results returned from the API and generate data statistics and visualizations.
  
   ```bash
  chatanalyzer analyze
  ``` 

---

### 2. 数据文件命名和存储路径 / Data File Naming and Storage Path
- `sample`
  
  输入文件名：`sample_data.csv`
  
  存放路径：将文件存储在运行命令的同级目录中。
  
- `request`
  
  输入文件名：`full_data.csv`
  
  存放路径：同样存储在当前目录中，API 返回结果将保存为 `api_output.csv`。

- `analyze`
  
  输入文件名：`api_output.csv`
  
  分析结果输出为 `final_analysis.csv`，图表保存为 `.png` 文件。


- `sample`
  
  Enter the file name：`sample_data.csv`
    
  Storage path: Store the file in the same level directory as the command being run.
  
- `request` 
  Enter the file name：`full_data.csv`

  Storage path: Also stored in the current directory, the API return result will be saved as `api_output.csv`.
  
- `analyze` 
  Enter the file name：`api_output.csv`

  The analysis results are output as `final_analysis.csv` and the charts are saved as `.png` files.

---

### 3. 输出结果 / Output
- 分析结果以易读格式输出，并支持生成以下图表：用户活跃时间分布图，用户情绪趋势图，用户月度消息分布图，词云图。
- 分析结果保存为 `.csv` 文件，例如 `final_analysis.csv`。
- 可视化图表保存为 `.png` 文件，例如 `sentiment_distribution.png`。
- 输出文件将存储在与输入文件相同的目录中。

- The analysis results are output in an easy-to-read format and support the generation of the following charts: user activity time distribution chart, user sentiment trend chart, user monthly message distribution chart, word cloud chart.
- The analysis results are saved as a `.csv` file, for example `final_analysis.csv`.
- The visual charts are saved as `.png` files, for example `sentiment_distribution.png`.
- The output files will be stored in the same directory as the

---

## 配置 Baidu API 密钥 / Configure Baidu API key

要使用本工具，您需要提供[百度 NLP API](https://ai.baidu.com/ai-doc/REFERENCE/Ck3dwjgn3) 的 API Key 和 Secret Key。程序会根据这些密钥自动生成 Access Token。

To use this tool, you need to provide the API Key and Secret Key of the [Baidu NLP API](https://ai.baidu.com/ai-doc/REFERENCE/Ck3dwjgn3). The program will automatically generate an Access Token based on these keys.

### 使用步骤 / Steps to use

1. 启动程序后，系统将提示您输入 API Key 和 Secret Key。
2. 程序将自动生成 Access Token，并将其保存到 `access_token.txt` 文件中供后续使用。

1. After starting the program, you will be prompted to enter the API Key and Secret Key.
2. The program will automatically generate an Access Token and save it to the `access_token.txt` file for subsequent use.

### 示例 e.g.

```bash
$ python3 main.py analyze
Enter your Baidu API Key: <Your API Key>
Enter your Baidu Secret Key: <Your Secret Key>
New Access Token: <Generated Access Token>
```

--- 

## 许可 / License
该项目已获得MIT许可——详情请参阅[许可](LICENSE)文件。
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
