import requests
import xbmc
import xbmcgui
import xbmcvfs
import os

class AuthHandler:
    """
    This class handles the authentication process with The Movie Database (TMDb) API.
    It manages the creation and retrieval of request tokens, access tokens, and provides 
    mechanisms for user approval of authentication requests through a Kodi interface.
    
    Attributes:
        BASE_URL (str): The base URL for TMDb's authentication API.
        api_key (str): The API key used to authorize requests to the TMDb API.
        addon_path (str): The path where the Kodi add-on is located.
        ACCESS_FILE (str): The file path where the access token is stored locally.
        request_token (str): A temporary token used to request access to the TMDb API.
        access_token (str): A permanent token used to authenticate further API requests.

    Methods:
        __init__(self, api_key, addon_path):
            Initializes the `AuthHandler` class with the given API key and addon path.
        
        create_request_token(self):
            Creates a request token by making a request to TMDb's authentication API.
            Returns the request token if successful, otherwise shows an error message.
        
        create_approval(self):
            Directs the user to approve the authentication request on TMDb's website.
            The user will need to approve the request by visiting a shortened URL.
        
        shorten_url(self, long_url):
            Shortens a given URL using the TinyURL API.
            Returns the shortened URL.
        
        create_access_token(self):
            Converts the request token into an access token by making a request to TMDb's authentication API.
            The access token is saved to disk and can be used for further authenticated requests.
            Returns the access token if successful, otherwise shows an error message.
        
        load_access_token(self):
            Loads the access token from the local disk if it exists.
            Returns the access token or None if no access token is found.
    """
    BASE_URL = "https://api.themoviedb.org/3/authentication"
    def __init__(self, api_key, addon_path):
        self.api_key = api_key
        self.addon_path = addon_path
        self.ACCESS_FILE = os.path.join(addon_path, "tmdb_access_token.txt")

    def create_request_token(self):
        url = "https://api.themoviedb.org/4/auth/request_token"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        response = requests.post(url, headers=headers)
        response_json = response.json()
        if response.status_code == 200 and response_json.get('success'):
            xbmc.log(response_json.get('request_token'), xbmc.LOGINFO)
            self.request_token = response_json.get('request_token')
            return response_json.get('request_token')
        else:
            xbmcgui.Dialog().notification("TMDB Auth", "Failed to create request token", xbmcgui.NOTIFICATION_ERROR, 5000)
            return None

    def create_approval(self):
        url = f"https://www.themoviedb.org/auth/access?request_token={self.request_token}"
        short_url = self.shorten_url(url)
        dialog = xbmcgui.Dialog()
        dialog.ok("Approval Required", f"Please approve the request at {short_url}")
    
    def shorten_url(self, long_url):
        tinyurl_api = "http://tinyurl.com/api-create.php"
        response = requests.get(tinyurl_api, params={"url": long_url})
        if response.status_code == 200:
            return response.text
        else:
            return long_url

    def create_access_token(self):
        url = "https://api.themoviedb.org/4/auth/access_token"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "request_token": self.request_token
        }

        response = requests.post(url, headers=headers, json=payload)
        
        response_json = response.json()
        if response.status_code == 200 and response_json.get('success'):
            access_token = response_json.get('access_token')
            xbmc.log(access_token, xbmc.LOGINFO)
            self.access_token = access_token

            # Store access token to disk
            with open(self.ACCESS_FILE, 'w') as token_file:
                token_file.write(access_token)
                xbmc.log("Access token saved to disk", xbmc.LOGINFO)
                dialog = xbmcgui.Dialog()
                dialog.ok("TMDB Auth", "Access token created and saved successfully")
            return access_token
        else:
            dialog = xbmcgui.Dialog()
            dialog.ok("TMDB Auth", f"Failed to create access token")
            return None
    
    def load_access_token(self):
        if os.path.exists(self.ACCESS_FILE):
            with open(self.ACCESS_FILE, 'r') as token_file:
                return token_file.read()
        return None