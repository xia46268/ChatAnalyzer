import pandas as pd
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
    get_longest_silence
)

def analyze_saved_results(input_path, analysis_output_path):
    """
    Analyze the results saved from API requests.
    """
    df = pd.read_csv(input_path)
    df['StrTime'] = pd.to_datetime(df['StrTime'])

    # 1. 打印第一次聊天和时间差分析
    get_first_chat_date(df)
    get_date_difference(df)
    get_peak_hour_activity(df)
    get_peak_month_activity(df)
    get_active_days_count(df)
    get_longest_silence(df)

    # 2. 可视化
    user_colors = assign_colors(df)
    plot_sentiment_distribution(df, user_colors)
    plot_monthly_message_distribution(df, user_colors)
    plot_sentiment_trend(df, user_colors)
    plot_active_hours_distribution(df, user_colors)
    plot_sentiment_volatility(df, user_colors)

    # 3. 打印用户统计信息
    user_stats = df.groupby('User').agg(
        Message_Count=('Text', 'count'),
        Total_Words=('Text', lambda x: x.str.len().sum()),
        Avg_Words=('Text', lambda x: x.str.len().mean())
    )
    print("\nUser Message Statistics (Text Only):\n", user_stats)

    # 4. 打印情感比例
    sentiment_proportion = calculate_sentiment_proportion(df)
    print("\nSentiment Proportion by User (Relative to User's Message Count):\n", sentiment_proportion)

    # 5. 打印时间间隔统计
    df['Time_Diff'] = df.groupby('User')['StrTime'].diff().dt.total_seconds().div(60)
    time_stats = df.groupby('User')['Time_Diff'].agg(['mean', 'var']).fillna(0)
    print("\nTime Interval Statistics:\n", time_stats)

    # 6. 打印破冰者和消失者比例
    silence_break_stats = calculate_silence_breakers(df)
    print("\nIce-breaker Ratio:\n", silence_break_stats['breaker_ratio'])
    print("Vanisher Ratio:\n", silence_break_stats['vanish_ratio'])

    # 7. 打印情感波动
    variability = calculate_emotional_variability(df)
    print("\nEmotional Variability:\n", variability)

    # 8. 词频分析和词云
    word_counts = word_frequency_analysis(df)
    print("\nTop 50 Common Words:\n", word_counts.most_common(50))

    generate_word_cloud(word_counts, output_path="word_cloud.png", colormap="viridis")
