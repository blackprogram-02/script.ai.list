import requests
import xbmc
import xbmcgui
import time
from .ItemHandler import ItemHandler
from lib.log import log

class TMDBListManager():
    BASE_URL_4 = "https://api.themoviedb.org/4"
    BASE_URL_3 = "https://api.themoviedb.org/3"
    
    def __init__(self,api_key, access_token):
        self.api_key = api_key
        self.access_token = access_token
        # log("TMDBListManager initialized.", xbmc.LOGINFO)
        self.account_id = self.get_account_id()

    def get_account_id(self):
        url = f"{self.BASE_URL_3}/account"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        log(f"Requesting account ID with URL: {url}", xbmc.LOGDEBUG)
        response = requests.get(url, headers=headers)
        log(f"Account ID response: {response.text}", xbmc.LOGDEBUG)
        if response.status_code == 200:
            return response.json().get('id')
        else:
            log("Failed to retrieve account ID.", xbmc.LOGERROR)
            return None

    def create_list(self, name, description):
        url = f"{self.BASE_URL_4}/list"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "name": name,
            "description": description,
            "iso_639_1": "en"
        }
        log(f"Creating list with payload: {payload}", xbmc.LOGDEBUG)
        response = requests.post(url, headers=headers, json=payload)
        response_json = response.json()
        log(f"Create list response: {response_json}", xbmc.LOGDEBUG)
        if response.status_code == 201:
            log("List created successfully.", xbmc.LOGINFO)
            return response_json.get('id')
        else:
            log("Failed to create list.", xbmc.LOGERROR)
            return None
        
    def delete_list(self, list_id):
        url = f"{self.BASE_URL_3}/list/{list_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        log(f"Deleting list with ID: {list_id}", xbmc.LOGINFO)
        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            log(f"List {list_id} deleted successfully.", xbmc.LOGINFO)
        else:
            log(f"Failed to delete list {list_id}. Response: {response.text}", xbmc.LOGERROR)

    def rename_list(self, list_id, new_name):
        url = f"{self.BASE_URL_4}/list/{list_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {"name": new_name}
        log(f"Renaming list {list_id} to {new_name}.", xbmc.LOGINFO)
        response = requests.put(url, json=payload, headers=headers)
        log(f"Rename list response: {response.text}", xbmc.LOGDEBUG)
        if response.status_code == 200:
            log(f"List {list_id} renamed successfully.", xbmc.LOGINFO)
        else:
            log(f"Failed to rename list {list_id}.", xbmc.LOGERROR)

    def get_lists(self, list_id):
        url = f"{self.BASE_URL_4}/list/{list_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        log(f"Retrieving list with ID: {list_id}", xbmc.LOGINFO)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            log(f"List retrieved successfully: {response.json()}", xbmc.LOGDEBUG)
            return response.json()
        else:
            log(f"Failed to retrieve list {list_id}.", xbmc.LOGERROR)
            return None
        
    def find_list_by_name(self, list_name):
        if not self.account_id:
            log("Account ID not available.", xbmc.LOGERROR)
            return None
        url = f"{self.BASE_URL_3}/account/{self.api_key}/lists?page=1"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        log(f"Searching for list by name: {list_name}", xbmc.LOGINFO)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            lists = response.json().get('results', [])
            for lst in lists:
                if lst['name'].lower() == list_name.lower():
                    log(f"List found: {lst}", xbmc.LOGDEBUG)
                    return lst['id']
            log(f"List {list_name} does not exist.", xbmc.LOGINFO)
            return None
        else:
            log("Failed to retrieve lists.", xbmc.LOGERROR)
            return None
    
    def clear_list(self, list_id):
        url = f"{self.BASE_URL_3}/list/{list_id}/clear?confirm=true"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        log(f"Clearing list with ID: {list_id}", xbmc.LOGINFO)
        response = requests.post(url, headers=headers)
        log(f"Clear list response: {response.text}", xbmc.LOGDEBUG)
        if response.status_code == 201:
            log(f"List {list_id} cleared successfully.", xbmc.LOGINFO)
            return True
        else:
            log(f"Failed to clear list {list_id}.", xbmc.LOGERROR)
            return False

    def update_list_with_recommendations(self, list_name, list_id, description, recommendations, media_type):
        # list_id = self.find_list_by_name(list_name)
        if list_id:
            self.clear_list(list_id)
        else:
            list_id = self.create_list(list_name, description)
        
        if not list_id:
            log("Failed to create or find list.", xbmc.LOGERROR)
            return
        
        log(f"Updating list with ID: {list_id}", xbmc.LOGINFO)

        payload = {"items": []}
        INTERVAL = 1 / 40 # 40 requests per second for the TMDB API Limits
        for item in recommendations['recommendations']:
            item_id, item_type = ItemHandler(self.access_token).get_media_id(item['title'], media_type)
            log(f"Processing item: {item} - Item Type: {item_type}", xbmc.LOGDEBUG)
            if item_id is None:
                log(f"Failed to get media ID for {item['title']}", xbmc.LOGERROR)
                continue
            time.sleep(INTERVAL)
            payload["items"].append({"media_type": item_type, "media_id": item_id})

        log(f"Payload for updating list: {payload}", xbmc.LOGDEBUG)

        url = f"{self.BASE_URL_4}/list/{list_id}/items"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.access_token}"	
        }

        response = requests.post(url, headers=headers, json=payload)
        log(f"Update list response: {response.text}", xbmc.LOGDEBUG)
        if response.status_code == 1:
            log("List updated successfully.", xbmc.LOGINFO)
        else:
            log("Failed to update list.", xbmc.LOGERROR)