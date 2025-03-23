import os
import time
import xbmc
import xbmcaddon
from lib.log import log

class Timer:
    def __init__(self, addon_id, addon_path, script_to_run):
        """
        Initialize the Timer class with the add-on ID, path, and script to run.
        """
        self.script_to_run = script_to_run
        self.addon = xbmcaddon.Addon(addon_id)  # Create an Addon object using the add-on ID
        self.addon_path = addon_path
        self.timestamp_file = os.path.join(addon_path, 'last_run_timestamp.txt')

        # Retrieve the timer interval from the add-on settings
        timer_interval_hours = int(self.addon.getSetting('timer_interval'))
        self.interval = timer_interval_hours * 3600
        log(f"Timer initialized with interval={self.interval} seconds.", xbmc.LOGINFO)

    def get_last_run_time(self):
        """
        Retrieve the last run timestamp from the file.

        :return: The last run timestamp as a float, or 0 if the file doesn't exist or is invalid.
        """
        if os.path.exists(self.timestamp_file):
            try:
                with open(self.timestamp_file, 'r') as f:
                    last_run_time = float(f.read().strip())
                    log(f"Last run time retrieved: {last_run_time}", xbmc.LOGDEBUG)
                    return last_run_time
            except (ValueError, IOError) as e:
                log(f"Invalid timestamp file. Resetting to 0. Error: {str(e)}", xbmc.LOGWARNING)
        else:
            log("Timestamp file does not exist. Returning 0.", xbmc.LOGDEBUG)
        return 0

    def update_last_run_time(self):
        """
        Update the last run timestamp in the file to the current time.
        """
        current_time = time.time()
        with open(self.timestamp_file, 'w') as f:
            f.write(str(current_time))
        log(f"Updated last run time to {current_time}.", xbmc.LOGINFO)

    def should_run(self):
        """
        Check if the script should run based on the interval.

        :return: True if the interval has passed since the last run, False otherwise.
        """
        last_run = self.get_last_run_time()
        current_time = time.time()
        time_since_last_run = current_time - last_run
        log(f"Time since last run: {time_since_last_run} seconds.", xbmc.LOGDEBUG)
        return time_since_last_run >= self.interval

    def run(self):
        """
        Run the script if the interval has passed.
        """
        if self.should_run():
            log(f"Running script: {self.script_to_run}", xbmc.LOGINFO)
            xbmc.executebuiltin(self.script_to_run)
            self.update_last_run_time()
        else:
            time_remaining = self.interval - (time.time() - self.get_last_run_time())
            log(f"Script not run. Time remaining: {time_remaining} seconds.", xbmc.LOGINFO)