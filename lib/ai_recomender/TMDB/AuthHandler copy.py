import requests
import xbmc
import xbmcgui
import xbmcvfs

import os
from lib.log import log
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
    access_token = None

    def __init__(self, api_key, addon_path):
        self.api_key = api_key
        self.addon_path = addon_path
        self.ACCESS_FILE = os.path.join(addon_path, "tmdb_access_token.txt")
        # log("AuthHandler initialized.", xbmc.LOGINFO)

    def create_approval(self):
        """
        Direct the user to approve the authentication request on TMDb's website.
        """
        url = f"https://www.themoviedb.org/auth/access?request_token={self.request_token}"
        short_url = self.shorten_url(url)
        log(f"Approval URL: {url}", xbmc.LOGDEBUG)
        log(f"Shortened approval URL: {short_url}", xbmc.LOGDEBUG)

        dialog = xbmcgui.Dialog()
        dialog.ok("Approval Required", f"Please approve the request at {short_url}")
    
    def create_request_token(self):
        """
        Create a request token by making a request to TMDb's authentication API.
        Returns the request token if successful, otherwise shows an error message.
        """
        url = f"{self.BASE_URL}/token/new"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        log(f"Sending request to create request token with URL: {url}", xbmc.LOGDEBUG)

        response = requests.post(url, headers=headers)
        response_json = response.json()

        if response.status_code == 200 and response_json.get('success'):
            self.request_token = response_json.get('request_token')
            log(f"Request token created successfully: {self.request_token}", xbmc.LOGINFO)
            return self.request_token
        else:
            log(f"Failed to create request token. Response: {response_json}", xbmc.LOGERROR)
            dialog = xbmcgui.Dialog()
            dialog.ok("TMDB Auth", "Failed to create request token. Please try again.")
            return None
    # def create_approval(self):
    #     """
    #     Direct the user to approve the authentication request on TMDb's website.
    #     """
    #     url = f"https://www.themoviedb.org/auth/access?request_token={self.request_token}"
    #     short_url = self.shorten_url(url)
    #     log(f"Approval URL: {url}", xbmc.LOGDEBUG)
    #     log(f"Shortened approval URL: {short_url}", xbmc.LOGDEBUG)

    #     # Generate QR code
    #     qr_code_path = os.path.join(self.addon_path, "qr_code.png")
    #     qr = qrcode.QRCode(
    #         version=1,
    #         error_correction=qrcode.constants.ERROR_CORRECT_L,
    #         box_size=10,
    #         border=4,
    #     )
    #     qr.add_data(short_url)
    #     qr.make(fit=True)

    #     qr_image = qr.make_image(fill_color="black", back_color="white")
    #     qr_image.save(qr_code_path)
    #     log(f"QR code saved to: {qr_code_path}", xbmc.LOGINFO)

    #     # Display QR code in a dialog
    #     dialog = xbmcgui.Dialog()
    #     dialog.ok("Approval Required", f"Please approve the request by scanning the QR code or visiting: {short_url}")

    #     # Optionally, display the QR code as an image in Kodi
    #     if xbmcvfs.exists(qr_code_path):
    #         xbmc.executebuiltin(f'ShowPicture("{qr_code_path}")')
    
    def shorten_url(self, long_url):
        tinyurl_api = "http://tinyurl.com/api-create.php"
        log(f"Shortening URL: {long_url}", xbmc.LOGDEBUG)

        response = requests.get(tinyurl_api, params={"url": long_url})
        if response.status_code == 200:
            short_url = response.text
            log(f"Shortened URL: {short_url}", xbmc.LOGDEBUG)
            return short_url
        else:
            log(f"Failed to shorten URL. Returning original URL: {long_url}", xbmc.LOGWARNING)
            return long_url

    def create_access_token(self):
        """
        Convert the request token into an access token by making a request to TMDb's authentication API.
        """
        url = "https://api.themoviedb.org/4/auth/access_token"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "request_token": self.request_token
        }

        log(f"Sending request to create access token with URL: {url}", xbmc.LOGDEBUG)
        log(f"Payload: {payload}", xbmc.LOGDEBUG)

        response = requests.post(url, headers=headers, json=payload)
        
        response_json = response.json()
        if response.status_code == 200 and response_json.get('success'):
            access_token = response_json.get('access_token')
            self.access_token = access_token
            log(f"Access token created successfully: {access_token}", xbmc.LOGINFO)
            log(f"Full response: {response_json}", xbmc.LOGDEBUG)

            # Store access token to disk
            with open(self.ACCESS_FILE, 'w') as token_file:
                token_file.write(access_token)
                log("Access token saved to disk.", xbmc.LOGINFO)

            dialog = xbmcgui.Dialog()
            dialog.ok("TMDB Auth", "Access token created and saved successfully")
            return access_token
        else:
            log(f"Failed to create access token. Response: {response_json}", xbmc.LOGERROR)
            dialog = xbmcgui.Dialog()
            dialog.ok("TMDB Auth", f"Failed to create access token")
            return None
    
    def load_access_token(self):
        if AuthHandler.access_token is None:
            if os.path.exists(self.ACCESS_FILE):
                with open(self.ACCESS_FILE, 'r') as token_file:
                    access_token = token_file.read()
                    AuthHandler.access_token = access_token
                    log("Access token loaded from disk.", xbmc.LOGINFO)
                    log(f"Loaded access token: {access_token}", xbmc.LOGDEBUG)
                    return access_token
            else:
                log("Access token file not found.", xbmc.LOGWARNING)
        else:
            log("Access token already loaded in memory.", xbmc.LOGDEBUG)
        return AuthHandler.access_token
