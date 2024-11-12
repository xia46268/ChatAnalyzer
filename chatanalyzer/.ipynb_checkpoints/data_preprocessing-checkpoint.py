import pandas as pd
import re

def load_and_preprocess_data(file_path):
    """
    Load and preprocess chat data from a CSV file.

    Parameters:
    - file_path (str): Path to the CSV file containing chat data.

    Returns:
    - pd.DataFrame: Preprocessed DataFrame with relevant columns.
    """
    # 读取CSV文件；read
    df = pd.read_csv(file_path)

    # 仅保留相关列；keep only relevant columns
    df = df[['StrContent', 'StrTime', 'Remark']]

    # 将 Remark 列重命名为 User；rename
    df.rename(columns={'Remark': 'User'}, inplace=True)

    # 填补缺失值；fill in missing values
    df['StrContent'].fillna('', inplace=True)

    # 解析表情包和图片；category Emoticons and pictures
    df['MessageType'] = df['StrContent'].apply(classify_message_type)

    # 确保时间格式正确；time format
    df['StrTime'] = pd.to_datetime(df['StrTime'], format='%Y-%m-%d %H:%M:%S')

    return df


def classify_message_type(content):
    """
    Classify the message type based on content.

    Parameters:
    - content (str): The message content.

    Returns:
    - str: Type of the message ('emoji', 'image', 'empty', 'other', or 'text').
    """
    # 匹配图片消息
    if re.search(r'<msg>\s*<img.*?>\s*</msg>', content, re.DOTALL):
        return 'image'  # 图片消息
    # 匹配表情包消息
    elif re.search(r'<msg>\s*<emoji.*?>.*?</msg>', content, re.DOTALL):
        return 'emoji'  # 表情包
    # 匹配空消息
    elif content.strip() == '':
        return 'empty'  # 空消息
    # 排除其他特殊消息
    elif re.search(r'<msg>.*?</msg>', content, re.DOTALL):
        return 'other'  # 其他消息
    else:
        return 'text'  # 纯文本消息
