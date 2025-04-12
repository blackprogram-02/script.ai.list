import requests
import xbmc
import xbmcgui
import xbmcvfs
import xbmcaddon
import os
import urllib.parse
from lib.gui.QRWindow import MyQRCodeWindow
from lib.gui.OKWindow import MyOkWindow

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
        self.addon = xbmcaddon.Addon()

        self.addon_install_path = self.addon.getAddonInfo('path')
        self.addon_profile_path = xbmcvfs.translatePath(self.addon.getAddonInfo('profile'))

        # Calculate the expected XML file path
        self.xml_file = os.path.join(self.addon_install_path, 'resources', 'skins', 'default', '1080i', 'MyQRCodeWindow.xml')
        self.ACCESS_FILE = os.path.join(self.addon_profile_path, "tmdb_access_token.txt")

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
            window = MyOkWindow("MyOkWindow.xml", self.addon_install_path, "default", "1080i",
                    display_title="Error TMDB",
                    message=f"Failed to create request token. \n\n" + str(response_json.get('status_message'))
                    )
            window.doModal()
            del window
            return None

    def create_approval(self):
        """
        Generates TMDB approval URL, a QR code URL for it,
        and displays them in a custom Kodi window.
        """
        # 1. Construct the original approval URL
        url = f"https://www.themoviedb.org/auth/access?request_token={self.request_token}"

        # 2. Generate the QR code image URL
        encoded_approval_url = urllib.parse.quote(url)
        qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={encoded_approval_url}"

        # 3. Shorten the original URL for text display
        short_display_url = self.shorten_url(url)

        # 4. Display using the custom QRwindow
        window = MyQRCodeWindow("MyQRCodeWindow.xml", self.addon_install_path, "default", "1080i",
                                qr_code_url=qr_code_url,
                                display_url=short_display_url,
                                display_title="TMDB Approval Required"
                                )
        window.doModal()
        del window
    
    def shorten_url(self, long_url):
        tinyurl_api = "http://tinyurl.com/api-create.php"
        try:
            response = requests.get(tinyurl_api, params={"url": long_url}, timeout=10) # Added timeout
            if response.status_code == 200:
                return response.text
            else:
                xbmc.log(f"[AuthHandler] TinyURL request failed: {response.status_code}", level=xbmc.LOGWARNING)
                return long_url
        except requests.exceptions.RequestException as e:
            xbmc.log(f"[AuthHandler] TinyURL request exception: {e}", level=xbmc.LOGWARNING)
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
                window = MyOkWindow("MyOkWindow.xml", self.addon_install_path, "default", "1080i",
                    display_title="Succefully Linked TMDB",
                    message="Your TMDB Acoount has been linked to the addon!"
                    )
                window.doModal()
                del window
            return access_token
        else:
            window = MyOkWindow("MyOkWindow.xml", self.addon_install_path, "default", "1080i",
                                display_title="Failed linking TMDB",
                                message=f"Something went wrong. Please try again. \n\n" + str(response_json.get('status_message'))
                                )
            window.doModal()
            del window
            return None
    
    def load_access_token(self):
        if os.path.exists(self.ACCESS_FILE):
            with open(self.ACCESS_FILE, 'r') as token_file:
                return token_file.read()
        return None