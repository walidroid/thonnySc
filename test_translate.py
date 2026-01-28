import re

_ERROR_TRANSLATIONS = {
    r"NameError: name '(.*)' is not defined": r"NameError : la variable « \1 » n'est pas définie",
}

def _translate_error(text):
    if not text:
        return text
    for pattern, replacement in _ERROR_TRANSLATIONS.items():
        text = re.sub(pattern, replacement, text)
    return text

# Test
test = "NameError: name 'x' is not defined"
print("Original:", test)
print("Translated:", _translate_error(test))
