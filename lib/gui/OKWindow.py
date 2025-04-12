import xbmcgui
import xbmc


# --- Custom Window Class ---
class MyOkWindow(xbmcgui.WindowXMLDialog):
    """
    Custom window class to display QR code and URL.
    Loads OkWindow.xml
    """
    def __init__(self, *args, **kwargs):
        # Initialize the MyWindowXMLDialog. The XML filename is passed implicitly by Kodi
        self.message = kwargs.get('message', '')
        self.display_title = kwargs.get('display_title', 'test')

    def onInit(self):
        """
        Called when the window is initialized.
        Set control values here.
        """
        xbmc.log("OKWindow: Initializing...", level=xbmc.LOGINFO)
        
        try:
            # Set properties that the XML can read using $INFO[Window.Property(key)]
            self.setProperty('display_title', self.display_title)
            self.setProperty('message', self.message)

            # Set focus to the close button initially
            self.setFocusId(9000)

        except Exception as e:
            xbmc.log(f"OkWindow: Error in onInit: {e}", level=xbmc.LOGERROR)
            # Optionally close the window or show an error within it
            self.close()


    def onClick(self, controlId):
        """
        Called when a control is clicked.
        """
        xbmc.log(f"OkWindow: onClick received for controlId: {controlId}", level=xbmc.LOGINFO)
        if controlId == 9000: # Close button ID
            self.close()

    def onAction(self, action):
        """
        Called when an action (like remote button press) is performed.
        """
        xbmc.log(f"OkWindow: onAction received: {action.getId()}", level=xbmc.LOGINFO)
        # Action codes can be found on Kodi wiki (e.g., ACTION_PREVIOUS_MENU, ACTION_NAV_BACK)
        if action.getId() in (9, 10): # 9=NAV_BACK, 10=PREVIOUS_MENU
            self.close()