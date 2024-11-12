import argparse
from chatanalyzer.auth import BaiduAuth
from chatanalyzer.sentiment_analysis import (
    analyze_sample_data,
    batch_request_api,
    analyze_saved_results
)

def main(mode):
    # Prompt the user for API credentials if required
    if mode in ["request", "analyze"]:
        api_key = input("Enter your Baidu API Key: ").strip()
        secret_key = input("Enter your Baidu Secret Key: ").strip()
        
        # Initialize BaiduAuth and get access token
        auth_client = BaiduAuth(api_key, secret_key)
        auth_client.load_or_generate_access_token()

    # 修改下面路径file_path以进行 小样本分析 ，默认记录数量sample_size=100
    # Modify the following path file_path for small sample analysis. The default number of records sample_size=100
    # python3 main.py sample
    if mode == 'sample':
        file_path = "path_to_your_sample_chat_data.csv"
        output_path = "sentiment_analysis_sample_results.csv"
        analyze_sample_data(file_path, output_path)

    # 修改下面路径chat_data_path以进行 全样本分析
    # Modify the following path chat_data_path for full sample analysis
    # python3 main.py request
    elif mode == 'request':
        chat_data_path = "path_to_your_full_chat_data.csv"
        api_output_path = "sentiment_api_results.csv"
        batch_request_api(chat_data_path, api_output_path, batch_size=100)
    
    # 修改下面路径api_output_path以进行 API结果文本分析
    # Modify the following path api_output_path for text analysis of API results
    # python3 main.py analyze
    elif mode == 'analyze':
        api_output_path = "sentiment_api_results.csv"
        analysis_output_path = "sentiment_analysis_final.csv"
        analyze_saved_results(api_output_path, analysis_output_path)
    
    else:
        print("Invalid mode selected. Use 'sample', 'request', or 'analyze'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat Analyzer Main Script")
    parser.add_argument(
        "mode",
        type=str,
        choices=["sample", "request", "analyze"],
        help=(
            "Select 'sample' for small sample analysis, "
            "'request' for full dataset API requests, "
            "or 'analyze' for analysis of saved results."
        )
    )
    args = parser.parse_args()
    main(args.mode)
