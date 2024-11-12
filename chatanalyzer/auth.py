import requests

class BaiduAuth:
    """
    A class to handle authentication for Baidu API.
    """
    def __init__(self, api_key=None, secret_key=None):
        # 默认使用传入的API Key和Secret Key
        self.api_key = api_key or "f0KOyB3KSVCapiR2ObP5pLQB"
        self.secret_key = secret_key or "Ej4kcXt4ukkbfNJ5shqKMavqWD7xd24d"
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

        print("Request URL:", url)
        print("Request Params:", params)

        response = requests.post(url, params=params)

        print("Response Status Code:", response.status_code)
        print("Response Content:", response.json())

        if response.status_code == 200:
            self.access_token = response.json().get("access_token")
            print("New Access Token:", self.access_token)
            return self.access_token
        else:
            raise ValueError("Failed to retrieve access token")

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
            print(f"No access token file found at {file_path}. Please authenticate.")
        except Exception as e:
            print(f"Failed to load access token: {e}")

    def refresh_access_token(self, file_path="refresh_token.txt"):
        """Refresh the access token using the refresh token."""
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "refresh_token",
            "refresh_token": self.get_refresh_token(file_path),
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        
        response = requests.post(url, params=params)
        if response.status_code == 200:
            self.access_token = response.json().get("access_token")
            self.save_access_token()
            print("Access token refreshed successfully.")
        else:
            raise ValueError("Failed to refresh access token:", response.json())

    def save_refresh_token(self, refresh_token, file_path="refresh_token.txt"):
        """Save the refresh token to a file."""
        with open(file_path, "w") as file:
            file.write(refresh_token)
        print(f"Refresh token saved to {file_path}.")

    def get_refresh_token(self, file_path="refresh_token.txt"):
        """Load refresh token from a file."""
        try:
            with open(file_path, "r") as file:
                return file.read().strip()
        except FileNotFoundError:
            raise ValueError("No refresh token file found.")

    def is_token_valid(self):
        """
        Check if the current access token is valid.
        """
        return self.access_token is not None


# Example usage
if __name__ == "__main__":
    auth_client = BaiduAuth()
    token = auth_client.get_access_token()
    print(f"Access Token: {token}")
