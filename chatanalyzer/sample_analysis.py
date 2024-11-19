import random
import pandas as pd
import requests
from tqdm import tqdm
from chatanalyzer.auth import BaiduAuth
from chatanalyzer.data_preprocessing import load_and_preprocess_data
from chatanalyzer.sentiment_utils import calculate_emotional_variability, get_peak_hour_activity, analyze_sentiment



def analyze_sample_data(file_path, output_path, sample_size=30):
    """
    Perform sentiment analysis on a sample of the data and generate summary.
    """
    # 加载和预处理数据
    df = load_and_preprocess_data(file_path)
    df = df[df['MessageType'] == 'text']  # 只分析文本消息

    total_records = len(df)

    # 随机采样
    random_state = random.randint(1, 10000)
    print(f"Random State Used: {random_state}")
    sampled_df = df.sample(sample_size, random_state=random_state)

    # 获取并检查百度 API 访问令牌
    auth_client = BaiduAuth()
    auth_client.load_access_token()
    if not auth_client.is_token_valid():
        auth_client.get_access_token()
        auth_client.save_access_token()

    access_token = auth_client.access_token
    results = []

    # 逐行进行情绪分析
    for _, row in tqdm(sampled_df.iterrows(), total=sampled_df.shape[0], desc="Analyzing Sentiment"):
        content = row['StrContent']
        if content.strip():  # 跳过空文本
            sentiment_result = analyze_sentiment(access_token, content, retries=3, timeout=10)
            sentiment_data = {
                "Text": content,
                "StrTime": row['StrTime'],
                "User": row['User'],
                "MessageType": row['MessageType'],
                "Sentiment": sentiment_result.get('Sentiment'),
                "Confidence": sentiment_result.get('Confidence'),
                "Positive_Prob": sentiment_result.get('Positive_Prob'),
                "Negative_Prob": sentiment_result.get('Negative_Prob')
            }
            results.append(sentiment_data)
        else:
            # 处理空文本，直接保存基本信息
            results.append({
                "Text": content,
                "StrTime": row['StrTime'],
                "User": row['User'],
                "MessageType": row['MessageType'],
                "Sentiment": 1,  # 中性情绪
                "Confidence": 0.0,
                "Positive_Prob": 0.0,
                "Negative_Prob": 0.0
            })

    # 创建结果 DataFrame
    result_df = pd.DataFrame(results)

    # 输出 DataFrame 的信息以检查数据
    print("Saving DataFrame to CSV:")
    print(result_df.info())

    # 保存到 CSV 文件
    result_df.to_csv(output_path, index=False)
    print(f"Analysis complete. Results saved to {output_path}")

    # 生成总结报告
    generate_summary_report(result_df, total_records, sample_size)

def generate_summary_report(df, total_records, sample_size):
    """
    Generate a textual summary of the analysis results.
    """
    unique_users = df['User'].nunique()
    records_per_user = df['User'].value_counts()
    avg_words_per_user = df.groupby('User')['Text'].apply(lambda x: x.str.len().mean())

    user_summary = df.groupby("User")[["Positive_Prob", "Negative_Prob"]].mean()

    # 确保用户按照顺序输出（比如 'User1', 'User2'）
    user_1 = records_per_user.index[0]
    user_2 = records_per_user.index[1]

    summary = f"""
    已成功随机抽取你们共 {total_records} 条聊天记录中的 {sample_size} 条！

    其中有 {records_per_user[user_1]} 条是由 '{user_1}' 发送的，平均每条消息 {avg_words_per_user[user_1]:.2f} 字。
    另外有 {records_per_user[user_2]} 条是由 '{user_2}' 发送的，平均每条消息 {avg_words_per_user[user_2]:.2f} 字。

    从情绪分析来看，'{user_1}' 平均积极情绪为 {user_summary.loc[user_1, 'Positive_Prob']:.2f}，平均消极情绪为 {user_summary.loc[user_1, 'Negative_Prob']:.2f}；
    '{user_2}' 平均积极情绪为 {user_summary.loc[user_2, 'Positive_Prob']:.2f}，平均消极情绪为 {user_summary.loc[user_2, 'Negative_Prob']:.2f}。
    """

    print(summary)

if __name__ == "__main__":
    input_file = "sample_data.csv"  # 输入文件路径
    output_file = "output_sample.csv"  # 输出文件路径
    analyze_sample_data(input_file, output_file)
