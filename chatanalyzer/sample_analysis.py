import random
import pandas as pd
from tqdm import tqdm
from chatanalyzer.auth import BaiduAuth
from chatanalyzer.data_preprocessing import load_and_preprocess_data
from chatanalyzer.visualization import (
    assign_colors,
    plot_active_hours_distribution,
    plot_sentiment_distribution
)
from chatanalyzer.sentiment_utils import analyze_sentiment, calculate_emotional_variability

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

    user_colors = assign_colors(df)
    plot_active_hours_distribution(result_df, user_colors)
    plot_sentiment_distribution(result_df, user_colors)
    variability = calculate_emotional_variability(result_df)
    print("Emotional Variability:\n", variability)
