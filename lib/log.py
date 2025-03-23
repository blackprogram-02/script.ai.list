import xbmc
import inspect
import os

def log(message, level=xbmc.LOGINFO):
    """
    Log a message with a consistent prefix, including the file and function name.

    :param message: The message to log.
    :param level: The log level (e.g., xbmc.LOGINFO, xbmc.LOGDEBUG).
    """
    # Get the caller's file name, function name, and line number
    frame = inspect.currentframe().f_back
    file_path = inspect.getfile(frame)
    file_name = os.path.basename(file_path)  # Extract only the file name
    function_name = frame.f_code.co_name
    line_number = frame.f_lineno

    # Define the log prefix
    prefix = f"[ai.list] [{file_name}:{function_name}:{line_number}]"

    # Log the message
    xbmc.log(f"{prefix} {message}", level)