import sys
import xbmcaddon
import xbmcgui
import xbmcvfs
import xbmc
import os
from lib.log import log

from lib.trakt.trakt_auth import TraktAuthHandler
from lib.trakt.TraktManager import TraktManager

from lib.ai_recomender.TMDB.ListManager import TMDBListManager
from lib.ai_recomender.TMDB.AuthHandler import AuthHandler
from lib.ai_recomender.Lists.ListHandeler import ListHandler
from lib.ai_recomender.ListEditor.EditorGUI import EditorGUI
from lib.trakt.database import Database
from lib.ai_recomender.providers.gemini import GeminiProvider

addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
addon_path = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
db_path = os.path.join(addon_path, 'user_info.db')
try:
    db = Database(db_path)
except Exception as e:
    log("Cant find DB likly due to first time boot.", xbmc.LOGINFO)


API_KEY = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJkODNjNTZiY2FiMDAwYTAzYjRjYzViMjhiNjczMDVkYSIsIm5iZiI6MTcyMTEzODU2NC41NjgsInN1YiI6IjY2OTY3ZDg0ZDI2MzQ4YjNkM2RmN2ZmZiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.4nWGQX6ccWaxNMA0YuSfF3Wr_XPnPMjt590MHPJUlT4'
TRAKT_CLIENT_ID = "da630ca44b422f29a41fe341290f8259b9f62cf492d27411ec39b0b91e078f31"
TRAKT_CLIENT_SECRET = "5be457dcf7ddc6f34f1fe19b654d2247694cb9e646e1091d4b01c2072ccc20e0"

# Load the TMDB token
auth_handler = AuthHandler(API_KEY, addon_path)
tmdb_token = auth_handler.load_access_token()
tmd_user_list = TMDBListManager(API_KEY, tmdb_token) if tmdb_token else None

# Load the Trakt token
trakt_auth_handler = TraktAuthHandler(TRAKT_CLIENT_ID, TRAKT_CLIENT_SECRET, addon_path)
trakt_token = trakt_auth_handler.load_access_token()
if not trakt_token:
    trakt_token = trakt_auth_handler.load_access_token()
    if trakt_token:
        db.insert_user_info('trakt_token', trakt_token)
trakt_manager = TraktManager(TRAKT_CLIENT_ID, trakt_token) if trakt_token else None


def link_trakt_account():
    """Handle Trakt account linking."""
    trakt_auth_handler.create_request_token()
    trakt_auth_handler.create_approval()
    trakt_token = trakt_auth_handler.create_access_token()
    if trakt_token:
        db.insert_user_info('trakt_token', trakt_token)
        log("Trakt account linked successfully.", xbmc.LOGINFO)
    else:
        log("Failed to link Trakt account.", xbmc.LOGERROR)

def link_tmdb_account():
    """Handle TMDB account linking."""
    auth_handler = AuthHandler(API_KEY, addon_path)
    auth_handler.create_request_token()
    auth_handler.create_approval()
    tmdb_token = auth_handler.create_access_token()
    if tmdb_token:
        db.insert_user_info('tmdb_token', tmdb_token)
        log("TMDB account linked successfully.")
    else:
        log("Failed to link TMDB account.", xbmc.LOGERROR)


