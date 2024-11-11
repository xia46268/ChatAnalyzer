import pandas as pd
import random
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
from chatanalyzer.auth import BaiduAuth
from chatanalyzer.data_preprocessing import load_and_preprocess_data
from chatanalyzer.sentiment_analysis import (
    analyze_sentiment,
    plot_sentiment_distribution,
    calculate_emotional_variability
)



def analyze_sample_data(file_path, output_path, sample_size=100):
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
        if row['MessageType'] == 'text':  # 仅分析文本消息
            sentiment_result = analyze_sentiment(auth_client.access_token, content)
            if sentiment_result:
                sentiment_data = {
                    "Text": content,
                    "StrTime": row['StrTime'],
                    "User": row['Remark'],
                    "MessageType": row['MessageType'],  # 保留 MessageType 信息
                    "Sentiment": sentiment_result.get('sentiment'),
                    "Confidence": sentiment_result.get('confidence', 0.0),
                    "Positive_Prob": sentiment_result.get('positive_prob', 0.0),
                    "Negative_Prob": sentiment_result.get('negative_prob', 0.0)
                }
                results.append(sentiment_data)
        else:
            # 非文本消息记录但不分析
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

    # 统计用户消息数量、总字数、平均字数（仅文本消息）
    user_stats = result_df[result_df['MessageType'] == 'text'].groupby('User').agg(
        Message_Count=('Text', 'count'),
        Total_Words=('Text', lambda x: x.str.len().sum()),
        Avg_Words=('Text', lambda x: x.str.len().mean())
    )
    print("User Message Statistics (Text Only):\n", user_stats)

    # 统计情绪分布
    sentiment_counts = result_df['Sentiment'].value_counts()
    print("Statistical Distribution of Sentiment:\n", sentiment_counts)

    user_sentiment_avg = result_df.groupby('User')[['Positive_Prob', 'Negative_Prob']].mean()
    print("Mean User Emotional Rating:\n", user_sentiment_avg)

    result_df['Weighted_Positive'] = result_df['Positive_Prob'] * result_df['Confidence']
    result_df['Weighted_Negative'] = result_df['Negative_Prob'] * result_df['Confidence']
    user_weighted_sentiment = result_df.groupby('User')[['Weighted_Positive', 'Weighted_Negative']].mean()
    print("Mean User Weighted Emotional Rating:\n", user_weighted_sentiment)

    plot_active_hours_distribution(result_df)
    variability = calculate_emotional_variability(result_df)
    plot_sentiment_distribution(result_df)


def plot_active_hours_distribution(df):
    """
    Plot the active hours distribution for each user.
    """
    df['Hour'] = pd.to_datetime(df['StrTime']).dt.hour
    user_hourly_counts = df.groupby(['Hour', 'User']).size().unstack(fill_value=0)
    
    plt.figure(figsize=(10, 6))
    user_hourly_counts.plot(kind='bar', stacked=True, figsize=(12, 6), color=['#1f77b4', '#ff7f0e'])
    
    plt.xlabel('Hour of Day')
    plt.ylabel('Message Count')
    plt.title('Active Hours Distribution by User')
    plt.xticks(range(0, 24), rotation=0)
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.legend(title='User')
    plt.tight_layout()
    plt.savefig("active_hours_distribution.png")
    plt.show()

def main():
    file_path = "path_to_your_chat_data.csv"
    output_path = "sentiment_analysis_results.csv"
    analyze_sample_data(file_path, output_path)

if __name__ == "__main__":
    main()
