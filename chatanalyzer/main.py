import argparse
from chatanalyzer.sentiment_analysis import (
    analyze_sample_data,
    batch_request_api,
    analyze_saved_results
)

def main():
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

    if args.mode == 'sample':
        analyze_sample_data('sample_data.csv', 'output.csv')
    elif args.mode == 'request':
        batch_request_api('full_data.csv', 'api_output.csv')
    elif args.mode == 'analyze':
        analyze_saved_results('api_output.csv', 'final_analysis.csv')
    else:
        print("Invalid mode. Please choose 'sample', 'request', or 'analyze'.")

if __name__ == "__main__":
    main()
