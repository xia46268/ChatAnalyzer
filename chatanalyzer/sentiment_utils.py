import requests
import jieba
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import pandas as pd

def analyze_sentiment(access_token, text, retries=3, timeout=10):
    """
    Analyze sentiment using Baidu's API.
    """
    if not text.strip():
        return None

    url = f"https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify?access_token={access_token}"
    headers = {"Content-Type": "application/json"}
    payload = {"text": text}

    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            if response.status_code == 200:
                response_json = response.json()
                items = response_json.get("items", [])
                if items:
                    return {
                        "Sentiment": items[0].get("sentiment", 1),  # Default neutral sentiment
                        "Confidence": items[0].get("confidence", 0.0),
                        "Positive_Prob": items[0].get("positive_prob", 0.0),
                        "Negative_Prob": items[0].get("negative_prob", 0.0),
                    }
                else:
                    return {"Sentiment": 1, "Confidence": 0.0, "Positive_Prob": 0.0, "Negative_Prob": 0.0}
            else:
                return {"Sentiment": 1, "Confidence": 0.0, "Positive_Prob": 0.0, "Negative_Prob": 0.0}

        except requests.exceptions.RequestException:
            continue

    return {"Sentiment": 1, "Confidence": 0.0, "Positive_Prob": 0.0, "Negative_Prob": 0.0}


def calculate_emotional_variability(df):
    """
    Calculate emotional variability for each user by calculating the standard deviation of sentiment scores.
    """
    # Ensure the data contains 'Positive_Prob' and 'Negative_Prob' columns
    if 'Positive_Prob' not in df.columns or 'Negative_Prob' not in df.columns:
        raise ValueError("The DataFrame must contain 'Positive_Prob' and 'Negative_Prob' columns.")

    # Group by user and calculate the standard deviation of positive and negative sentiments
    variability = df.groupby('User')[['Positive_Prob', 'Negative_Prob']].std()

    # Fill any missing values with 0 (e.g., if a user has only one record and cannot calculate std dev)
    variability = variability.fillna(0)

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
    """
    Calculate who breaks silences and who vanishes, based on message time intervals.
    """
    df['Time_Diff'] = df['StrTime'].diff().dt.total_seconds().div(3600).fillna(0)
    df['Is_Breaker'] = df['Time_Diff'] > 12  # Threshold for silence breaker: 12 hours
    df['Is_Vanisher'] = (df['Time_Diff'] > 1) & (~df['Is_Breaker'])  # Threshold for vanisher: 1 hour

    breaker_counts = df[df['Is_Breaker']].groupby('User').size()
    vanish_counts = df[df['Is_Vanisher']].groupby('User').size()
    total_counts = df.groupby('User').size()

    breaker_ratio = breaker_counts / total_counts
    vanish_ratio = vanish_counts / total_counts

    return {'breaker_ratio': breaker_ratio, 'vanish_ratio': vanish_ratio}

def get_first_chat_date(df):
    """
    Output the date of the first chat.
    """
    first_date = df['StrTime'].min().date()
    print(f"Date of the first chat: {first_date}")
    return first_date

def get_date_difference(df):
    """
    Calculate the time difference between the first and last chat dates.
    """
    first_date = df['StrTime'].min().date()
    last_date = df['StrTime'].max().date()
    difference = (last_date - first_date).days
    print(f"The time difference between the first and last chat dates is {difference} days.")
    return difference

def get_peak_hour_activity(df):
    """
    Output the hour of the day with the highest message frequency, the number of messages, and the percentage.
    """
    df['Hour'] = df['StrTime'].dt.hour
    peak_hour = df['Hour'].value_counts().idxmax()
    peak_count = df['Hour'].value_counts().max()
    total_messages = len(df)
    peak_percentage = (peak_count / total_messages) * 100
    print(f"The hour with the highest message frequency is {peak_hour}, with {peak_count} messages, accounting for {peak_percentage:.2f}%.")
    return peak_hour, peak_count, peak_percentage

def get_peak_month_activity(df):
    """
    Output the month with the highest message frequency, the number of messages, and the percentage.
    """
    df['Month'] = df['StrTime'].dt.to_period('M')
    peak_month = df['Month'].value_counts().idxmax()
    peak_month_count = df['Month'].value_counts().max()
    total_messages = len(df)
    peak_month_percentage = (peak_month_count / total_messages) * 100
    print(f"The month with the highest message frequency is {peak_month}, with {peak_month_count} messages, accounting for {peak_month_percentage:.2f}%.")
    return peak_month, peak_month_count, peak_month_percentage

def get_active_days_count(df):
    """
    Calculate the number of days with messages.
    """
    active_days = df['StrTime'].dt.date.nunique()
    print(f"There are {active_days} days with message records.")
    return active_days

def get_longest_silence(df):
    """
    Calculate the longest silence period and who broke the silence.
    """
    df['Time_Diff'] = df['StrTime'].diff().dt.total_seconds().div(3600).fillna(0)
    max_silence = df['Time_Diff'].max()
    silence_breaker = df.loc[df['Time_Diff'].idxmax(), 'User']
    return max_silence, silence_breaker

def count_specific_word(df):
    """
    Allow the user to input a word and count its total occurrence in the chat records.
    """
    word = input("Enter a word to count its frequency: ")
    total_occurrences = df['Text'].str.count(word).sum()
    occurrences_per_user = df.groupby('User')['Text'].apply(lambda x: x.str.count(word).sum())
    
    print(f"\nTotal occurrences of '{word}': {total_occurrences}")
    print(f"Occurrences of '{word}' by user:")
    print(occurrences_per_user)