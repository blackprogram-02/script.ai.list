import xbmc
from lib.ai_recomender.timer.timer import Timer
import xbmcaddon
import xbmcvfs
import xbmcgui

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')  # Get the add-on ID
addonname = addon.getAddonInfo('name')
addon_path = xbmcvfs.translatePath(addon.getAddonInfo('profile'))

# Define the script to run
script_to_run = "RunScript(script.ai.list, update_all_lists)"

# Initialize the Timer with the add-on ID
timer = Timer(addon_id, addon_path, script_to_run)

# Run the timer periodically
while not xbmc.Monitor().abortRequested():
    timer.run()
    xbmc.sleep(5 * 60 * 1000)  # Sleep for 5 minutes