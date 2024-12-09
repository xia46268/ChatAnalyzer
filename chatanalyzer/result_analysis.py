import pandas as pd
from chatanalyzer.data_preprocessing import append_csv_files
from chatanalyzer.visualization import (
    assign_colors,
    plot_sentiment_distribution,
    plot_monthly_message_distribution,
    plot_sentiment_trend,
    plot_active_hours_distribution,
    plot_sentiment_volatility,
    generate_word_cloud
)
from chatanalyzer.sentiment_utils import (
    calculate_sentiment_proportion,
    word_frequency_analysis,
    calculate_silence_breakers,
    calculate_emotional_variability, 
    get_first_chat_date,
    get_date_difference,
    get_peak_hour_activity,
    get_peak_month_activity,
    get_active_days_count,
    get_longest_silence,
    count_specific_word
)

# append_csv_files("api_output1.csv", "api_output2.csv", "api_output.csv")

def analyze_saved_results(input_path, analysis_output_path):
    """
    Analyze the results saved from API requests.
    """
    # Read input data and convert the time string to datetime format
    df = pd.read_csv(input_path)
    df['StrTime'] = pd.to_datetime(df['StrTime'])

    # 1. Output the chat summary
    # Get usernames of all participants
    users_list = ', '.join(map(str, df['User'].dropna().unique()))

    # Get information about the first and last chat
    first_chat_row = df.loc[df['StrTime'].idxmin()]
    last_chat_row = df.loc[df['StrTime'].idxmax()]
    print("————————————————————")
    print("Chat analysis for {}:".format(users_list))
    print(f"Date of the first chat: {first_chat_row['StrTime'].date()}")
    print(f"{first_chat_row['User']} said: \"{first_chat_row['Text']}\"")
    print(f"Date of the last chat: {last_chat_row['StrTime'].date()}")
    print(f"{last_chat_row['User']} said: \"{last_chat_row['Text']}\"")
    date_difference = get_date_difference(df)
    active_days = get_active_days_count(df)

    # Calculate the average number of messages per day
    avg_daily_messages = df.shape[0] / active_days
    print(f"On average, {avg_daily_messages:.2f} messages are exchanged per day.")

    # Peak activity analysis (hourly and monthly)
    peak_hour, peak_count, peak_percentage = get_peak_hour_activity(df)
    peak_month, peak_month_count, peak_month_percentage = get_peak_month_activity(df)
    max_silence, silence_breaker = get_longest_silence(df)
    silence_break_text = df.loc[df['Time_Diff'].idxmax(), 'Text']
    print(f"The longest silence lasted {max_silence:.2f} hours, broken by {silence_breaker} who said: \"{silence_break_text}\".")
    print("————————————————————")
    
    # Compare message counts and word counts between users
    total_message_count = df.shape[0]
    total_word_count = df['Text'].str.len().sum()
    print(f"A total of {total_message_count} messages were exchanged, containing {total_word_count} words.")

    # Statistics of each user's messages
    user_stats = df.groupby('User').agg(
        Message_Count=('Text', 'count'),
        Total_Words=('Text', lambda x: x.str.len().sum())
    )
    user_stats['Message_Percentage'] = user_stats['Message_Count'] / total_message_count * 100
    user_stats['Word_Percentage'] = user_stats['Total_Words'] / total_word_count * 100

    for user, stats in user_stats.iterrows():
        print(f"{user} sent {stats['Message_Count']} messages, accounting for {stats['Message_Percentage']:.2f}% of total messages.")
        print(f"{user} sent {stats['Total_Words']} words, accounting for {stats['Word_Percentage']:.2f}% of total words.")

    # Who is more active, and whose message timing is more random
    time_stats = df.groupby('User')['Time_Diff'].agg(['mean', 'var']).fillna(0)
    most_active_user = time_stats['mean'].idxmin()
    most_random_user = time_stats['var'].idxmax()
    print(f"{most_active_user} is more active with shorter average intervals.")
    print(f"{most_random_user}'s message timing is more random, making their messages unpredictable.")

    # Ice-breaker and vanisher analysis
    silence_break_stats = calculate_silence_breakers(df)
    num_freeze_periods = df[df['Time_Diff'] > 12].shape[0]
    print(f"There were {num_freeze_periods} instances of silence lasting over 12 hours.")
    if not silence_break_stats['breaker_ratio'].isna().all():
        print(f"{silence_break_stats['breaker_ratio'].idxmax()} is more likely to break the silence.")
    
    if not silence_break_stats['vanish_ratio'].isna().all():
        print(f"{silence_break_stats['vanish_ratio'].idxmax()} is more likely to suddenly vanish mid-conversation.")
    print("————————————————————")
    
    # Sentiment analysis
    sentiment_proportion = calculate_sentiment_proportion(df)
    most_positive_user = sentiment_proportion['Positive_Proportion'].idxmax()
    most_negative_user = sentiment_proportion['Negative_Proportion'].idxmax()
    print(f"It seems that {most_positive_user} is more positive, while {most_negative_user} tends to complain more during chats.")

    # Emotional variability
    variability = calculate_emotional_variability(df)
    most_variable_user = variability['Positive_Prob'].idxmax()
    print(f"{most_variable_user} shows the most emotional variability.")

    # Word frequency analysis
    word_counts = word_frequency_analysis(df)
    common_words = word_counts.most_common()
    print(f"The most frequently used word is \"{common_words[2][0]}\", appearing {common_words[2][1]} times.")
    print("Other commonly used words include:")
    for word, count in common_words[3:9]:
        print(f"\"{word}\", appearing {count} times.")

    # Analysis of the usage of "哈" or "ha"
    ha_counts = df['Text'].str.count('哈').sum()
    avg_ha_per_day = ha_counts / active_days
    print(f"A total of {ha_counts} instances of \"哈\" were exchanged, averaging {avg_ha_per_day:.2f} per day.")
    ha_counts_per_user = df.groupby('User')['Text'].apply(lambda x: x.str.count('哈').sum())
    for user, count in ha_counts_per_user.items():
        print(f"{user} said \"哈\" {count} times.")

    # User input word count functionality
    print("Try entering a word you want to count.")
    count_specific_word(df)

    print("————————————————————")
    print("\nBelow is the detailed data source:\n")

    # Visualization section (unchanged)
    user_colors = assign_colors(df)
    plot_sentiment_distribution(df, user_colors)
    plot_monthly_message_distribution(df, user_colors)
    plot_sentiment_trend(df, user_colors)
    plot_active_hours_distribution(df, user_colors)
    plot_sentiment_volatility(df, user_colors)

    generate_word_cloud(word_counts, output_path="word_cloud.png", colormap="viridis")

    # Print user message statistics
    print("\nUser Message Statistics (Text Only):\n", user_stats)
    print("————————————————————")

    # Print sentiment proportions
    print("\nSentiment Proportion by User (Relative to User's Message Count):\n", sentiment_proportion)
    print("————————————————————")

    # Print time interval statistics
    print("\nTime Interval Statistics:\n", time_stats)
    print("————————————————————")

    # Print ice-breaker and vanisher ratios
    print("\nIce-breaker Ratio:\n", silence_break_stats['breaker_ratio'])
    print("Vanisher Ratio:\n", silence_break_stats['vanish_ratio'])
    print("————————————————————")

    # Print emotional variability
    print("\nEmotional Variability:\n", variability)
    print("————————————————————")

    # Word frequency analysis and word cloud
    print("\nTop 50 Common Words:\n", word_counts.most_common(50))

if __name__ == "__main__":
    input_file = "api_output.csv"  # Input file path
    output_file = "final_analysis.csv"  # Output file path
    analyze_saved_results(input_file, output_file)