import unittest
import pandas as pd
from chatanalyzer.sentiment_analysis import plot_sentiment_distribution, calculate_emotional_variability

class TestSentimentAnalysis(unittest.TestCase):

    def setUp(self):
        # 设置示例数据
        self.sample_data = pd.DataFrame({
            'Text': ['Test message 1', 'Test message 2', 'Test message 3'],
            'StrTime': ['2024-01-01 00:00:00', '2024-01-01 01:00:00', '2024-01-01 02:00:00'],
            'User': ['User1', 'User2', 'User1'],
            'MessageType': ['text', 'text', 'text'],
            'Sentiment': [2, 0, 1],
            'Positive_Prob': [0.95, 0.1, 0.7],
            'Negative_Prob': [0.05, 0.9, 0.3],
            'Confidence': [0.99, 0.85, 0.95]
        })

    def test_plot_sentiment_distribution(self):
        plot_sentiment_distribution(self.sample_data)
        import os
        self.assertTrue(os.path.exists("sentiment_distribution.png"))

    def test_calculate_emotional_variability(self):
        variability = calculate_emotional_variability(self.sample_data)
        expected_columns = ['Positive_Prob', 'Negative_Prob']
        self.assertTrue(all(col in variability.columns for col in expected_columns))
        self.assertEqual(len(variability), 2)

if __name__ == '__main__':
    unittest.main()