lock_file = os.path.join(addon_path, "update.lock")
def update_all_lists():
    """Update all lists."""
    if not trakt_token:
        xbmcgui.Dialog().notification(addonname, "Trakt account not linked. Please link your Trakt account first.", xbmcgui.NOTIFICATION_INFO)
        log("Failed to update lists: Trakt account not linked.", xbmc.LOGERROR)
        return

    # Check if TMDB account is linked
    if not tmdb_token:
        xbmcgui.Dialog().notification(addonname, "TMDB account not linked. Please link your TMDB account first.", xbmcgui.NOTIFICATION_INFO)
        log("Failed to update lists: TMDB account not linked.", xbmc.LOGERROR)
        return

    # Validate Gemini API key
    gemini_provider = GeminiProvider()  # Initialize the provider
    if not gemini_provider.validate_api_key():
        xbmcgui.Dialog().notification(addonname, "Invalid Gemini API key. Please check your settings.", xbmcgui.NOTIFICATION_INFO)
        log("Failed to update lists: Invalid Gemini API key.", xbmc.LOGERROR)
        return


    if os.path.exists(lock_file):
        # Show an OK popup to inform the user about the ongoing update
        xbmcgui.Dialog().ok(
            "Update in Progress",
            "The lists are already being updated. Please wait for the current update to finish before starting a new one."
        )
        log("Update skipped: Another update is already in progress.", xbmc.LOGWARNING)
        return

    # Create the lock file to indicate the update is in progress
    with open(lock_file, "w") as f:
        f.write("Updating")

    if not addon.getSetting("Disable_Update_Notifications") == "true":
        xbmcgui.Dialog().notification(addonname, "Start updating all lists", xbmcgui.NOTIFICATION_INFO)

    if xbmc.getCondVisibility("Window.IsActive(addonsettings)"):
        xbmcgui.Dialog().ok('Updating List', 'The lists are being updated. Based on your list count, this may take a couple of minutes.')

    try:
        log("Updating all lists...", xbmc.LOGINFO)
        sync_trakt_account()
        ListHandler(addon_path, API_KEY, tmdb_token).procces_all_lists()
        if not addon.getSetting("Disable_Update_Notifications") == "true":
            xbmcgui.Dialog().notification(addonname, "All lists updated successfully.", xbmcgui.NOTIFICATION_INFO)
        log("All lists updated successfully.", xbmc.LOGINFO)
    except Exception as e:
        xbmcgui.Dialog().notification(addonname, "Failed to update lists.", xbmcgui.NOTIFICATION_ERROR)
        log(f"Failed to update lists: {str(e)}", xbmc.LOGERROR)
    finally:
        # Remove the lock file after the update is complete
        if os.path.exists(lock_file):
            os.remove(lock_file)

def sync_trakt_account():
    """Sync Trakt account."""
    log("Syncing Trakt data...", xbmc.LOGINFO)

    if not trakt_token:
        xbmcgui.Dialog().notification(addonname, "Trakt account not linked. Please link your Trakt account first.", xbmcgui.NOTIFICATION_ERROR)
        log("Failed to sync Trakt account: Trakt account not linked.", xbmc.LOGERROR)
        return

    trakt_manager.sync_account(db)

    if not addon.getSetting("Disable_Update_Notifications") == "true":
        xbmcgui.Dialog().notification(addonname, "Trakt account synced successfully.", xbmcgui.NOTIFICATION_INFO)
    log("Trakt account synced successfully.", xbmc.LOGINFO)

def list_editor():
    if not trakt_token:
        xbmcgui.Dialog().notification(addonname, "Trakt account not linked. Please link your Trakt account first.", xbmcgui.NOTIFICATION_ERROR)
        log("Failed to update lists: Trakt account not linked.", xbmc.LOGERROR)
        return

    # Check if TMDB account is linked
    if not tmdb_token:
        xbmcgui.Dialog().notification(addonname, "TMDB account not linked. Please link your TMDB account first.", xbmcgui.NOTIFICATION_ERROR)
        log("Failed to update lists: TMDB account not linked.", xbmc.LOGERROR)
        return
    
    editor_gui = EditorGUI(addon_path, API_KEY, tmdb_token)
    editor_gui.open_list_manager()

def parse_arguments():
    """Parse arguments passed via RunScript."""
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "link_trakt_account":
            link_trakt_account()
        elif action == "link_tmdb_account":
            link_tmdb_account()
        elif action == "editor":
            list_editor()
        elif action == "update_all_lists":
            update_all_lists()
        elif action == "sync_trakt_account":
            sync_trakt_account()

if __name__ == "__main__":
    parse_arguments()