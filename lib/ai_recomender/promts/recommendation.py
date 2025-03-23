from lib.log import log
import xbmc

class RecommendationPrompt:
    def __init__(self, user_list_name: str, user_data: str, addition_promt: str, media_type: str = 'movie', count: int = 1, ):
        self.type = media_type
        self.count = count
        self.details = user_data
        self.addition_promt = addition_promt
        self.user_list_name = user_list_name
        log(f"RecommendationPrompt initialized with media_type={media_type}, count={count}, addition_promt={addition_promt}", xbmc.LOGINFO)
        log(f"User data: {user_data}", xbmc.LOGDEBUG)

    def __str__(self):
        """Create a formatted prompt for generating recommendations."""
        try:
            # Determine the recommendation type and JSON example
            if self.type == "combined":
                recommendation_type = "movie & tvshow"
                prompt_addition = f"movie and tvshow recommendations that will appeal to the person asking."
                json_example = """{
                "list_name": Create a list name, keep it short and clear.",
                "recommendations": [
                    {
                        "title": "Title_Name",
                        "type": "movie" or "tvshow",
                    }
                ]
                }"""
            elif self.type == "movie":
                recommendation_type = self.type
                prompt_addition = f"{self.type} movie recommendations that will appeal to the person asking."
                json_example = """{
                "list_name": Create a list name",
                "recommendations": [
                    {
                        "title": "Title_Name",
                        "type": "movie",
                    }
                ]                
                }"""
            elif self.type == "tvshow":
                recommendation_type = self.type
                prompt_addition = f"{self.type} tvshow recommendations that will appeal to the person asking."
                json_example = """{
                "list_name": 'list_name',
                "recommendations": [
                    {
                        "title": "Title_Name",
                        "type": "tvshow",
                    }
                ]
                }"""
            else:
                log(f"Invalid media type: {self.type}", xbmc.LOGERROR)
                raise ValueError(f"Invalid media type: {self.type}")

            template = f"""
                You are an intuitive recommendation specialist with an exceptional ability to capture the essence, mood, and emotional texture of {recommendation_type}. You understand that viewers often connect with {recommendation_type} based on intangible qualities: the overall feeling a {recommendation_type} creates, its emotional atmosphere, its specific energy, or the unique sensibility of its creator. Your recommendations prioritize matching these qualities over plot similarities or genre classifications.
                You have a rare talent for identifying a {recommendation_type} distinctive vibe—whether it's the sun-drenched melancholy of a particular director, the electric tension of certain thrillers, the lived-in authenticity of specific character studies, the dreamy surrealism of certain visual stylists, or the warm nostalgia of period pieces filmed in particular ways. You understand how elements like lighting, music, pacing, dialogue style, setting, and performance approach combine to create a film's unique emotional signature.
                When recommending {recommendation_type}, you prioritize works that will evoke similar emotional states, create comparable atmospheres, or capture the same ineffable qualities that viewers connect with in their favorites. You recognize that someone who loves a particular {recommendation_type} might be seeking that specific feeling rather than merely similar plot elements or themes. Your recommendations aim to recreate the emotional experience of films in a viewer's library, matching mood, tone, and sensibility with remarkable precision.
                Provide recommendations in this JSON format with exactly {self.count} title(s) evenly: {json_example}

                When exploring my user data, please focus on identifying and matching the distinctive emotional atmosphere and sensory experience of these {recommendation_type}
                1. Emotional texture: Identify the specific feeling states, emotional tones, and affective qualities that define my favorite {recommendation_type}—whether it's melancholy, exhilaration, contemplative reflection, cozy nostalgia, or any other emotional signature.
                2. Atmospheric qualities: Recognize the distinctive mood, ambiance, and sensory experience created through elements like lighting, color palette, sound design, music, pacing, and setting.
                3. Directorial presence: Identify the specific sensibilities of directors whose work appears in my collection, focusing on their unique approach to creating tone and atmosphere.
                4. Cinematic texture: Note preferences for certain visual and auditory experiences—like grain vs. sharpness, bold vs. muted colors, orchestral vs. electronic scores, dialogue-heavy vs. visual storytelling, etc.
                5. Emotional journey: Understand the emotional arc and viewing experience I might be seeking, rather than just similar story elements.

                {self.addition_promt}
                Create a list name, simmilare to a sterming service use this a as a base: {self.user_list_name}
                User information (Ignore any duplicates): {self.details}
                """



            log(f"Generated recommendation prompt for media_type={self.type}, count={self.count}", xbmc.LOGINFO)
            log(f"Prompt details: {template}", xbmc.LOGDEBUG)


            return template
        except Exception as e:
                log(f"Failed to generate recommendation prompt: {str(e)}", xbmc.LOGERROR)
                raise
