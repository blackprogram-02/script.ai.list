import requests
import xbmc
from lib.log import log

class ItemHandler:
    def __init__(self, access_token):
        """
        Initialize the ItemHandler class with the access token.
        """
        self.access_token = access_token
        # log("TMDB ItemHandler initialized.", xbmc.LOGINFO)

    def get_media_id(self, title, search_type):
        """
        Search for a media item by title and type (movie or tv) and return its ID and media type.

        Args:
            title (str): The title of the media item to search for.
            search_type (str): The type of media to search for (e.g., "movie" or "tv").

        Returns:
            tuple: A tuple containing the media ID and media type, or (None, None) if not found.
        """
        url = f"https://api.themoviedb.org/3/search/{search_type}?query={title}&include_adult=false&language=en-US&page=1"
        log(f"Searching for media with URL: {url}", xbmc.LOGDEBUG)

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

        try:
            response = requests.get(url, headers=headers)
            log(f"Search response status code: {response.status_code}", xbmc.LOGDEBUG)

            if response.status_code != 200:
                log(f"Failed to search for '{title}'. Status code: {response.status_code}", xbmc.LOGERROR)
                return None, None

            data = response.json()
            log(f"Search response data: {data}", xbmc.LOGDEBUG)

            if 'results' in data and len(data['results']) > 0:
                first_result = data['results'][0]
                if 'media_type' not in first_result:
                    first_result['media_type'] = search_type

                if 'id' in first_result and 'media_type' in first_result:
                    log(f"Found media: ID={first_result['id']}, Type={first_result['media_type']}", xbmc.LOGDEBUG)
                    return first_result['id'], first_result['media_type']
                else:
                    log(f"Missing 'id' or 'media_type' in the first result for '{title}'", xbmc.LOGERROR)
                    return None, None
            else:
                log(f"No results found for '{title}'", xbmc.LOGINFO)
                return None, None
            
        except requests.exceptions.RequestException as e:
            log(f"Request to TMDb failed: {str(e)}", xbmc.LOGERROR)
            return None, None
        except Exception as e:
            log(f"An unexpected error occurred: {str(e)}", xbmc.LOGERROR)
            return None, None