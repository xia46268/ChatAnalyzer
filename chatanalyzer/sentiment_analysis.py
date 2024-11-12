import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
from chatanalyzer.auth import BaiduAuth
from chatanalyzer.data_preprocessing import load_and_preprocess_data 
from chatanalyzer.visualization import (
    assign_colors, 
    plot_sentiment_trend,
    plot_sentiment_volatility,
    plot_active_hours_distribution,
    plot_monthly_message_distribution,
    plot_sentiment_distribution
)

def analyze_sentiment(access_token, text, retries=3, timeout=10):
    """
    Use Baidu NLP API to perform sentiment analysis with retries and timeout.

    Parameters:
    - access_token (str): The API access token.
    - text (str): The text to analyze.
    - retries (int): Number of retry attempts in case of failure.
    - timeout (int): Timeout for the API request in seconds.

    Returns:
    - dict: The sentiment analysis result or None if the request fails.
    """
    if not text.strip():  # 忽略空文本 ignore empty text
        return None
    
    url = f"https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify?access_token={access_token}"
    headers = {"Content-Type": "application/json"}
    payload = {"text": text}

    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            if response.status_code == 200:
                return response.json().get("items", [{}])[0]  # Return the first result
            else:
                print(f"Error {response.status_code}: {response.json()}")
                return None
        except requests.exceptions.Timeout:
            print(f"Timeout occurred on attempt {attempt + 1}. Retrying...")
        except requests.exceptions.RequestException as e:
            print(f"Request error on attempt {attempt + 1}: {e}")
        
    print("Failed to analyze sentiment after multiple retries.")
    return None
    pass

# 小样本分析：sample_size可调整； Small sample analysis: sample_size is adjustable
def analyze_sample_data(file_path, output_path, sample_size=100):
    """
    Perform sentiment analysis on a sample of the data.

    Parameters:
    - file_path (str): Path to the input CSV file.
    - output_path (str): Path to save the sample sentiment analysis results.
    - sample_size (int): Number of samples to analyze.
    """
    df = load_and_preprocess_data(file_path)
    random_state = random.randint(1, 10000)
    print(f"Random State Used: {random_state}")

    sampled_df = df.sample(sample_size, random_state=random_state)
    results = []

    auth_client = BaiduAuth()
    auth_client.load_access_token()
    if not auth_client.is_token_valid():
        auth_client.get_access_token()
        auth_client.save_access_token()

    for _, row in tqdm(sampled_df.iterrows(), total=sampled_df.shape[0], desc="Analyzing Sentiment"):
        content = row['StrContent']
        if row['MessageType'] == 'text':
            sentiment_result = analyze_sentiment(auth_client.access_token, content, retries=5, timeout=15)
            if sentiment_result:
                sentiment_data = {
                    "Text": content,
                    "StrTime": row['StrTime'],
                    "User": row['Remark'],
                    "MessageType": row['MessageType'],
                    "Sentiment": sentiment_result.get('sentiment'),
                    "Confidence": sentiment_result.get('confidence', 0.0),
                    "Positive_Prob": sentiment_result.get('positive_prob', 0.0),
                    "Negative_Prob": sentiment_result.get('negative_prob', 0.0)
                }
                results.append(sentiment_data)
        else:
            results.append({
                "Text": content,
                "StrTime": row['StrTime'],
                "User": row['Remark'],
                "MessageType": row['MessageType'],
                "Sentiment": None,
                "Confidence": None,
                "Positive_Prob": None,
                "Negative_Prob": None
            })

    result_df = pd.DataFrame(results)
    result_df.to_csv(output_path, index=False)
    print(f"Analysis complete. Results saved to {output_path}")

    # Statistics and visualizations
    user_stats = result_df[result_df['MessageType'] == 'text'].groupby('User').agg(
        Message_Count=('Text', 'count'),
        Total_Words=('Text', lambda x: x.str.len().sum()),
        Avg_Words=('Text', lambda x: x.str.len().mean())
    )
    print("User Message Statistics (Text Only):\n", user_stats)

    sentiment_counts = result_df['Sentiment'].value_counts()
    print("Statistical Distribution of Sentiment:\n", sentiment_counts)

    user_sentiment_avg = result_df.groupby('User')[['Positive_Prob', 'Negative_Prob']].mean()
    print("Mean User Emotional Rating:\n", user_sentiment_avg)

    result_df['Weighted_Positive'] = result_df['Positive_Prob'] * result_df['Confidence']
    result_df['Weighted_Negative'] = result_df['Negative_Prob'] * result_df['Confidence']
    user_weighted_sentiment = result_df.groupby('User')[['Weighted_Positive', 'Weighted_Negative']].mean()
    print("Mean User Weighted Emotional Rating:\n", user_weighted_sentiment)

    user_colors = assign_colors(df)
    plot_active_hours_distribution(result_df, user_colors)
    plot_sentiment_distribution(result_df, user_colors)
    variability = calculate_emotional_variability(result_df)
    print("Emotional Variability:\n", variability)

