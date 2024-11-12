import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from itertools import cycle
from matplotlib.colors import to_hex
import matplotlib.cm as cm
from wordcloud import WordCloud

def assign_colors(df):
    """
    Assign a consistent color for each unique user in the dataset.

    Parameters:
    - df: DataFrame containing a 'User' column.

    Returns:
    - dict: A dictionary mapping users to unique colors.
    """
    unique_users = df['User'].unique()
    cmap = cm.get_cmap('tab10', len(unique_users))  # Use 'tab10' colormap for distinct colors
    colors = {user: to_hex(cmap(i)) for i, user in enumerate(unique_users)}
    return colors

def generate_word_cloud(word_counts, output_path="word_cloud.png", colormap='coolwarm'):
    """
    Generate and display a word cloud from word frequencies.

    Parameters:
    - word_counts: Dictionary of word frequencies.
    - output_path: Path to save the word cloud image.
    - colormap: Colormap for word cloud color scheme.
    """
    wordcloud = WordCloud(
        font_path="/System/Library/Fonts/STHeiti Light.ttc",  # 中文字体；Chinese
        width=800,
        height=400,
        background_color='white',
        colormap=colormap  
    ).generate_from_frequencies(word_counts)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title("Word Cloud of Chat Content", fontsize=14)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()


def plot_sentiment_trend(df, user_colors, output_path="sentiment_trend.png"):
    """
    Plot sentiment trends over time.
    """
    df['Date'] = pd.to_datetime(df['StrTime']).dt.date
    daily_sentiment = df.groupby(['Date', 'Sentiment']).size().unstack(fill_value=0)
    daily_sentiment = daily_sentiment.rename(columns={0: 'Negative', 1: 'Neutral', 2: 'Positive'})

    plt.figure(figsize=(12, 6))
    daily_sentiment.plot(kind='line', marker='o', figsize=(12, 6), color=['#d62728', '#1f77b4', '#2ca02c'])  # Fixed sentiment colors
    plt.title("Sentiment Trend Over Time", fontsize=14)
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Message Count", fontsize=12)
    plt.legend(title='Sentiment')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()

def plot_sentiment_volatility(df, user_colors, output_path="sentiment_volatility.png"):
    """
    Plot sentiment volatility by hour as a line plot.
    """
    df['Hour'] = pd.to_datetime(df['StrTime']).dt.hour
    hourly_sentiment = df.groupby(['Hour', 'Sentiment']).size().unstack(fill_value=0)
    hourly_sentiment = hourly_sentiment.rename(columns={0: 'Negative', 1: 'Neutral', 2: 'Positive'})

    plt.figure(figsize=(12, 6))
    hourly_sentiment.plot(kind='line', marker='o', linewidth=2, color=['#d62728', '#1f77b4', '#2ca02c'])  # Fixed sentiment colors
    plt.title("Sentiment Volatility by Hour", fontsize=14)
    plt.xlabel("Hour of Day", fontsize=12)
    plt.ylabel("Message Count", fontsize=12)
    plt.legend(title='Sentiment')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()

def plot_active_hours_distribution(df, user_colors, output_path="active_hours_distribution.png"):
    """
    Plot active hours distribution for each user.
    """
    df['Hour'] = pd.to_datetime(df['StrTime']).dt.hour
    user_hourly_counts = df.groupby(['Hour', 'User']).size().unstack(fill_value=0)

    plt.figure(figsize=(10, 6))
    user_hourly_counts.plot(kind='bar', stacked=True, color=[user_colors[user] for user in user_hourly_counts.columns])
    plt.xlabel('Hour of Day', fontsize=12)
    plt.ylabel('Message Count', fontsize=12)
    plt.title('Active Hours Distribution by User', fontsize=14)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()

def plot_monthly_message_distribution(df, user_colors, output_path="monthly_message_distribution.png"):
    """
    Plot monthly message distribution for each user.
    """
    df['Month'] = pd.to_datetime(df['StrTime']).dt.to_period('M')
    monthly_counts = df.groupby(['Month', 'User']).size().unstack(fill_value=0)

    plt.figure(figsize=(12, 6))
    monthly_counts.plot(kind='bar', stacked=True, color=[user_colors[user] for user in monthly_counts.columns])
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Message Count', fontsize=12)
    plt.title('Monthly Message Distribution by User', fontsize=14)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()

def plot_sentiment_distribution(df, user_colors, output_path="sentiment_distribution.png"):
    """
    Plot the sentiment distribution for each user.
    """
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='Sentiment', hue='User', palette=user_colors)
    plt.xlabel('Sentiment', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.title('Sentiment Distribution by User', fontsize=14)
    plt.legend(title='User')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()
