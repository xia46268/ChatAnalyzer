import os
import pandas as pd
from tqdm import tqdm
from chatanalyzer.auth import BaiduAuth
from chatanalyzer.data_preprocessing import load_and_preprocess_data
from chatanalyzer.sentiment_utils import analyze_sentiment

def batch_request_api(file_path, output_path, batch_size=100):
    """
    Perform sentiment analysis via API in batches and save intermediate results.
    """
    # Load and preprocess data
    df = load_and_preprocess_data(file_path)
    df = df[df['MessageType'] == 'text']  # Only process text messages

    # Initialize authentication
    auth_client = BaiduAuth()
    auth_client.load_access_token()
    if not auth_client.is_token_valid():
        auth_client.get_access_token()
        auth_client.save_access_token()

    results = []

    # Process data in batches and save intermediate results
    for i in tqdm(range(0, len(df), batch_size), desc="Requesting Sentiment Analysis"):
        batch = df.iloc[i:i + batch_size]

        batch_results = []

        # Perform sentiment analysis on each message
        for _, row in batch.iterrows():
            sentiment_result = analyze_sentiment(auth_client.access_token, row['StrContent'], retries=5, timeout=15)
            if sentiment_result:
                batch_results.append({
                    "Text": row['StrContent'],
                    "StrTime": row['StrTime'],
                    "User": row['User'],
                    "MessageType": row['MessageType'],
                    "Sentiment": sentiment_result.get('Sentiment', None),
                    "Confidence": sentiment_result.get('Confidence', 0.0),
                    "Positive_Prob": sentiment_result.get('Positive_Prob', 0.0),
                    "Negative_Prob": sentiment_result.get('Negative_Prob', 0.0),
                })

        if batch_results:
            results.extend(batch_results)
            # Print one result from every 100 records
            print(f"Batch {i//batch_size + 1} Completed. Sample Result:\n{batch_results[0]}")

            # Convert each batch's results to a DataFrame and save as a CSV file
            batch_df = pd.DataFrame(batch_results)
            if os.path.exists(output_path):
                batch_df.to_csv(output_path, mode='a', header=False, index=False)
            else:
                batch_df.to_csv(output_path, index=False)
            print(f"Batch {i//batch_size + 1} saved to {output_path}")

    # Save all results at the end
    if results:
        results_df = pd.DataFrame(results)
        results_df.to_csv(output_path, index=False)
        print(f"Analysis complete. Results saved to {output_path}")

if __name__ == "__main__":
    # Specify default file paths
    input_file = "full_data.csv"  
    output_file = "api_output.csv"  
    batch_request_api(input_file, output_file)