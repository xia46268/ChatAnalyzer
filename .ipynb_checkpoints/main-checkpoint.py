from chatanalyzer.auth import BaiduAuth
from chatanalyzer.sentiment_analysis import analyze_sentiment

def main():
    # 初始化 BaiduAuth 实例
    auth_client = BaiduAuth()

    # 尝试加载 Access Token
    auth_client.load_access_token()

    # 如果 Token 无效或不存在，获取新的 Token
    if not auth_client.is_token_valid():
        print("Access token is invalid or not found. Fetching a new one...")
        auth_client.get_access_token()
        auth_client.save_access_token()

    # 使用 Access Token 调用情感分析
    text = "这个产品真的很好！"
    sentiment_result = analyze_sentiment(auth_client.access_token, text)
    
    # 打印情感分析结果
    print(f"Sentiment analysis result for text '{text}': {sentiment_result}")

if __name__ == "__main__":
    main()
