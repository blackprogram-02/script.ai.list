import os
import json
import xbmc
import xbmcgui
import xbmcaddon
from lib.ai_recomender.providers.gemini import GeminiProvider
from lib.ai_recomender.promts.recommendation import RecommendationPrompt
from lib.trakt.database import Database

from lib.ai_recomender.TMDB.ListManager import TMDBListManager
from lib.log import log
import time

class ListHandler:
    def __init__(self, addon_path, tmdb_api_key, token):
        self.tmdb_api_key = tmdb_api_key
        self.lists_file = os.path.join(addon_path, "list.json")
        self.addon_path = addon_path
        self.addon = xbmcaddon.Addon()
        self.lists = self.load_lists()
        self.gemini = GeminiProvider()
        self.user_data = {}
        self.db = Database(os.path.join(addon_path, 'user_info.db'))
        self.tmdb_token = token
        log("ListHandler initialized.", xbmc.LOGINFO)
    
    def load_lists(self):
        """Load lists from the JSON file."""
        if os.path.exists(self.lists_file):
            with open(self.lists_file, 'r') as file:
                log(f"Loading lists from {self.lists_file}", xbmc.LOGINFO)
                lists = json.load(file).get('lists', {})
                log(f"Loaded lists: {lists}", xbmc.LOGDEBUG)
                return lists
        return {}
    
    def save_lists(self):
        """Save the current state of lists to the JSON file."""
        with open(self.lists_file, 'w') as file:
            json.dump({'lists': self.lists}, file, indent=4)
            log(f"Lists saved to {self.lists_file}", xbmc.LOGINFO)

    def delete_list(self, list_name):
        """Delete a list by name."""
        if list_name in self.lists:
            del self.lists[list_name]
            self.save_lists()
            log(f"List {list_name} deleted.", xbmc.LOGINFO)
        else:
            log(f"List {list_name} not found.", xbmc.LOGERROR)

    def get_list(self, list_name):
        """Get a list by name."""
        list_data = self.lists.get(list_name)
        log(f"Retrieved list {list_name}: {list_data}", xbmc.LOGDEBUG)
        return list_data

    def fetch_user_data(self, attached_data):
        if 'watch_history' in attached_data:
            history_return_count = attached_data.get('watch_history', {}).get('item_count', 10)
            history = self.db.get_watch_history()[:history_return_count]
            self.user_data['watch_history'] = history
        elif 'watchlist' in attached_data:
            watchlist_return_count = attached_data.get('watchlist', {}).get('item_count', 10)
            watchlist = self.db.get_watchlist()[:watchlist_return_count]
            self.user_data['watchlist'] = watchlist
        else:
            log("Unknown attached data type.", xbmc.LOGERROR)

    def process_list(self, list_name):
        """Process a specific list based on its settings."""
        list_data = self.get_list(list_name)
        if not list_data:
            log(f"List {list_name} not found.", xbmc.LOGERROR)
            return
        
        if not list_data.get('enabled', True):
            log(f"List {list_name} is disabled.", xbmc.LOGINFO)
            return
        
        list_setting = list_data.get('list_setting', {})
        list_type = list_setting.get('list_type', 'combined')
        list_length = list_setting.get('list_length', 10)
        ai_promt = list_data.get('AI', {}).get('promt', '')
        user_defined_list_name = list_setting.get('list_name', '')
        if list_type == 'combined':
            self.list_type = 'multi'	# modify type file
        elif list_type == 'movie':
            self.list_type = 'movie'
        elif list_type == 'tvshow':
            self.list_type = 'tv'

        log(f"Processing list {list_name} with settings: {list_setting}", xbmc.LOGINFO)
        log(f"Attached data: {list_data.get('attacched_data', {})}", xbmc.LOGDEBUG)

        attacched_data = list_data.get('attacched_data', {})
        self.fetch_user_data(attacched_data)

        user_details = f"the user data: {self.user_data}"
        promt = RecommendationPrompt(user_list_name=user_defined_list_name, user_data=user_details, addition_promt=ai_promt, media_type=list_type, count=list_length)
        log(f"Generated prompt: {promt}", xbmc.LOGDEBUG)

        recommendations = self.gemini.query(str(promt))
        log(f"Gemini response: {recommendations}", xbmc.LOGDEBUG)
        
        try:
            recommendations = json.loads(recommendations)
        except Exception as e:
            log(f"Failed to parse recommendations: {str(e)}", xbmc.LOGERROR)
            return None, None, None
        
        return recommendations, list_data.get('list_setting', {}).get('list_description', ''), list_data.get('list_setting', {}).get('list_name', '')

    def get_list_id_by_name(self, list_name):
        """
        Retrieve the list ID by searching for the list name in the provided JSON data.

        :param json_data: The JSON data containing the lists.
        :param list_name: The name of the list to search for.
        :return: The list ID if found, otherwise None.
        """
        try:
            for list_id, list_data in self.lists.items():
                if list_data.get("list_setting", {}).get("list_name", "").lower() == list_name.lower():
                    log(f"List ID found for '{list_name}': {list_id}", xbmc.LOGINFO)
                    return list_id
            log(f"List name '{list_name}' not found in the JSON data.", xbmc.LOGINFO)
            return None
        except Exception as e:
            log(f"Error while searching for list ID: {str(e)}", xbmc.LOGERROR)
            return None
    
    def procces_all_lists(self):
        """Process all lists defined in the JSON file."""

        disable_notifications = self.addon.getSetting("Disable_Update_Notifications") == "true"

        # fetch_all()
        INTERVAL = 60 / 14 # 14 requests per minute for the Gemini Limits
        for list_name in self.lists.keys():
            time.sleep(INTERVAL)
            data, list_description, list_name = self.process_list(list_name)
            if data:
                user_list = TMDBListManager(self.tmdb_api_key, self.tmdb_token)
                list_id = self.get_list_id_by_name(list_name)
                user_list.update_list_with_recommendations(list_name, list_id, list_description, data, self.list_type)

                # Udpate list with genrated name
                genarted_name = data.get('list_name')
                user_list.rename_list(list_id,genarted_name)

                if not disable_notifications:
                    xbmcgui.Dialog().notification("Success", f"Successfully updated list {list_name}", xbmcgui.NOTIFICATION_INFO)
                log(f"Successfully updated list {list_name} with recommendations.", xbmc.LOGINFO)
            else:
                xbmcgui.Dialog().notification("Error", f"Failed to process list {list_name}", xbmcgui.NOTIFICATION_ERROR)
                log(f"Failed to process list {list_name}.", xbmc.LOGERROR)