
# AI Curator Addon

Uses Gemini to manage personalized TMDB lists based on user trakt data.

This addon allows users to link their Trakt and TMDB accounts to manage custom lists. With the power of Gemini AI, it provides personalized recommendations and automates list updates based on user preferences. Ideal for users looking to enhance their media organization and discovery experience

# Installation Guide

Ensure you install from my repository to get the latest updates.

## Kodi Installation

### **Installation Sources**
- **Kodi File Manager Source:** [Insert your link here]
- **Direct ZIP Install:** [Insert your link here]

### **Installation Instructions**

1. **Enable Unknown Sources**
   - Go to **Kodi Settings** > **System** > **Add-ons**
   - Enable **Unknown Sources**

2. **Enable Add-on Updates from Any Repository**
   - Navigate to **Kodi Settings** > **System** > **Add-ons**
   - Enable **Update official add-ons from: Any repositories**

3. **Install My Repository**
   - Use either the **ZIP file** or **File Manager Source** linked above

4. **Install the Latest Version**
   - Locate the add-on in **My Repository** and install the latest version


# How to Use


### Linking Your Accounts
1. Go to **Account Settings**
2. Link your **Trakt Account** and **TMDB Account**
3. Enter your **Gemini API Key**

### Creating Custom Lists
Navigate to **List Settings** -> **Open List Editor** to create and manage your lists.

### Understanding the List Editor

#### Start by
Editing an existing list or create a new one.

#### Edit List Settings
- **Enabled**: Enable or disable list updates.
- **List Name**: Suggested list name for the AI (AI may rename it during updates, to have it fit the list better).
- **List Type**:
  - **Combined**: Includes both movies and TV shows.
  - **Movie**: Movies only.
  - **TV Show**: TV shows only.
- **List Description**: Description of the list.
- **List Length**: Number of items in the list (e.g., `5` for five items).

#### Attached Data
Modules allowing users to configure what Trakt user data will be sent to the AI.
- **Watch History**:
  - **Item Count**: Number of items being attached to the generation.
  - **Media Type**:
    - **Combined**: Includes both movie and TV show watch history.
    - **Movie**: Movie history only.
    - **TV Show**: TV show history only.

#### AI Provider
- Currently there is only supports for **Gemini**.

#### AI Prompt
Describe the type of list the AI should generate.
Example prompts:
  - *Pick a random item from my history and create a list based on its vibe.*
  - *Take the user's most-watched genre and create a list based on that genre.*

  You can be as creative as you like! Think of this field as a prompt for the AI.

## Requirements

To use this add-on, you will need the following:

1. **TMDB Account**  
   Sign up or log in at [The Movie Database (TMDB)](https://www.themoviedb.org/login)

2. **Trakt Account**  
   Sign up or log in at [Trakt.tv](https://trakt.tv)

3. **Gemini API Key**  
   Obtain your API key from [Google Gemini API](https://www.googleadservices.com/pagead/aclk?sa=L&ai=DChcSEwizld3qv6CMAxVLkIMHHYDvCEwYABAAGgJlZg&co=1&gclid=Cj0KCQjw4v6-BhDuARIsALprm32qawQV4Ydk7yFhAecHN8UWcp9kmiHHtbyEb15Ew9SclRj_xm94LR0aAmu3EALw_wcB&ohost=www.google.com&cid=CAESVeD2oIj9ROfJW1Ubn1c-Vj2cOkPWPmYObXZRP8jFhujbiGYtUIbvN6ekNdzZ9V6bh4obGl7Hu2FcSKWXnnDX72VhEhFW0aJtV4eBXRX3KDa0l3FvB_U&sig=AOD64_2Uo6iyIOoxTRMdZGPVy9QyUJyaqw&q&adurl&ved=2ahUKEwjRuNbqv6CMAxVL_rsIHQQ3GoAQ0Qx6BAgJEAE)