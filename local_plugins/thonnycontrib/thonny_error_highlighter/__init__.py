"""
Thonny plugin for real-time syntax error underlining.
Underlines syntax errors in red directly in the editor as you type.
"""
import ast
from logging import getLogger
from thonny import get_workbench

logger = getLogger(__name__)

TAG_NAME = "syntax_error"
ERROR_COLOR = "#E51400"
DEBOUNCE_MS = 350


def is_python_file(text_widget):
    """Vérifie si le document actif est un script Python."""
    try:
        if hasattr(text_widget, "is_python_text") and text_widget.is_python_text():
            return True
        if hasattr(text_widget, "file_type") and text_widget.file_type == "python":
            return True
    except Exception:
        pass
    return True


def setup_tag(text_widget):
    """Configure le tag de soulignement rouge sur le widget Text."""
    try:
        text_widget.tag_configure(
            TAG_NAME,
            underline=True,
            underlinefg=ERROR_COLOR,
        )
        text_widget.tag_raise(TAG_NAME)
        # S'assurer que la sélection de texte reste au-dessus
        text_widget.tag_lower(TAG_NAME, "sel")
    except Exception as e:
        logger.debug("Erreur lors de la configuration du tag syntax_error: %s", e)


def get_error_range(text_widget, e: SyntaxError):
    """Calcule l'intervalle exact (start_index, end_index) dans Tkinter pour l'erreur de syntaxe."""
    line = e.lineno or 1
    msg = (e.msg or "").lower()

    try:
        line_str = text_widget.get(f"{line}.0", f"{line}.end")
    except Exception:
        return f"{line}.0", f"{line}.end"

    line_len = len(line_str)
    raw_col = max(0, (e.offset or 1) - 1)

    # 1. Chaîne non fermée (unterminated string literal) : souligner depuis le guillemet jusqu'à la fin de la ligne
    if "string" in msg or "literal" in msg:
        start_col = min(raw_col, line_len)
        return f"{line}.{start_col}", f"{line}.end"

    # 2. Erreur d'indentation : souligner le bloc / la ligne non indentée
    if "indent" in msg or "block" in msg:
        stripped = line_str.rstrip()
        if stripped:
            first_non_ws = len(line_str) - len(line_str.lstrip())
            return f"{line}.{first_non_ws}", f"{line}.{len(stripped)}"
        return f"{line}.0", f"{line}.end"

    # 3. Erreur en fin de ligne (ex: deux-points ':' manquants, parenthèse non fermée)
    stripped = line_str.rstrip()
    if raw_col >= len(stripped):
        if stripped:
            end_col = len(stripped)
            start_col = end_col - 1
            # Si le dernier caractère est alphanumérique, souligner le mot complet
            if stripped[start_col].isalnum() or stripped[start_col] == '_':
                while start_col > 0 and (stripped[start_col - 1].isalnum() or stripped[start_col - 1] == '_'):
                    start_col -= 1
            return f"{line}.{start_col}", f"{line}.{end_col}"
        else:
            return f"{line}.0", f"{line}.end"

    # 4. Intervalle fourni par Python 3.10+ (end_lineno et end_offset)
    end_line = getattr(e, "end_lineno", line) or line
    end_col_raw = getattr(e, "end_offset", None)
    if end_col_raw is not None and (end_line > line or (end_col_raw - 1) > raw_col):
        start_col = max(0, min(raw_col, line_len))
        end_col = min(line_len, max(start_col + 1, end_col_raw - 1))
        return f"{line}.{start_col}", f"{end_line}.{end_col}"

    # 5. Position unique : souligner le jeton ou mot courant
    start_col = max(0, min(raw_col, max(0, line_len - 1)))
    end_col = start_col + 1
    if start_col < line_len and (line_str[start_col].isalnum() or line_str[start_col] == '_'):
        while end_col < line_len and (line_str[end_col].isalnum() or line_str[end_col] == '_'):
            end_col += 1

    return f"{line}.{start_col}", f"{line}.{end_col}"


