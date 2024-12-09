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
    # Load CSV file
    df = pd.read_csv(file_path)

    # Check if 'Remark' column exists, if not, prompt a warning or try another name
    if 'Remark' not in df.columns:
        print("Warning: 'Remark' column not found, please check your CSV file columns.")
        # Example to handle a different column name, modify as necessary
        if 'Name' in df.columns:
            df = df.rename(columns={'Name': 'Remark'})

    # Keep only relevant columns
    df = df[['StrContent', 'StrTime', 'Remark']]

    # Rename Remark column to User
    df = df.rename(columns={'Remark': 'User'}) 

    # Fill in missing values
    df['StrContent'] = df['StrContent'].fillna('')

    # Parse message type (e.g., emoji, image)
    df['MessageType'] = df['StrContent'].apply(classify_message_type)

    # Ensure time format is correct
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
    # Match image messages
    if re.search(r'<msg>\s*<img.*?>\s*</msg>', content, re.DOTALL):
        return 'image'
    # Match emoji messages
    elif re.search(r'<msg>\s*<emoji.*?>.*?</msg>', content, re.DOTALL):
        return 'emoji'
    # Match empty messages
    elif content.strip() == '':
        return 'empty'
    # Match other types of messages
    elif re.search(r'<msg>.*?</msg>', content, re.DOTALL):
        return 'other'
    else:
        return 'text'

def append_csv_files(file1, file2, output_file):
    """
    Append the contents of file1 and file2 and save the result to output_file.
    """
    # Load the two CSV files
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Combine the two DataFrames
    combined_df = pd.concat([df1, df2], ignore_index=True)

    # Save to the new output file
    combined_df.to_csv(output_file, index=False)
    print(f"Files {file1} and {file2} have been combined and saved to {output_file}")