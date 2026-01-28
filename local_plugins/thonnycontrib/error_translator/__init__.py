"""
Thonny plugin for translating Python errors to French.
Uses friendly-traceback for comprehensive error translation.
"""
import re
from thonny import get_workbench
from logging import getLogger

logger = getLogger(__name__)

# Additional regex-based translations for errors not caught by friendly-traceback
ERROR_TRANSLATIONS = {
    r"NameError: name '(.*)' is not defined": r"NameError : la variable « \1 » n'est pas définie",
    r"SyntaxError: invalid syntax": r"SyntaxError : syntaxe invalide",
    r"IndentationError: unexpected indent": r"IndentationError : indentation inattendue",
    r"IndentationError: expected an indented block": r"IndentationError : un bloc indenté est attendu",
    r"TypeError: (.*) takes (.*) positional argument but (.*) were given": r"TypeError : \1 prend \2 paramètre(s) mais \3 a/ont été donné(s)",
    r"TypeError: (.*) missing (.*) required positional arguments: (.*)": r"TypeError : \1 manque \2 paramètre(s) requis : \3",
    r"ValueError: (.*)": r"ValueError : \1",
    r"IndexError: (.*) index out of range": r"IndexError : index \1 hors intervalle",
    r"KeyError: (.*)": r"KeyError : clé \1 introuvable",
    r"ZeroDivisionError: division by zero": r"ZeroDivisionError : division par zéro",
    r"ModuleNotFoundError: No module named '(.*)'" : r"ModuleNotFoundError : Aucun module nommé « \1 »",
    r"AttributeError: '(.*)' object has no attribute '(.*)'": r"AttributeError : l'objet « \1 » n'a pas d'attribut « \2 »",
    r"FileNotFoundError: \[Errno 2\] No such file or directory: '(.*)'": r"FileNotFoundError : [Errno 2] Aucun fichier ou dossier de ce type : « \1 »",
}

def translate_text(text):
    """Apply regex-based translation to text."""
    if not text:
        return text
    
    # Process line by line
    lines = text.splitlines(keepends=True)
    translated_lines = []
    
    for line in lines:
        translated_line = line
        for pattern, replacement in ERROR_TRANSLATIONS.items():
            new_line = re.sub(pattern, replacement, translated_line)
            if new_line != translated_line:
                translated_line = new_line
                break
        translated_lines.append(translated_line)
    
    return "".join(translated_lines)

def handle_program_output(event):
    """Handle ProgramOutput events and translate stderr."""
    print(f"[ERROR_TRANSLATOR] Event received: {event}", flush=True)  # Debug
    try:
        # Only translate stderr (error output)
        if hasattr(event, 'stream_name'):
            stream = event.stream_name
        else:
            stream = event.get("stream_name")
        
        print(f"[ERROR_TRANSLATOR] Stream: {stream}", flush=True)  # Debug
        
        if stream == "stderr":
            if hasattr(event, 'data'):
                original_data = event.data
            else:
                original_data = event.get("data", "")
            
            print(f"[ERROR_TRANSLATOR] Original: {original_data}", flush=True)  # Debug
            
            if original_data:
                # Apply translation
                translated_data = translate_text(original_data)
                print(f"[ERROR_TRANSLATOR] Translated: {translated_data}", flush=True)  # Debug
                
                # Update the event with translated text
                if hasattr(event, 'data'):
                    event.data = translated_data
                else:
                    event["data"] = translated_data
    except Exception as e:
        print(f"[ERROR_TRANSLATOR] Exception: {e}", flush=True)  # Debug
        logger.exception("Error in error_translator plugin: %s", e)

def load_plugin():
    """Initialize the error translation plugin."""
    print("[ERROR_TRANSLATOR] Loading plugin...", flush=True)  # Debug
    
    try:
        # Install friendly-traceback with French language
        import friendly_traceback
        friendly_traceback.install(lang="fr")
        print("[ERROR_TRANSLATOR] friendly-traceback installed with French", flush=True)
        logger.info("friendly-traceback installed with French language")
    except ImportError:
        print("[ERROR_TRANSLATOR] friendly-traceback not available", flush=True)
        logger.warning("friendly-traceback not available, using regex-only translation")
    except Exception as e:
        print(f"[ERROR_TRANSLATOR] Error loading friendly-traceback: {e}", flush=True)
        logger.exception("Error installing friendly-traceback: %s", e)
    
    # Hook into ProgramOutput events
    # The True parameter means we want to receive events before they're processed
    wb = get_workbench()
    wb.bind("ProgramOutput", handle_program_output, True)
    print(f"[ERROR_TRANSLATOR] Plugin loaded, bound to ProgramOutput", flush=True)
    logger.info("Error translator plugin loaded")
