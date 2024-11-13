import requests
import jieba
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import pandas as pd

def analyze_sentiment(access_token, text, retries=3, timeout=10):
    if not text.strip():
        return None
    url = f"https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify?access_token={access_token}"
    headers = {"Content-Type": "application/json"}
    payload = {"text": text}

    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            if response.status_code == 200:
                items = response.json().get("items", [])
                if items:
                    positive_prob = items[0].get("positive_prob", 0.0)
                    negative_prob = items[0].get("negative_prob", 0.0)
                    neutral_prob = items[0].get("neutral_prob", 0.0)
                    return {
                        "Positive_Prob": positive_prob,
                        "Negative_Prob": negative_prob,
                        "Neutral_Prob": neutral_prob,
                    }
                else:
                    return {"Positive_Prob": 0.0, "Negative_Prob": 0.0, "Neutral_Prob": 0.0}
            else:
                print(f"Error {response.status_code}: {response.json()}")
                return {"Positive_Prob": 0.0, "Negative_Prob": 0.0, "Neutral_Prob": 0.0}
        except requests.exceptions.RequestException as e:
            print(f"Request error on attempt {attempt + 1}: {e}")

    return {"Positive_Prob": 0.0, "Negative_Prob": 0.0, "Neutral_Prob": 0.0}


def calculate_emotional_variability(df):
    """
    Calculate emotional variability for each user by calculating the standard deviation of sentiment scores.
    通过计算情绪得分的标准差来计算每个用户的情绪波动。
    """
    # 确保数据包含 'Positive_Prob' 和 'Negative_Prob' 两列
    if 'Positive_Prob' not in df.columns or 'Negative_Prob' not in df.columns:
        raise ValueError("The DataFrame must contain 'Positive_Prob' and 'Negative_Prob' columns.")

    # 按用户分组，计算每个用户的正面和负面情绪的标准差
    variability = df.groupby('User')[['Positive_Prob', 'Negative_Prob']].std()

    # 用 0 填充任何可能的缺失值（例如某个用户只有一条数据，导致无法计算标准差）
    variability = variability.fillna(0)

    # 检查正负情绪的波动是否计算正确
    return variability


def calculate_sentiment_proportion(df):
    sentiment_counts = df.groupby('User')['Sentiment'].value_counts().unstack(fill_value=0)
    total_words = df.groupby('User')['Text'].apply(lambda x: x.str.len().count())
    sentiment_proportion = sentiment_counts.div(total_words, axis=0)
    sentiment_proportion.columns = ['Negative_Proportion', 'Neutral_Proportion', 'Positive_Proportion'][:len(sentiment_proportion.columns)]
    return sentiment_proportion

def word_frequency_analysis(df):
    all_text = ' '.join(df['Text'].dropna())
    words = [word for word in jieba.lcut(all_text) if len(word.strip()) > 1]
    word_counts = Counter(words)
    return word_counts

def calculate_silence_breakers(df):
    df['Is_破冰者'] = (df['Time_Diff'] > 720)
    df['Is_消失者'] = (df['Time_Diff'] > 60) & (~df['Is_破冰者'])
    breaker_counts = df[df['Is_破冰者']].groupby('User').size()
    vanish_counts = df[df['Is_消失者']].groupby('User').size()
    total_counts = df.groupby('User').size()
    # 使用 fillna(0) 防止 NaN
    breaker_ratio = (breaker_counts / total_counts).fillna(0)
    vanish_ratio = (vanish_counts / total_counts).fillna(0)
    return {'breaker_ratio': breaker_ratio, 'vanish_ratio': vanish_ratio}


def get_first_chat_date(df):
    """
    输出第一次聊天的日期。
    """
    first_date = df['StrTime'].min().date()
    print(f"第一次聊天的日期: {first_date}")
    return first_date

def get_date_difference(df):
    """
    计算距离第一次聊天的日期和最后一次聊天相隔的时间。
    """
    first_date = df['StrTime'].min().date()
    last_date = df['StrTime'].max().date()
    difference = (last_date - first_date).days
    print(f"距离第一次聊天的日期和最后一次聊天相隔了 {difference} 天")
    return difference

def get_peak_hour_activity(df):
    """
    输出在一天中哪个小时发消息频率最高，发了多少条，占比多少。
    """
    df['Hour'] = df['StrTime'].dt.hour
    peak_hour = df['Hour'].value_counts().idxmax()
    peak_count = df['Hour'].value_counts().max()
    total_messages = len(df)
    peak_percentage = (peak_count / total_messages) * 100
    print(f"在一天中 {peak_hour} 点发消息频率最高，共发了 {peak_count} 条，占比 {peak_percentage:.2f}%")
    return peak_hour, peak_count, peak_percentage

def get_peak_month_activity(df):
    """
    输出在哪个月发消息频率最高，发了多少条，占比多少。
    """
    df['Month'] = df['StrTime'].dt.to_period('M')
    peak_month = df['Month'].value_counts().idxmax()
    peak_month_count = df['Month'].value_counts().max()
    total_messages = len(df)
    peak_month_percentage = (peak_month_count / total_messages) * 100
    print(f"在 {peak_month} 月发消息频率最高，共发了 {peak_month_count} 条，占比 {peak_month_percentage:.2f}%")
    return peak_month, peak_month_count, peak_month_percentage

def get_active_days_count(df):
    """
    计算一共有多少天有消息记录。
    """
    active_days = df['StrTime'].dt.date.nunique()
    print(f"一共有 {active_days} 天有消息记录")
    return active_days

def get_longest_silence(df):
    """
    计算最久没聊天是隔了多久，谁是打破沉默的那个。
    """
    df['Time_Diff'] = df['StrTime'].diff().dt.total_seconds().div(3600).fillna(0)
    max_silence = df['Time_Diff'].max()
    silence_breaker = df.loc[df['Time_Diff'].idxmax(), 'User']
    return max_silence, silence_breaker

def count_specific_word(df):
    """
    Allow the user to input a word and count its total occurrence in the chat records.
    让用户输入一个词并统计它在聊天记录中的总出现次数。
    """
    word = input("Enter a word to count its frequency: ")
    total_occurrences = df['Text'].str.count(word).sum()
    occurrences_per_user = df.groupby('User')['Text'].apply(lambda x: x.str.count(word).sum())
    
    print(f"\nTotal occurrences of '{word}': {total_occurrences}")
    print(f"Occurrences of '{word}' by user:")
    print(occurrences_per_user)
