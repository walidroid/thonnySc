"""
Thonny plugin for translating Python errors to French.
Uses sys.excepthook to intercept exceptions.
"""
import sys
import re
from logging import getLogger

print("[ERROR_TRANSLATOR] Module imported", flush=True)

logger = getLogger(__name__)

# Regex-based translations for common Python errors
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
    
    for pattern, replacement in ERROR_TRANSLATIONS.items():
        text = re.sub(pattern, replacement, text)
    
    return text

# Store the original excepthook
_original_excepthook = sys.excepthook

def custom_excepthook(exc_type, exc_value, exc_traceback):
    """Custom exception hook that translates error messages."""
    print("[ERROR_TRANSLATOR] Custom excepthook called", flush=True)
    
    # Get the original traceback string
    import traceback
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    
    # Translate each line
    translated_lines = [translate_text(line) for line in tb_lines]
    
    # Print translated traceback
    for line in translated_lines:
        sys.stderr.write(line)
    
    sys.stderr.flush()

def load_plugin() -> None:
    """Initialize the error translation plugin."""
    print("[ERROR_TRANSLATOR] load_plugin() called", flush=True)
    
    try:
        # Install friendly-traceback with French language
        import friendly_traceback
        friendly_traceback.install(lang="fr")
        print("[ERROR_TRANSLATOR] friendly-traceback installed", flush=True)
    except ImportError:
        print("[ERROR_TRANSLATOR] friendly-traceback not available, using regex only", flush=True)
        # Fall back to our custom excepthook
        sys.excepthook = custom_excepthook
        print("[ERROR_TRANSLATOR] Custom excepthook installed", flush=True)
    except Exception as e:
        print(f"[ERROR_TRANSLATOR] Error: {e}", flush=True)
        logger.exception("Error installing friendly-traceback: %s", e)

print("[ERROR_TRANSLATOR] Module loaded, load_plugin defined", flush=True)
