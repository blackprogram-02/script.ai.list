import xbmcgui
import json
import os
from lib.ai_recomender.Lists.ListHandeler import ListHandler
from lib.ai_recomender.TMDB.ListManager import TMDBListManager
from lib.log import log
import xbmc

class EditorGUI:
    def __init__(self, addon_path, tmdb_api_key, tmdb_token):
        """
        Initialize the EditorGUI class with the given addon path, TMDB API key, and TMDB token.
        """
        self.list_handler = ListHandler(addon_path, tmdb_api_key, tmdb_token)
        self.tmdb_list_manager = TMDBListManager(tmdb_api_key, tmdb_token)
        log("EditorGUI initialized.", xbmc.LOGINFO)

    def manage_lists(self):
        """
        Manage the lists by displaying a dialog to select a list or create a new one.
        """
        lists = self.list_handler.lists
        log(f"Loaded lists: {lists}", xbmc.LOGDEBUG)

        list_keys = list(lists.keys())
        list_names = [lists[key]['list_setting']['list_name'] for key in list_keys]
        list_names.append("Create New List")  # Add option to create a new list
        
        selected_index = xbmcgui.Dialog().select("Select a List", list_names)
        if selected_index == -1:
            log("No list selected. Exiting list management.", xbmc.LOGINFO)
            return
        
        if selected_index == len(list_names) - 1:  # Create New List
            new_name = xbmcgui.Dialog().input("Enter new list name")
            if not new_name:
                xbmcgui.Dialog().notification("Error", "List name cannot be empty", xbmcgui.NOTIFICATION_ERROR)
                log("Failed to create a new list: List name is empty.", xbmc.LOGERROR)
                return
            new_description = xbmcgui.Dialog().input("Enter new list description")
            new_list = {
                "enabled": True,
                "list_setting": {
                    "list_name": new_name,
                    "list_type": "movie",
                    "list_description": new_description,
                    "list_length": 5
                },
                "attacched_data": {
                    "watch_history": {
                        "item_count": 1,
                        "media_type": "movie",
                        "random": True
                    }
                },
                "AI": {
                    "provider": "gemini",
                    "promt": "Give me a list of family titles"
                }
            }
            try:
                # Create the list on TMDB and get the ID
                tmdb_list_id = self.tmdb_list_manager.create_list(new_list['list_setting']['list_name'], new_list['list_setting']['list_description'])
                if not tmdb_list_id:
                    raise Exception("Failed to create list on TMDB")
                # Use the TMDB list ID as the key
                lists[tmdb_list_id] = new_list
                self.list_handler.save_lists()
                xbmcgui.Dialog().ok('List Created', f'Name: {new_name}')
                log(f"New list created: {new_list}", xbmc.LOGDEBUG)
            except Exception as e:
                xbmcgui.Dialog().notification("Error", str(e), xbmcgui.NOTIFICATION_ERROR)
                log(f"Failed to create new list: {str(e)}", xbmc.LOGERROR)
            return
        
        selected_key = list_keys[selected_index]
        selected_list = lists[selected_key]
        log(f"Selected list: {selected_list}", xbmc.LOGDEBUG)

        list_name = selected_list['list_setting']['list_name']
        list_description = selected_list['list_setting']['list_description']
                
        action = xbmcgui.Dialog().select("Select Action", ["Edit List Settings", "Delete List"])
        if action == -1:
            log("No action selected for the list.", xbmc.LOGINFO)
            return
        
        if action == 1:  # Delete List
            if xbmcgui.Dialog().yesno("Confirm Delete", f"Are you sure you want to delete the list '{list_name}'?"):
                try:
                    # Delete the list from TMDB
                    self.tmdb_list_manager.delete_list(selected_key)
                    # Delete the list locally
                    self.list_handler.delete_list(selected_key)
                    xbmcgui.Dialog().ok('List Deleted', f'List {list_name} has been deleted.')
                    log(f"List deleted: {list_name} (ID: {selected_key})", xbmc.LOGINFO)
                except Exception as e:
                    xbmcgui.Dialog().notification("Error", str(e), xbmcgui.NOTIFICATION_ERROR)
                    log(f"Failed to delete list: {str(e)}", xbmc.LOGERROR)
        elif action == 0:  # Edit Settings
            self.edit_settings(selected_list, selected_key)


    def edit_settings(self, selected_list, selected_key):
        """
        Edit the settings of the selected list.
        """
        while True:
            settings = selected_list['list_setting']
            attached_data = selected_list.get('attacched_data', {})
            ai_settings = selected_list['AI']

            log(f"Editing settings for list: {settings}", xbmc.LOGDEBUG)
            
            setting_options = [
                f"Enabled: {selected_list['enabled']}",
                f"List Name: {settings['list_name']}",
                f"List Type: {settings['list_type']}",
                f"List Description: {settings['list_description']}",
                f"List Length: {settings['list_length']}",
                "Attached Data" if attached_data else "Add Attached Data",
                f"AI Provider: {ai_settings['provider']}",
                f"AI Prompt: {ai_settings['promt']}"
            ]
            
            selected_setting = xbmcgui.Dialog().select("Select Setting to Edit", setting_options)
            if selected_setting == -1:
                log("No setting selected for editing.", xbmc.LOGINFO)
                break
            
            try:
                if selected_setting == 0:  # Enabled
                    enabled_options = ["True", "False"]
                    selected_enabled = xbmcgui.Dialog().select("Select Enabled", enabled_options)
                    if selected_enabled != -1:
                        selected_list['enabled'] = selected_enabled == 0
                        log(f"Updated 'enabled' setting to: {selected_list['enabled']}", xbmc.LOGINFO)
                elif selected_setting == 1:  # List Name
                    new_value = xbmcgui.Dialog().input("Enter new list name", settings['list_name'])
                    if new_value:
                        self.tmdb_list_manager.rename_list(selected_key, new_value)
                        settings['list_name'] = new_value
                        log(f"Updated 'list_name' to: {new_value}", xbmc.LOGINFO)
                    else:
                        xbmcgui.Dialog().notification("Error", "List name cannot be empty", xbmcgui.NOTIFICATION_ERROR)
                        log("Failed to update 'list_name': Name is empty.", xbmc.LOGERROR)
                elif selected_setting == 2:  # List Type
                    list_type_options = ["combined", "movie", "tvshow"]
                    selected_list_type = xbmcgui.Dialog().select("Select List Type", list_type_options)
                    if selected_list_type != -1:
                        settings['list_type'] = list_type_options[selected_list_type]
                        log(f"Updated 'list_type' to: {settings['list_type']}", xbmc.LOGINFO)
                elif selected_setting == 3:  # List Description
                    new_value = xbmcgui.Dialog().input("Enter new list description", settings['list_description'])
                    settings['list_description'] = new_value
                    log(f"Updated 'list_description' to: {new_value}", xbmc.LOGINFO)
                elif selected_setting == 4:  # List Length
                    new_value = xbmcgui.Dialog().input("Enter new list length", str(settings['list_length']), type=xbmcgui.INPUT_NUMERIC)
                    if new_value.isdigit():
                        settings['list_length'] = int(new_value)
                        log(f"Updated 'list_length' to: {settings['list_length']}", xbmc.LOGINFO)
                    else:
                        xbmcgui.Dialog().notification("Error", "List length must be a number", xbmcgui.NOTIFICATION_ERROR)
                        log("Failed to update 'list_length': Value is not a number.", xbmc.LOGERROR)
                elif selected_setting == 5:  # Attached Data
                    if attached_data:
                        self.manage_attached_data(attached_data)
                    else:
                        self.add_attached_data(selected_list)
                elif selected_setting == 6:  # AI Provider
                    provider_options = ["gemini"]
                    selected_provider = xbmcgui.Dialog().select("Select AI Provider", provider_options)
                    if selected_provider != -1:
                        ai_settings['provider'] = provider_options[selected_provider]
                        log(f"Updated 'AI provider' to: {ai_settings['provider']}", xbmc.LOGINFO)
                elif selected_setting == 7:  # AI Prompt
                    new_value = xbmcgui.Dialog().input("Enter new AI prompt", ai_settings['promt'])
                    ai_settings['promt'] = new_value
                    log(f"Updated 'AI prompt' to: {new_value}", xbmc.LOGINFO)
                
                self.list_handler.save_lists()
                log("List settings saved successfully.", xbmc.LOGINFO)
            except Exception as e:
                xbmcgui.Dialog().notification("Error", str(e), xbmcgui.NOTIFICATION_ERROR)
                log(f"Failed to edit settings: {str(e)}", xbmc.LOGERROR)

    def manage_attached_data(self, attached_data):
        """
        Manage the attached data of the selected list.
        """
        while True:
            attached_data_options = list(attached_data.keys()) + ["Add Module"]
            
            selected_attached_data = xbmcgui.Dialog().select("Select Attached Data Module", attached_data_options)
            if selected_attached_data == -1:
                break
            
            if selected_attached_data == len(attached_data_options) - 1:  # Add Module
                self.add_attached_data_module(attached_data)
            else:
                module_name = attached_data_options[selected_attached_data]
                self.edit_attached_data_module(attached_data, module_name)

    def edit_attached_data_module(self, attached_data, module_name):
        """
        Edit the settings of the selected attached data module.
        """
        while True:
            module_data = attached_data[module_name]
            log(f"Editing attached data module: {module_name} with data: {module_data}", xbmc.LOGDEBUG)

            module_options = [
                f"Item Count: {module_data['item_count']}",
                f"Media Type: {module_data['media_type']}",
                # f"Random: {module_data['random']}",
                "Remove Module"
            ]
            
            selected_module_option = xbmcgui.Dialog().select("Select Module Setting to Edit", module_options)
            if selected_module_option == -1:
                log(f"Exited editing attached data module: {module_name}", xbmc.LOGINFO)
                break
            
            try:
                if selected_module_option == 0:  # Item Count
                    new_value = xbmcgui.Dialog().input("Enter new item count", str(module_data['item_count']), type=xbmcgui.INPUT_NUMERIC)
                    if new_value.isdigit():
                        module_data['item_count'] = int(new_value)
                        log(f"Updated 'item_count' for module '{module_name}' to: {module_data['item_count']}", xbmc.LOGINFO)
                    else:
                        xbmcgui.Dialog().notification("Error", "Item count must be a number", xbmcgui.NOTIFICATION_ERROR)
                        log(f"Failed to update 'item_count' for module '{module_name}': Value is not a number.", xbmc.LOGERROR)
                elif selected_module_option == 1:  # Media Type
                    media_type_options = ["combined", "movie", "tv_show"]
                    selected_media_type = xbmcgui.Dialog().select("Select Media Type", media_type_options)
                    if selected_media_type != -1:
                        module_data['media_type'] = media_type_options[selected_media_type]
                        log(f"Updated 'media_type' for module '{module_name}' to: {module_data['media_type']}", xbmc.LOGINFO)
                elif selected_module_option == 3:  # Random
                    random_options = ["True", "False"]
                    selected_random = xbmcgui.Dialog().select("Select Random", random_options)
                    if selected_random != -1:
                        module_data['random'] = selected_random == 0
                        log(f"Updated 'random' for module '{module_name}' to: {module_data['random']}", xbmc.LOGINFO)
                elif selected_module_option == 2:  # Remove Module
                    if xbmcgui.Dialog().yesno("Confirm Remove", f"Are you sure you want to remove the module '{module_name}'?"):
                        del attached_data[module_name]
                        self.list_handler.save_lists()
                        xbmcgui.Dialog().ok('Module Removed', f'The module {module_name} has been removed.')
                        log(f"Removed attached data module: {module_name}", xbmc.LOGINFO)
                        break
                
                self.list_handler.save_lists()
                xbmcgui.Dialog().ok('Module Updated', 'The module has been updated.')
                log(f"Attached data module '{module_name}' updated successfully.", xbmc.LOGINFO)
            except Exception as e:
                xbmcgui.Dialog().notification("Error", str(e), xbmcgui.NOTIFICATION_ERROR)
                log(f"Failed to edit attached data module '{module_name}': {str(e)}", xbmc.LOGERROR)

    def add_attached_data(self, selected_list):
        """
        Add attached data to the selected list.
        """
        module_name_options = ["watch_history"]
        selected_module_name = xbmcgui.Dialog().select("Select Module Name", module_name_options)
        if selected_module_name == -1:
            log("No module selected for adding attached data.", xbmc.LOGINFO)
            return
        new_module_name = module_name_options[selected_module_name]
        new_item_count = xbmcgui.Dialog().input("Enter item count", type=xbmcgui.INPUT_NUMERIC)
        if not new_item_count.isdigit():
            xbmcgui.Dialog().notification("Error", "Item count must be a number", xbmcgui.NOTIFICATION_ERROR)
            log(f"Failed to add attached data: Invalid item count for module '{new_module_name}'.", xbmc.LOGERROR)
            return
        media_type_options = ["combined", "movie", "tv_show"]
        selected_media_type = xbmcgui.Dialog().select("Select Media Type", media_type_options)
        if selected_media_type == -1:
            log(f"Media type selection canceled for module '{new_module_name}'.", xbmc.LOGINFO)
            return
        new_media_type = media_type_options[selected_media_type]
        new_random = xbmcgui.Dialog().yesno("Random", "Should the items be random?")

        selected_list['attacched_data'][new_module_name] = {
            "item_count": int(new_item_count),
            "media_type": new_media_type,
            "random": new_random
        }
        
        self.list_handler.save_lists()
        xbmcgui.Dialog().ok('Attached Data Added', 'The attached data has been added.')
        log(f"Attached data added to list: {selected_list['list_setting']['list_name']} with module '{new_module_name}'", xbmc.LOGINFO)

    def add_attached_data_module(self, attached_data):
        """
        Add a new attached data module to the selected list.
        """
        module_name_options = ["watch_history"]
        selected_module_name = xbmcgui.Dialog().select("Select Module Attachment to add", module_name_options)
        if selected_module_name == -1:
            log("No module selected for adding attached data module.", xbmc.LOGINFO)
            return
        new_module_name = module_name_options[selected_module_name]
        new_item_count = xbmcgui.Dialog().input("Enter the item count to attache", type=xbmcgui.INPUT_NUMERIC)
        if not new_item_count.isdigit():
            xbmcgui.Dialog().notification("Error", "Item count must be a number", xbmcgui.NOTIFICATION_ERROR)
            log(f"Failed to add attached data module: Invalid item count for module '{new_module_name}'.", xbmc.LOGERROR)
            return
        media_type_options = ["combined", "movie", "tv_show"]
        selected_media_type = xbmcgui.Dialog().select("Select Media Type to attache", media_type_options)
        if selected_media_type == -1:
            log(f"Media type selection canceled for module '{new_module_name}'.", xbmc.LOGINFO)
            return
        new_media_type = media_type_options[selected_media_type]
        new_random = xbmcgui.Dialog().yesno("Random", "Should the items be random?")
        
        attached_data[new_module_name] = {
            "item_count": int(new_item_count),
            "media_type": new_media_type,
            "random": new_random
        }
        
        self.list_handler.save_lists()
        xbmcgui.Dialog().ok('Module Added', 'The new module has been added.')
        log(f"New attached data module '{new_module_name}' added with data: {attached_data[new_module_name]}", xbmc.LOGDEBUG)

    def open_list_manager(self):
        """
        Open the list manager to manage lists.
        """
        self.manage_lists()