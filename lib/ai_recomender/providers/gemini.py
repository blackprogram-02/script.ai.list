import requests
import xbmcaddon
import xbmc
import xbmcgui
import json
import re
from lib.ai_recomender.promts.recommendation import RecommendationPrompt
from lib.log import log

class GeminiProvider:
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        """
        Initialize the Gemini provider with the API key and model name.
        
        Args:
            model_name (str): The model name to be used (default: gemini-1.5-flash).
        """
        # Initialize addon
        addon = xbmcaddon.Addon()

        # Retrieve the API key from the Kodi settings
        self.api_key = addon.getSetting("gemini_api_key")

        # Check if API key is valid
        if not self.api_key:
            log("Gemini API key is missing or invalid in the settings.", xbmc.LOGERROR)#
            xbmcgui.Dialog().notification('Missing Gemini API key', 'Make sure to have filed in a valid gemini api key in the addon settings', xbmcgui.NOTIFICATION_INFO, 5000)
            return
        
        # Log the model name for debugging (avoid logging sensitive API key)
        self.model_name = model_name
        log(f"Using Gemini model: {self.model_name}", xbmc.LOGINFO)

    def validate_api_key(self) -> bool:
        """
        Validate the Gemini API key by sending a test request.
        
        Returns:
            bool: True if the API key is valid, False otherwise.
        """
        test_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": "Test"}]}]}

        try:
            response = requests.post(test_url, headers=headers, json=data)
            if response.status_code == 200:
                log("Gemini API key validated successfully.", xbmc.LOGINFO)
                return True
            else:
                log(f"Gemini API key validation failed: {response.status_code} - {response.text}", xbmc.LOGERROR)
                return False
        except requests.exceptions.RequestException as e:
            log(f"Gemini API key validation failed: {str(e)}", xbmc.LOGERROR)
            return False

    def query(self, prompt: RecommendationPrompt) -> str:
        """
        Send a query to the Gemini model using a formatted prompt.
        
        Args:
            prompt (str): The prompt to send to the model.
        
        Returns:
            str: The response text from the Gemini model.
        """
        # Ensure API key is available
        if not self.api_key:
            log("API key is missing or invalid.", xbmc.LOGERROR)
            return "API key is missing or invalid."

        # Setup headers for the request
        URL = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"

        formatted_prompt = str(prompt)
        log(f"Sending query to Gemini model with prompt: {formatted_prompt}", xbmc.LOGDEBUG)

        # Headers
        headers = {
            "Content-Type": "application/json",
        }

        # Data payload
        data = {
            "contents": [{
                "parts": [{"text": formatted_prompt}],
            }]
        }

        try:
            response = requests.post(URL, headers=headers, data=json.dumps(data))
            response.raise_for_status()  # Raise an exception for HTTP errors
            response_data = response.json()

            # Extract the response text
            text_response = response_data["candidates"][0]["content"]["parts"][0]["text"]
            log(f"Raw response from Gemini: {text_response}", xbmc.LOGDEBUG)

            # Extract JSON from the response
            json_match = re.search(r"```json\n(.*)\n```", text_response, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
                log(f"Extracted JSON from response: {json_text}", xbmc.LOGDEBUG)
                return json_text
            else:
                log("Failed to extract JSON from the Gemini response.", xbmc.LOGERROR)
                return "Failed to extract JSON from the response."

        except requests.exceptions.RequestException as e:
            log(f"Request to Gemini model failed: {str(e)}", xbmc.LOGERROR)
            return "Request failed. Check logs for details."
        except KeyError as e:
            log(f"Unexpected response structure: Missing key {str(e)}", xbmc.LOGERROR)
            return "Unexpected response structure. Check logs for details."
        except Exception as e:
            log(f"An unexpected error occurred: {str(e)}", xbmc.LOGERROR)
            return "An unexpected error occurred. Check logs for details."

