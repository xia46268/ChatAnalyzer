import unittest
from unittest.mock import patch
import pandas as pd
import os
from collections import Counter
from chatanalyzer.sentiment_analysis import (
    calculate_emotional_variability, 
    word_frequency_analysis, 
    specific_word_stats,
    calculate_silence_breakers,
    calculate_sentiment_proportion
)
from chatanalyzer.visualization import generate_word_cloud

class TestSentimentAnalysis(unittest.TestCase):

    def setUp(self):
        # 设置示例数据
        self.sample_data = pd.DataFrame({
            'Text': ['Test message 1', '哈哈哈 Test message 2', 'Test message 3 哈哈'],
            'StrTime': ['2024-01-01 00:00:00', '2024-01-01 01:00:00', '2024-01-01 02:00:00'],
            'User': ['User1', 'User2', 'User1'],
            'MessageType': ['text', 'text', 'text'],
            'Sentiment': [2, 0, 1],
            'Positive_Prob': [0.95, 0.1, 0.7],
            'Negative_Prob': [0.05, 0.9, 0.3],
            'Confidence': [0.99, 0.85, 0.95]
        })
        
        self.word_counts = Counter({'哈哈': 2, 'Test': 3, 'message': 3})

    def test_calculate_emotional_variability(self):
        variability = calculate_emotional_variability(self.sample_data)
        expected_columns = ['Positive_Prob', 'Negative_Prob']
        self.assertTrue(all(col in variability.columns for col in expected_columns))
        self.assertEqual(len(variability), 2)

    def test_word_frequency_analysis(self):
        with patch('builtins.input', return_value='哈哈哈'):  # 模拟用户输入
            word_counts = word_frequency_analysis(self.sample_data)
            self.assertGreater(len(word_counts), 0)

    def test_specific_word_stats(self):
        # 验证特定词 "哈哈" 的统计
        specific_word_stats(self.sample_data, word="哈哈")
        specific_word_stats(self.sample_data, word="Test")

    def test_generate_word_cloud(self):
        generate_word_cloud(self.word_counts, output_path="test_word_cloud.png", colormap="plasma")
        self.assertTrue(os.path.exists("test_word_cloud.png"))
        os.remove("test_word_cloud.png")

    def test_calculate_sentiment_proportion(self):
        sentiment_proportion = calculate_sentiment_proportion(self.sample_data)
        self.assertTrue('Positive_Proportion' in sentiment_proportion.columns)
        self.assertAlmostEqual(sentiment_proportion.loc['User1', 'Positive_Proportion'], 0.5, places=2)

    def test_calculate_silence_breakers(self):
        self.sample_data['StrTime'] = pd.to_datetime(self.sample_data['StrTime'])
        self.sample_data['Time_Diff'] = self.sample_data.groupby('User')['StrTime'].diff().dt.total_seconds().div(60)
        silence_stats = calculate_silence_breakers(self.sample_data)
        self.assertIn('breaker_ratio', silence_stats)
        self.assertIn('vanish_ratio', silence_stats)

if __name__ == '__main__':
    unittest.main()
