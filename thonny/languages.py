import gettext
import os
from logging import getLogger

logger = getLogger(__name__)

BASE_LANGUAGE_CODE = "fr_FR"
BASE_LANGUAGE_NAME = "Français [défaut]"

# https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes

LANGUAGES_DICT = {
    "en_US": "English (US)",
    BASE_LANGUAGE_CODE: BASE_LANGUAGE_NAME,
}

# how many spaces to add to button caption in order to make whole text visible
BUTTON_PADDING_SIZES = {"zh_TW": 4, "zh_CN": 4, "ja_JP": 4}

_translation = gettext.NullTranslations()


def get_button_padding():
    from thonny import get_workbench

    code = get_workbench().get_option("general.language")
    if code in BUTTON_PADDING_SIZES:
        return BUTTON_PADDING_SIZES[code] * " "
    else:
        return ""


def get_language_code_by_name(name):
    for code in LANGUAGES_DICT:
        if LANGUAGES_DICT[code] == name:
            return code

    raise RuntimeError("Unknown language name '%s'" % name)


def tr(message: str) -> str:
    return _translation.gettext(message)


class ThonnyGNUTranslations(gettext.GNUTranslations):
    def __init__(self, fp=None):
        self._charset = "utf-8"
        super().__init__(fp)


def set_language(language_code: str) -> None:
    global _translation
    import sys

    candidate_paths = [
        os.path.join(os.path.dirname(__file__), "locale"),
    ]
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            candidate_paths.append(os.path.join(sys._MEIPASS, "thonny", "locale"))
            candidate_paths.append(os.path.join(sys._MEIPASS, "locale"))
        exe_dir = os.path.dirname(sys.executable)
        candidate_paths.append(os.path.join(exe_dir, "_internal", "thonny", "locale"))
        candidate_paths.append(os.path.join(exe_dir, "thonny", "locale"))

    for path in candidate_paths:
        mo_file = os.path.join(path, language_code, "LC_MESSAGES", "thonny.mo")
        if os.path.isfile(mo_file):
            try:
                _translation = gettext.translation(
                    "thonny", path, [language_code], class_=ThonnyGNUTranslations
                )
                logger.info("Loaded language '%s' from %s", language_code, mo_file)
                return
            except Exception as e:
                logger.exception("Could not set language to '%s' from %s", language_code, mo_file, exc_info=e)

    try:
        path = os.path.join(os.path.dirname(__file__), "locale")
        _translation = gettext.translation(
            "thonny", path, [language_code], class_=ThonnyGNUTranslations
        )
    except Exception as e:
        logger.exception("Could not set language to '%s'", language_code, exc_info=e)
        _translation = gettext.NullTranslations()
