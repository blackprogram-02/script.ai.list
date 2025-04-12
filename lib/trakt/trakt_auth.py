import requests
import xbmc
import xbmcgui
import xbmcvfs
import xbmcaddon
import os
import urllib.parse
from lib.log import log
from lib.gui.QRWindow import MyQRCodeWindow
from lib.gui.OKWindow import MyOkWindow

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
        self.addon = xbmcaddon.Addon()

        self.addon_install_path = self.addon.getAddonInfo('path')
        self.addon_profile_path = xbmcvfs.translatePath(self.addon.getAddonInfo('profile'))
        self.ACCESS_FILE = os.path.join(self.addon_profile_path, "trakt_access_token.txt")

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
            window = MyOkWindow("MyOkWindow.xml", self.addon_install_path, "default", "1080i",
                    display_title="Error Trakt",
                    message=f"Failed to create request token. \n\n" + str(response_json.get('status_message'))
                    )
            window.doModal()
            del window
            
            log(f"Failed to create request token. Response: {response.text}", xbmc.LOGERROR)
            return None

    def create_approval(self):
        # 1. Generate the QR code image URL
        encoded_approval_url = urllib.parse.quote(self.verification_url)
        qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={encoded_approval_url}"

        # 2. Display using the custom QRwindow
        window = MyQRCodeWindow("MyQRCodeWindow.xml", self.addon_install_path, "default", "1080i",
                        qr_code_url=qr_code_url,
                        display_url=str(self.verification_url + ' with code: ' + self.user_code),
                        display_title="Trakt Approval Required"
                        )
        window.doModal()
        del window
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
        if response:
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
                window = MyOkWindow("MyOkWindow.xml", self.addon_install_path, "default", "1080i",
                    display_title="Succefully Linked Trakt",
                    message="Your Trakt Acoount has been linked to the addon!\nAccess token has been saved successfully."
                    )
                window.doModal()
                del window
            return access_token
        else:
            window = MyOkWindow("MyOkWindow.xml", self.addon_install_path, "default", "1080i",
                                display_title="Failed linking Trakt",
                                message=f"Something went wrong. Please try again.\n\n Failed to create access token."
                                )
            window.doModal()
            del window
            
            log(f"Failed to create access token.", xbmc.LOGERROR)
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