def check_syntax(text_widget):
    """Exécute l'analyse syntaxique et applique ou retire le soulignement rouge."""
    wb = get_workbench()
    if wb and not wb.get_option("view.highlight_syntax_errors", True):
        try:
            text_widget.tag_remove(TAG_NAME, "1.0", "end")
        except Exception:
            pass
        return

    if not is_python_file(text_widget):
        return

    try:
        source = text_widget.get("1.0", "end-1c")
    except Exception:
        return

    if not source.strip():
        try:
            text_widget.tag_remove(TAG_NAME, "1.0", "end")
        except Exception:
            pass
        return

    try:
        ast.parse(source)
        # Syntaxe valide -> effacer le soulignement d'erreur
        text_widget.tag_remove(TAG_NAME, "1.0", "end")
    except SyntaxError as e:
        setup_tag(text_widget)
        text_widget.tag_remove(TAG_NAME, "1.0", "end")
        start_idx, end_idx = get_error_range(text_widget, e)
        text_widget.tag_add(TAG_NAME, start_idx, end_idx)
        text_widget.tag_raise(TAG_NAME)
    except Exception:
        pass


def schedule_check(text_widget):
    """Programme une vérification avec délai (debounce) pour éviter tout ralentissement lors de la frappe."""
    old_timer = getattr(text_widget, "_syntax_error_timer", None)
    if old_timer:
        try:
            text_widget.after_cancel(old_timer)
        except Exception:
            pass

    try:
        text_widget._syntax_error_timer = text_widget.after(
            DEBOUNCE_MS, lambda: check_syntax(text_widget)
        )
    except Exception:
        pass


def on_text_changed(event):
    """Appelé à chaque modification dans l'éditeur."""
    text_widget = event.widget
    if text_widget:
        schedule_check(text_widget)


def on_editor_created(event):
    """Initialise le tag et lance la vérification pour un nouvel éditeur."""
    text_widget = getattr(event, "text_widget", None)
    if text_widget:
        setup_tag(text_widget)
        schedule_check(text_widget)


def on_workbench_ready(event=None):
    """Vérifie l'éditeur actuellement ouvert au démarrage."""
    wb = get_workbench()
    if not wb:
        return
    editor_notebook = wb.get_editor_notebook()
    if editor_notebook:
        for editor in editor_notebook.get_all_editors():
            text_widget = editor.get_text_widget()
            if text_widget:
                setup_tag(text_widget)
                schedule_check(text_widget)


def toggle_highlight():
    """Bascule l'activation du soulignement des erreurs."""
    wb = get_workbench()
    if not wb:
        return
    current = wb.get_option("view.highlight_syntax_errors", True)
    wb.set_option("view.highlight_syntax_errors", not current)
    on_workbench_ready()


def load_plugin():
    """Point d'entrée du plugin pour Thonny."""
    wb = get_workbench()
    wb.set_default("view.highlight_syntax_errors", True)

    # Option dans le menu Affichage (View) pour activer/désactiver si besoin
    lang = wb.get_option("general.language", "fr_FR")
    label = "Souligner les erreurs de syntaxe" if lang.startswith("fr") else "Highlight syntax errors"
    try:
        wb.add_command(
            "toggle_syntax_errors",
            "view",
            label,
            toggle_highlight,
            flag_name="view.highlight_syntax_errors",
            group=45,
        )
    except Exception:
        pass

    # Écoute des événements de modification de texte
    wb.bind_class("EditorCodeViewText", "<<TextChange>>", on_text_changed, True)
    wb.bind("EditorTextCreated", on_editor_created, True)
    wb.bind("WorkbenchReady", on_workbench_ready, True)

    # Si le workbench est déjà prêt lors du chargement
    if getattr(wb, "ready", False):
        on_workbench_ready()

    logger.info("Plugin thonny_error_highlighter chargé avec succès.")
