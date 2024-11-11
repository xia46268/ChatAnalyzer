import unittest
from chatanalyzer.auth import BaiduAuth

class TestBaiduAuth(unittest.TestCase):
    def setUp(self):
        self.invalid_api_key = "fake_api_key"
        self.invalid_secret_key = "fake_secret_key"
        self.auth_client_invalid = BaiduAuth(self.invalid_api_key, self.invalid_secret_key)

    def test_invalid_credentials(self):
        with self.assertRaises(ValueError) as context:
            self.auth_client_invalid.get_access_token()
        self.assertEqual(str(context.exception), "Failed to retrieve access token")

    def test_headers_without_token(self):
        with self.assertRaises(ValueError):
            self.auth_client_invalid.get_headers()

if __name__ == "__main__":
    unittest.main()
