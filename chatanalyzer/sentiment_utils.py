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
                return items[0] if items else {}
            else:
                print(f"Error {response.status_code}: {response.json()}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request error on attempt {attempt + 1}: {e}")
        
    return None

def calculate_emotional_variability(df):
    variability = df.groupby('User')[['Positive_Prob', 'Negative_Prob']].std().fillna(0)
    print("Emotional Variability:\n", variability)
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
    breaker_cou

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
    print(f"最久没聊天的时间间隔是 {max_silence:.2f} 小时，打破沉默的人是 {silence_breaker}")
    return max_silence, silence_breaker