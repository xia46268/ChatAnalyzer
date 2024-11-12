import unittest
from unittest.mock import patch, mock_open
from chatanalyzer.auth import BaiduAuth

class TestBaiduAuth(unittest.TestCase):
    def setUp(self):
        self.invalid_api_key = "fake_api_key"
        self.invalid_secret_key = "fake_secret_key"
        self.auth_client_invalid = BaiduAuth(self.invalid_api_key, self.invalid_secret_key)

    @patch('requests.post')
    def test_invalid_credentials(self, mock_post):
        # 模拟API返回错误
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {"error": "invalid_client"}

        with self.assertRaises(ValueError) as context:
            self.auth_client_invalid.get_access_token()
        self.assertIn("Failed to retrieve access token", str(context.exception))

    def test_headers_without_token(self):
        with self.assertRaises(ValueError, msg="Access token is not available. Please authenticate first."):
            self.auth_client_invalid.get_headers()

    @patch("builtins.open", new_callable=mock_open, read_data="mock_access_token")
    def test_load_access_token(self, mock_file):
        auth_client = BaiduAuth("api_key", "secret_key")
        auth_client.load_access_token("access_token.txt")
        self.assertEqual(auth_client.access_token, "mock_access_token")

    @patch("builtins.open", new_callable=mock_open)
    def test_save_access_token(self, mock_file):
        auth_client = BaiduAuth("api_key", "secret_key")
        auth_client.access_token = "new_mock_access_token"
        auth_client.save_access_token("access_token.txt")

        mock_file().write.assert_called_once_with("new_mock_access_token")

    @patch("chatanalyzer.auth.BaiduAuth.load_access_token")
    @patch("chatanalyzer.auth.BaiduAuth.get_access_token")
    @patch("chatanalyzer.auth.BaiduAuth.save_access_token")
    def test_load_or_generate_access_token(self, mock_save, mock_get, mock_load):
        mock_load.side_effect = FileNotFoundError  # 模拟文件不存在
        mock_get.return_value = "new_generated_token"

        auth_client = BaiduAuth("api_key", "secret_key")
        auth_client.load_or_generate_access_token()

        mock_get.assert_called_once()  # 应该调用 get_access_token
        mock_save.assert_called_once()  # 应该保存新的 token

if __name__ == "__main__":
    unittest.main()
