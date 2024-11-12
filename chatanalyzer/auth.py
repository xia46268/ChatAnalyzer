import requests

class BaiduAuth:
    """
    A class to handle authentication for Baidu API.
    """
    def __init__(self, api_key=None, secret_key=None):
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = None

    def get_access_token(self):
        """
        Fetch a new access token using API key and Secret key.
        """
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }

        response = requests.post(url, params=params)
        if response.status_code == 200:
            self.access_token = response.json().get("access_token")
            print("New Access Token generated successfully.")
            return self.access_token
        else:
            raise ValueError(f"Failed to retrieve access token: {response.json()}")

    def get_headers(self):
        """
        Return headers with the access token for API requests.
        """
        if not self.access_token:
            raise ValueError("Access token is not available. Please authenticate first.")
        return {"Content-Type": "application/json", "Authorization": f"Bearer {self.access_token}"}
    
    def save_access_token(self, file_path="access_token.txt"):
        """Save the current access token to a file."""
        if self.access_token:
            with open(file_path, "w") as file:
                file.write(self.access_token)
            print(f"Access token saved to {file_path}.")
        else:
            raise ValueError("No access token available to save.")

    def load_access_token(self, file_path="access_token.txt"):
        """Load access token from a file."""
        try:
            with open(file_path, "r") as file:
                self.access_token = file.read().strip()
            print(f"Access token loaded from {file_path}.")
        except FileNotFoundError:
            print(f"No access token file found at {file_path}.")
        except Exception as e:
            print(f"Failed to load access token: {e}")

    def is_token_valid(self):
        """
        Check if the current access token is valid.
        """
        return self.access_token is not None

    def load_or_generate_access_token(self, file_path="access_token.txt"):
        """
        Load the access token from a file or generate a new one if the file is not found.
        """
        try:
            self.load_access_token(file_path)
        except FileNotFoundError:
            print(f"{file_path} not found. Generating new access token.")
            self.get_access_token()
            self.save_access_token(file_path)
