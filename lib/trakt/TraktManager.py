import requests
import xbmc
import xbmcgui
import time
from lib.log import log

class TraktManager:
    """
    This class handles interactions with the Trakt API to retrieve the user's watch history and watchlist.
    """
    BASE_URL = "https://api.trakt.tv"

    def __init__(self, client_id, access_token):
        self.client_id = client_id
        self.access_token = access_token
        log("TraktManager initialized.", xbmc.LOGINFO)

    def get_watch_history(self, since=None):
        """
        Retrieves the user's watch history from the Trakt API.
        Handles pagination to retrieve all pages of the watch history.
        Returns the watch history as a list of dictionaries.
        """
        url = f"{self.BASE_URL}/sync/history"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "trakt-api-version": "2",
            "trakt-api-key": self.client_id
        }
        params = {"page": 1, "limit": 100}
        if since:
            params["start_at"] = since
        watch_history = []
        while True:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                page_data = response.json()
                watch_history.extend(page_data)
                log(f"Page {params['page']} watch history retrieved.", xbmc.LOGINFO)
                log(f"Page {params['page']} data: {page_data}", xbmc.LOGDEBUG)
                if len(page_data) < 100:
                    break
                params["page"] += 1
            elif response.status_code == 429:
                log("Rate limit exceeded. Waiting for 5 minutes before retrying...", xbmc.LOGWARNING)
                xbmcgui.Dialog().notification("Trakt Manager", "Rate limit exceeded. Waiting for 5 minutes before retrying...", xbmcgui.NOTIFICATION_WARNING)
                time.sleep(300)  # Wait for 5 minutes
            else:
                log(f"Failed to retrieve watch history. Response: {response.text}", xbmc.LOGERROR)
                xbmcgui.Dialog().notification("Trakt Manager", "Failed to retrieve watch history", xbmcgui.NOTIFICATION_ERROR)
                return None
        return watch_history

    def get_watchlist(self, since=None):
        """
        Retrieves the user's watchlist from the Trakt API.
        Handles pagination to retrieve all pages of the watchlist.
        Returns the watchlist as a list of dictionaries.
        """
        url = f"{self.BASE_URL}/users/me/watchlist"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "trakt-api-version": "2",
            "trakt-api-key": self.client_id
        }
        params = {"page": 1, "limit": 100}
        if since:
            params["start_at"] = since
        watchlist = []
        while True:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                page_data = response.json()
                watchlist.extend(page_data)
                log(f"Page {params['page']} watchlist retrieved.", xbmc.LOGINFO)
                log(f"Page {params['page']} data: {page_data}", xbmc.LOGDEBUG)
                if len(page_data) < 100:
                    break
                params["page"] += 1
            elif response.status_code == 429:
                log("Rate limit exceeded. Waiting for 5 minutes before retrying...", xbmc.LOGWARNING)
                xbmcgui.Dialog().notification("Trakt Manager", "Rate limit exceeded. Waiting for 5 minutes before retrying...", xbmcgui.NOTIFICATION_WARNING)
                time.sleep(300)  # Wait for 5 minutes
            else:
                log(f"Failed to retrieve watchlist. Response: {response.text}", xbmc.LOGERROR)
                xbmcgui.Dialog().notification("Trakt Manager", "Failed to retrieve watchlist", xbmcgui.NOTIFICATION_ERROR)
                return None
        return watchlist
    
    def sync_account(self, db):
        """
        Sync Trakt watch history and watchlist with the local database.
        :param db: The Database object to store the synced data.
        """
        log("Syncing Trakt data...", xbmc.LOGINFO)

        # Sync Watch History
        latest_added_at = db.get_latest_added_at()
        watch_history = self.get_watch_history(since=latest_added_at)
        if watch_history:
            unique_shows = set()
            filtered_watch_history = []
            for item in watch_history:
                if item['type'] == 'movie':
                    title = item['movie']['title']
                elif item['type'] == 'episode':
                    title = item['show']['title']
                else:
                    continue
                if title not in unique_shows:
                    unique_shows.add(title)
                    filtered_watch_history.append((
                        item['id'],
                        'tv_show' if item['type'] == 'episode' else item['type'],
                        title,
                        item['watched_at']
                    ))
            db.insert_watch_history(filtered_watch_history)
            log(f"Filtered watch history: {filtered_watch_history}", xbmc.LOGDEBUG)

        # Sync Watchlist
        latest_added_at_watchlist = db.get_latest_added_at_watchlist()
        watchlist = self.get_watchlist(since=latest_added_at_watchlist)
        if watchlist:
            unique_shows = set()
            filtered_watchlist = []
            for item in watchlist:
                if item['type'] == 'movie':
                    title = item['movie']['title']
                elif item['type'] == 'episode':
                    title = item['show']['title']
                else:
                    continue
                if title not in unique_shows:
                    unique_shows.add(title)
                    filtered_watchlist.append((
                        item['id'],
                        'tv_show' if item['type'] == 'episode' else item['type'],
                        title,
                        item['listed_at']
                    ))
            db.insert_watchlist(filtered_watchlist)
            log(f"Filtered watchlist: {filtered_watchlist}", xbmc.LOGDEBUG)
    