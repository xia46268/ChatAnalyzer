import os
import pandas as pd
from tqdm import tqdm
from chatanalyzer.auth import BaiduAuth
from chatanalyzer.data_preprocessing import load_and_preprocess_data
from chatanalyzer.sentiment_utils import analyze_sentiment

def batch_request_api(file_path, output_path, batch_size=100):
    """
    Perform sentiment analysis via API in batches and save intermediate results.
    This function supports incremental updates, meaning it only processes new data added to the chat logs.
    """
    # Load and preprocess the full data file
    df = load_and_preprocess_data(file_path)
    df = df[df['MessageType'] == 'text']  # Filter only text messages

    # Check if output file already exists to determine if incremental update is needed
    if os.path.exists(output_path):
        # Load previously processed data
        processed_df = pd.read_csv(output_path)
        # Create a set of processed unique identifiers (combination of StrTime and User)
        processed_ids = set(processed_df['StrTime'] + processed_df['User'])
    else:
        # If no previous output exists, create an empty set for processed ids
        processed_ids = set()

    # Initialize Baidu API authentication
    auth_client = BaiduAuth()
    auth_client.load_access_token()
    if not auth_client.is_token_valid():
        auth_client.get_access_token()
        auth_client.save_access_token()

    # Process data in batches, skipping records that have already been processed
    for i in tqdm(range(0, len(df), batch_size), desc="Requesting Sentiment Analysis"):
        batch = df.iloc[i:i + batch_size]
        # Filter out rows that have already been processed
        batch = batch[~((batch['StrTime'].dt.strftime('%Y-%m-%d %H:%M:%S') + batch['User']).isin(processed_ids))]

        # Prepare list to hold new results
        results = []
        for _, row in batch.iterrows():
            # Perform sentiment analysis on each row using Baidu NLP API
            sentiment_result = analyze_sentiment(auth_client.access_token, row['StrContent'], retries=5, timeout=15)
            if sentiment_result:
                # Append the sentiment analysis result to the results list
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

        # If there are new results, append them to the output file
        if results:
            batch_results_df = pd.DataFrame(results)
            # Append to output CSV, write header only if the file does not exist
            batch_results_df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)
            # Update the processed_ids set with the new records
            processed_ids.update(batch['StrTime'].dt.strftime('%Y-%m-%d %H:%M:%S') + batch['User'])

            # Print a sample result for verification
            print("Sample Result:\n", batch_results_df.iloc[0])

    print("All new data processed and saved to", output_path)

if __name__ == "__main__":
    # Example usage
    batch_request_api('full_data.csv', 'api_output.csv', batch_size=100)

