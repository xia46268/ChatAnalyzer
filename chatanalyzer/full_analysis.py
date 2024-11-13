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
    df = load_and_preprocess_data(file_path)
    df = df[df['MessageType'] == 'text']

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
