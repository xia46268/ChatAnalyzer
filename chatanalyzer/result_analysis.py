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

    # 获取首次和最后一次聊天的信息
    first_chat_row = df.loc[df['StrTime'].idxmin()]
    last_chat_row = df.loc[df['StrTime'].idxmax()]

    # 1. 输出聊天概述
    print("——————————————————————————")
    print("以下是对 {} 和 {} 的聊天记录分析：".format(first_chat_row['User'], last_chat_row['User']))
    print(f"第一次聊天的日期: {first_chat_row['StrTime'].date()}")
    print(f"{first_chat_row['User']} 说：“{first_chat_row['Text']}”")
    print(f"{last_chat_row['User']} 说：“{last_chat_row['Text']}”")
    print(f"最后一次聊天的日期: {last_chat_row['StrTime'].date()}")
    date_difference = get_date_difference(df)
    active_days = get_active_days_count(df)

    # 平均每天的消息数量
    avg_daily_messages = df.shape[0] / active_days
    print(f"平均一天互相发 {avg_daily_messages:.2f} 条消息")

    # 活跃时间段和月份分析
    peak_hour, peak_count, peak_percentage = get_peak_hour_activity(df)
    peak_month, peak_month_count, peak_month_percentage = get_peak_month_activity(df)
    max_silence, silence_breaker = get_longest_silence(df)
    silence_break_text = df.loc[df['Time_Diff'].idxmax(), 'Text']
    print(f"最久没聊天的时间间隔是 {max_silence:.2f} 小时，打破沉默的人是 {silence_breaker} 说：“{silence_break_text}”")

    # 消息数量和字数的对比
    total_message_count = df.shape[0]
    total_word_count = df['Text'].str.len().sum()
    print(f"你们一共互相发送了 {total_message_count} 条消息，共 {total_word_count} 个字")

    # 每个用户的消息统计
    user_stats = df.groupby('User').agg(
        Message_Count=('Text', 'count'),
        Total_Words=('Text', lambda x: x.str.len().sum())
    )
    user_stats['Message_Percentage'] = user_stats['Message_Count'] / total_message_count * 100
    user_stats['Word_Percentage'] = user_stats['Total_Words'] / total_word_count * 100

    for user, stats in user_stats.iterrows():
        print(f"{user} 发送了 {stats['Message_Count']} 条消息，占总消息的 {stats['Message_Percentage']:.2f}%")
        print(f"{user} 发送了 {stats['Total_Words']} 个字，占总字数的 {stats['Word_Percentage']:.2f}%")

    # 谁更活跃、谁发送较为随机、谁是破冰者和消失者
    time_stats = df.groupby('User')['Time_Diff'].agg(['mean', 'var']).fillna(0)
    most_active_user = time_stats['mean'].idxmin()
    most_random_user = time_stats['var'].idxmax()
    print(f"{most_active_user} 更活跃，平均时间间隔较短")
    print(f"{most_random_user} 的消息发送更随机，不知道ta的消息什么时候出现")

    silence_break_stats = calculate_silence_breakers(df)
    print(f"{silence_break_stats['breaker_ratio'].idxmax()} 更会突然出现，开启话题")
    print(f"{silence_break_stats['vanish_ratio'].idxmax()} 更会聊到一半突然消失")

    # 情绪分析
    sentiment_proportion = calculate_sentiment_proportion(df)
    most_positive_user = sentiment_proportion['Positive_Proportion'].idxmax()
    most_negative_user = sentiment_proportion['Negative_Proportion'].idxmax()
    print(f"看上去，可能 {most_positive_user} 的情绪更为积极")
    print(f"{most_negative_user} 更喜欢在聊天的时候吐槽")

    variability = calculate_emotional_variability(df)
    most_variable_user = variability['Positive_Prob'].idxmax()
    print(f"也有可能是因为 {most_variable_user} 的情绪波动更大")

    # 词频分析
    word_counts = word_frequency_analysis(df)
    common_words = word_counts.most_common()
    print(f"你们最喜欢说的词是（{common_words[6][0]}），共出现了 {common_words[6][1]} 次")
    print("其他也常被说起的是：")
    for word, count in common_words[7:16]:
        print(f"（{word}），共出现了 {count} 次")

    # "哈"的使用统计
    ha_counts = df['Text'].str.count('哈').sum()
    avg_ha_per_day = ha_counts / active_days
    print(f"你们一共互相发送了 {ha_counts} 个“哈”")
    print(f"平均一天要说 {avg_ha_per_day:.2f} 个")
    ha_counts_per_user = df.groupby('User')['Text'].apply(lambda x: x.str.count('哈').sum())
    for user, count in ha_counts_per_user.items():
        print(f"{user} 说了 {count} 个“哈”")

    # 继续输出详细的数据库来源
    print("——————————————————————————")
    print("\n下面是详细的数据库来源：\n")

    # 2. 可视化部分
    user_colors = assign_colors(df)
    plot_sentiment_distribution(df, user_colors)
    plot_monthly_message_distribution(df, user_colors)
    plot_sentiment_trend(df, user_colors)
    plot_active_hours_distribution(df, user_colors)
    plot_sentiment_volatility(df, user_colors)

    generate_word_cloud(word_counts, output_path="word_cloud.png", colormap="viridis")

    # 3. 打印用户统计信息
    print("\nUser Message Statistics (Text Only):\n", user_stats)

    # 4. 打印情感比例
    sentiment_proportion = calculate_sentiment_proportion(df)
    print("\nSentiment Proportion by User (Relative to User's Message Count):\n", sentiment_proportion)

    # 5. 打印时间间隔统计
    print("\nTime Interval Statistics:\n", time_stats)

    # 6. 打印破冰者和消失者比例
    print("\nIce-breaker Ratio:\n", silence_break_stats['breaker_ratio'])
    print("Vanisher Ratio:\n", silence_break_stats['vanish_ratio'])

    # 7. 打印情感波动
    print("\nEmotional Variability:\n", variability)

    # 8. 词频分析和词云
    print("\nTop 50 Common Words:\n", word_counts.most_common(50))

