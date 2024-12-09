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
    # Load and preprocess data
    df = load_and_preprocess_data(file_path)
    df = df[df['MessageType'] == 'text']  # Only analyze text messages

    total_records = len(df)

    # Random sampling
    random_state = random.randint(1, 10000)
    print(f"Random State Used: {random_state}")
    sampled_df = df.sample(sample_size, random_state=random_state)

    # Get and check Baidu API access token
    auth_client = BaiduAuth()
    auth_client.load_access_token()
    if not auth_client.is_token_valid():
        auth_client.get_access_token()
        auth_client.save_access_token()

    access_token = auth_client.access_token
    results = []

    # Perform sentiment analysis row by row
    for _, row in tqdm(sampled_df.iterrows(), total=sampled_df.shape[0], desc="Analyzing Sentiment"):
        content = row['StrContent']
        if content.strip():  # Skip empty text
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
            # Handle empty text, save basic information directly
            results.append({
                "Text": content,
                "StrTime": row['StrTime'],
                "User": row['User'],
                "MessageType": row['MessageType'],
                "Sentiment": 1,  # Neutral sentiment
                "Confidence": 0.0,
                "Positive_Prob": 0.0,
                "Negative_Prob": 0.0
            })

    # Create a result DataFrame
    result_df = pd.DataFrame(results)

    # Output DataFrame info to check data
    print("Saving DataFrame to CSV:")
    print(result_df.info())

    # Save to CSV file
    result_df.to_csv(output_path, index=False)
    print(f"Analysis complete. Results saved to {output_path}")

    # Generate summary report
    generate_summary_report(result_df, total_records, sample_size)

def generate_summary_report(df, total_records, sample_size):
    """
    Generate a textual summary of the analysis results.
    """
    unique_users = df['User'].nunique()
    records_per_user = df['User'].value_counts()
    avg_words_per_user = df.groupby('User')['Text'].apply(lambda x: x.str.len().mean())

    user_summary = df.groupby("User")[["Positive_Prob", "Negative_Prob"]].mean()

    # Ensure users are output in order (e.g., 'User1', 'User2')
    user_1 = records_per_user.index[0]
    user_2 = records_per_user.index[1]

    summary = f"""
    Successfully sampled {sample_size} messages out of {total_records} total chat records!

    '{user_1}' sent {records_per_user[user_1]} messages, with an average of {avg_words_per_user[user_1]:.2f} characters per message.
    '{user_2}' sent {records_per_user[user_2]} messages, with an average of {avg_words_per_user[user_2]:.2f} characters per message.

    Based on sentiment analysis:
    '{user_1}' had an average positive sentiment score of {user_summary.loc[user_1, 'Positive_Prob']:.2f} and an average negative sentiment score of {user_summary.loc[user_1, 'Negative_Prob']:.2f}.
    '{user_2}' had an average positive sentiment score of {user_summary.loc[user_2, 'Positive_Prob']:.2f} and an average negative sentiment score of {user_summary.loc[user_2, 'Negative_Prob']:.2f}.
    """

    print(summary)

if __name__ == "__main__":
    input_file = "sample_data.csv"  # Input file path
    output_file = "output_sample.csv"  # Output file path
    analyze_sample_data(input_file, output_file)