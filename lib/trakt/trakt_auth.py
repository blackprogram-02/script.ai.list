import requests
import xbmc
import xbmcgui
import xbmcvfs
import os
from lib.log import log

class TraktAuthHandler:
    """
    This class handles the authentication process with Trakt API.
    It manages the creation and retrieval of access tokens and provides 
    mechanisms for user approval of authentication requests through a Kodi interface.
    
    Attributes:
        BASE_URL (str): The base URL for Trakt's authentication API.
        client_id (str): The client ID used to authorize requests to the Trakt API.
        client_secret (str): The client secret used to authorize requests to the Trakt API.
        addon_path (str): The path where the Kodi add-on is located.
        ACCESS_FILE (str): The file path where the access token is stored locally.
        access_token (str): A permanent token used to authenticate further API requests.

    Methods:
        __init__(self, client_id, client_secret, addon_path):
            Initializes the `TraktAuthHandler` class with the given client ID, client secret, and addon path.
        
        create_request_token(self):
            Creates a request token by making a request to Trakt's authentication API.
            Returns the request token if successful, otherwise shows an error message.
        
        create_approval(self):
            Directs the user to approve the authentication request on Trakt's website.
            The user will need to approve the request by visiting a shortened URL.
        
        create_access_token(self):
            Converts the request token into an access token by making a request to Trakt's authentication API.
            The access token is saved to disk and can be used for further authenticated requests.
            Returns the access token if successful, otherwise shows an error message.
        
        load_access_token(self):
            Loads the access token from the local disk if it exists.
            Returns the access token or None if no access token is found.
    """
    BASE_URL = "https://api.trakt.tv"
    access_token = None

    def __init__(self, client_id, client_secret, addon_path):
        self.client_id = client_id
        self.client_secret = client_secret
        self.addon_path = addon_path
        self.ACCESS_FILE = os.path.join(addon_path, "trakt_access_token.txt")

    def create_request_token(self):
        url = f"{self.BASE_URL}/oauth/device/code"
        payload = {
            "client_id": self.client_id
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers)
        response_json = response.json()
        if response.status_code == 200:
            self.device_code = response_json.get('device_code')
            self.user_code = response_json.get('user_code')
            self.verification_url = response_json.get('verification_url')
            log("Fetching watchlist.", level=xbmc.LOGINFO)
            log(f"Device Code: {self.device_code}, User Code: {self.user_code}, Verification URL: {self.verification_url}", xbmc.LOGDEBUG)
            return self.device_code
        else:
            xbmcgui.Dialog().notification("Trakt Auth", "Failed to create request token", xbmcgui.NOTIFICATION_ERROR, 5000)
            log(f"Failed to create request token. Response: {response.text}", xbmc.LOGERROR)
            return None

    def create_approval(self):
        dialog = xbmcgui.Dialog()
        dialog.ok("Approval Required", f"Please approve the request at {self.verification_url} and enter the code: {self.user_code}")
        log(f"Approval requested. Verification URL: {self.verification_url}, User Code: {self.user_code}", xbmc.LOGDEBUG)

    def create_access_token(self):
        url = f"{self.BASE_URL}/oauth/device/token"
        payload = {
            "code": self.device_code,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers)
        response_json = response.json()
        if response.status_code == 200:
            access_token = response_json.get('access_token')
            self.access_token = access_token
            log("Access token created successfully.", xbmc.LOGINFO)
            log(f"Access Token: {access_token}", xbmc.LOGDEBUG)

            # Store access token to disk
            with open(self.ACCESS_FILE, 'w') as token_file:
                token_file.write(access_token)
                log("Access token saved to disk.", xbmc.LOGINFO)
                dialog = xbmcgui.Dialog()
                dialog.ok("Trakt Auth", "Access token created and saved successfully")
            return access_token
        else:
            dialog = xbmcgui.Dialog()
            dialog.ok("Trakt Auth", f"Failed to create access token")
            log(f"Failed to create access token. Response: {response.text}", xbmc.LOGERROR)
            return None
    
    def load_access_token(self):
        if TraktAuthHandler.access_token is None:
            if os.path.exists(self.ACCESS_FILE):
                with open(self.ACCESS_FILE, 'r') as token_file:
                    access_token = token_file.read()
                    log("Access token loaded from disk.", xbmc.LOGINFO)
                    log(f"Loaded Access Token: {access_token}", xbmc.LOGDEBUG)
                    TraktAuthHandler.access_token = access_token
                    return access_token
            else:
                log("Access token file not found.", xbmc.LOGINFO)
        else:
            log("Access token already loaded in memory.", xbmc.LOGDEBUG)
        return None