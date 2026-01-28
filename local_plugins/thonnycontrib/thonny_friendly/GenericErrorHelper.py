from thonny.assistance import ErrorHelper ,Suggestion
class GenericErrorHelper(ErrorHelper):
    def __init__(self, error_info):
        
        super().__init__(error_info)
        
        self.intro_text = "Une erreur est survenu dans votre code ☺, examinez  les détails qui suivent pour le résoudre:☻ "
        
        self.intro_confidence = 2
        self.suggestions = [
            Suggestion(
                "ask-for-specific-support",
                "Let Selmen know",
                "Click on the feedback link at the bottom of this panel to let Thonny developers know "
                + "about your problem. They may add support for "
                + "such cases in future Thonny versions.",
                1,
            )
        ]
        """
        if error_info["message"].lower() != "invalid syntax":
            self.suggestions.append(
                Suggestion(
                    "generic-search-the-web",
                    "Search the web",
                    "Try performing a web search for\n\n``Python %s: %s``"
                    % (
                        self.error_info["type_name"],
                        rst_utils.escape(self.error_info["message"].replace("\n", " ").strip()),
                    ),
                    1,
                )
            ) """