# 全样本分析 连接API；Full sample analysis Connect to API
def batch_request_api(file_path, output_path, batch_size=100):
    """
    Perform sentiment analysis via API in batches and save intermediate results.
    """
    df = load_and_preprocess_data(file_path)
    df = df[df['MessageType'] == 'text']  # Filter text messages

    # Load existing results if available
    if os.path.exists(output_path):
        processed_df = pd.read_csv(output_path)
        processed_ids = set(processed_df['StrTime'] + processed_df['User'])
    else:
        processed_ids = set()

    auth_client = BaiduAuth()
    auth_client.load_access_token()
    if not auth_client.is_token_valid():
        auth_client.get_access_token()
        auth_client.save_access_token()

    for i in tqdm(range(0, len(df), batch_size), desc="Requesting Sentiment Analysis"):
        batch = df.iloc[i:i + batch_size]
        batch = batch[~((batch['StrTime'].dt.strftime('%Y-%m-%d %H:%M:%S') + batch['User']).isin(processed_ids))]

        results = []
        for _, row in batch.iterrows():
            sentiment_result = analyze_sentiment(auth_client.access_token, row['StrContent'], retries=5, timeout=15)
            if sentiment_result:
                results.append({
                    "Text": row['StrContent'],
                    "StrTime": row['StrTime'],
                    "User": row['User'],
                    "MessageType": row['MessageType'],
                    "Sentiment": sentiment_result.get('sentiment', None),
                    "Confidence": sentiment_result.get('confidence', 0.0),
                    "Positive_Prob": sentiment_result.get('positive_prob', 0.0),
                    "Negative_Prob": sentiment_result.get('negative_prob', 0.0),
                })

        if results:
            batch_results_df = pd.DataFrame(results)
            batch_results_df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)
            processed_ids.update(batch['StrTime'].dt.strftime('%Y-%m-%d %H:%M:%S') + batch['User'])

            print("Sample Result:\n", batch_results_df.iloc[0])
    pass

def analyze_saved_results(input_path, analysis_output_path):
    """
    Analyze the results saved from API requests.
    """
    df = pd.read_csv(input_path)
    df['StrTime'] = pd.to_datetime(df['StrTime'])
    
    # Visualizations
    user_colors = assign_colors(df)
    plot_sentiment_distribution(df, user_colors)
    plot_monthly_message_distribution(df, user_colors)
    plot_sentiment_trend(df, user_colors)
    plot_active_hours_distribution(df, user_colors)
    plot_sentiment_volatility(df, user_colors)    

    # Statistics 
    user_stats = df.groupby('User').agg(
        Message_Count=('Text', 'count'),
        Total_Words=('Text', lambda x: x.str.len().sum()),
        Avg_Words=('Text', lambda x: x.str.len().mean())
    )
    user_stats.to_csv(analysis_output_path)
    print(f"Analysis saved to {analysis_output_path}")

    # 计算消息时间间隔；Calculate message interval
    df['Time_Diff'] = df.groupby('User')['StrTime'].diff().dt.total_seconds().div(60)  # 以分钟计算
    time_stats = df.groupby('User')['Time_Diff'].agg(['mean', 'var']).fillna(0)
    print("Time Interval Statistics:\n", time_stats)

    # 计算破冰者和消失者；Calculate ice breakers and vanishers
    silence_break_stats = calculate_silence_breakers(df)
    print("破冰者比例:\n", silence_break_stats['breaker_ratio'])
    print("消失者比例:\n", silence_break_stats['vanish_ratio'])

    # 计算并打印情感波动；Calculate and print emotional variability
    variability = calculate_emotional_variability(df)

def calculate_silence_breakers(df):
    """
    Calculate silence breakers (破冰者) and vanishers (消失者).

    Parameters:
    - df (DataFrame): Input DataFrame with 'StrTime' and 'User' columns.

    Returns:
    - dict: Containing breaker_ratio and vanish_ratio.
    """
    df['Is_破冰者'] = (df['Time_Diff'] > 720)  # 超过12小时后第一个发言；The first speaker after 12h
    df['Is_消失者'] = (df['Time_Diff'] > 60) & (~df['Is_破冰者'])  # 超过60分钟但小于12小时后第一个发言； The first speaker after 60 mins but less than 12h

    breaker_counts = df[df['Is_破冰者']].groupby('User').size()
    vanish_counts = df[df['Is_消失者']].groupby('User').size()
    total_counts = df.groupby('User').size()

    breaker_ratio = (breaker_counts / total_counts).fillna(0)
    vanish_ratio = (vanish_counts / total_counts).fillna(0)

    return {'breaker_ratio': breaker_ratio, 'vanish_ratio': vanish_ratio}


def calculate_emotional_variability(df):
    """
    Calculate emotional variability (standard deviation) for each user.
    
    Returns:
    - pd.DataFrame: Variability in Positive and Negative Probabilities.
    """
    variability = df.groupby('User')[['Positive_Prob', 'Negative_Prob']].std()
    print("Emotional Variability:\n", variability)
    return variability

