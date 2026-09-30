"""
Thonny plugin for post-execution error highlighting.
Underlines errors in red ONLY AFTER execution fails.
Does NOT underline while typing or editing.
"""
import ast
import os
import re
from logging import getLogger
from thonny import get_workbench, get_shell

logger = getLogger(__name__)

TAG_NAME = "syntax_error"
ERROR_COLOR = "#E51400"

# Buffer pour capturer stderr / tracebacks durant l'exécution
_stderr_buffer = ""
_execution_in_progress = False


def is_python_file(text_widget):
    """Vérifie si le document actif est un script Python."""
    try:
        if hasattr(text_widget, "is_python_text") and not text_widget.is_python_text():
            return False
        if hasattr(text_widget, "file_type") and text_widget.file_type != "python":
            return False
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
            foreground=ERROR_COLOR,
        )
        text_widget.tag_raise(TAG_NAME)
        text_widget.tag_lower(TAG_NAME, "sel")
    except Exception as e:
        logger.debug("Erreur configuration tag: %s", e)


def clear_all_highlights():
    """Efface tous les soulignements d'erreurs dans tous les éditeurs ouverts."""
    wb = get_workbench()
    if not wb:
        return
    notebook = wb.get_editor_notebook()
    if not notebook:
        return
    for editor in notebook.get_all_editors():
        try:
            txt = editor.get_text_widget()
            if txt:
                txt.tag_remove(TAG_NAME, "1.0", "end")
        except Exception:
            pass


def is_same_file(fn1, fn2):
    """Compare deux chemins de fichier."""
    if not fn1 or not fn2:
        return False
    if fn1 == fn2:
        return True
    try:
        if os.path.exists(fn1) and os.path.exists(fn2):
            return os.path.samefile(fn1, fn2)
    except Exception:
        pass
    norm1 = os.path.normcase(os.path.normpath(fn1))
    norm2 = os.path.normcase(os.path.normpath(fn2))
    if norm1 == norm2:
        return True
    if os.path.basename(norm1) == os.path.basename(norm2):
        return True
    return False


def is_file_open_in_editors(filename):
    """Vérifie si un fichier est ouvert dans un des éditeurs."""
    wb = get_workbench()
    if not wb:
        return False
    notebook = wb.get_editor_notebook()
    if not notebook:
        return False
    for editor in notebook.get_all_editors():
        ed_fn = editor.get_filename()
        if ed_fn and is_same_file(filename, ed_fn):
            return True
    return False


def find_target_editor(filename):
    """Trouve l'éditeur correspondant au fichier d'erreur ou l'éditeur actif."""
    wb = get_workbench()
    if not wb:
        return None
    notebook = wb.get_editor_notebook()
    if not notebook:
        return None

    current = notebook.get_current_editor()

    # Si pseudo-nom (<stdin>, <string>, etc.) ou vide, vérifier le dernier fichier exécuté
    if not filename or filename in ("<stdin>", "<string>", "<editor>", "<untitled>", ""):
        shell = get_shell()
        last_main = getattr(shell, "_last_main_file", None) if shell else None
        if last_main and last_main not in ("<stdin>", "<string>", "<editor>", "<untitled>", ""):
            filename = last_main
        else:
            return current

    for editor in notebook.get_all_editors():
        ed_fn = editor.get_filename()
        if ed_fn and is_same_file(filename, ed_fn):
            return editor

    return current


def parse_traceback_text(text):
    """
    Analyse le texte traceback de stderr pour extraire :
    - frames : liste de (filename, lineno)
    - error_type : type d'exception (ex: ZeroDivisionError, NameError, SyntaxError)
    - error_msg : message d'erreur
    - caret_col : position de la flèche '^' si présente
    """
    frames = []
    if not text:
        return frames, None, None, None

    # Pattern standard File "...", line 123
    frame_pattern = re.compile(r'File "([^"]+)", line (\d+)(?:, in (.+))?')
    for match in frame_pattern.finditer(text):
        frames.append((match.group(1), int(match.group(2))))

    # Alternative MicroPython (ex: line 12 in 'main.py')
    if not frames:
        alt_pattern = re.compile(r'\bline (\d+)\b[^\n]+\'([^\']+\.pyw?)\'', re.IGNORECASE)
        for match in alt_pattern.finditer(text):
            frames.append((match.group(2), int(match.group(1))))

    lines = text.splitlines()

    # Détection de la flèche '^'
    caret_col = None
    for line in lines:
        if line.strip().startswith('^'):
            caret_col = line.find('^')
            break

    # Détection du type et message d'erreur
    error_type = None
    error_msg = None
    for line in reversed(lines):
        line_clean = line.strip()
        m = re.match(r'^([a-zA-Z_]\w*(?:Error|Exception))\s*:\s*(.*)$', line_clean)
        if m:
            error_type = m.group(1)
            error_msg = m.group(2)
            break

    return frames, error_type, error_msg, caret_col


def get_syntax_error_range(text_widget, e: SyntaxError):
    """Calcule l'intervalle exact (start_index, end_index) pour une erreur de syntaxe."""
    line = e.lineno or 1
    msg = (e.msg or "").lower()

    try:
        line_str = text_widget.get(f"{line}.0", f"{line}.end")
    except Exception:
        return f"{line}.0", f"{line}.end"

    line_len = len(line_str)
    raw_col = max(0, (e.offset or 1) - 1)

    # 1. Chaîne non fermée
    if "string" in msg or "literal" in msg:
        start_col = min(raw_col, line_len)
        return f"{line}.{start_col}", f"{line}.end"

    # 2. Erreur d'indentation
    if "indent" in msg or "block" in msg:
        stripped = line_str.rstrip()
        if stripped:
            first_non_ws = len(line_str) - len(line_str.lstrip())
            return f"{line}.{first_non_ws}", f"{line}.{len(stripped)}"
        return f"{line}.0", f"{line}.end"

    # 3. Fin de ligne (ex: ':' manquant)
    stripped = line_str.rstrip()
    if raw_col >= len(stripped):
        if stripped:
            end_col = len(stripped)
            start_col = end_col - 1
            if stripped[start_col].isalnum() or stripped[start_col] == '_':
                while start_col > 0 and (stripped[start_col - 1].isalnum() or stripped[start_col - 1] == '_'):
                    start_col -= 1
            return f"{line}.{start_col}", f"{line}.{end_col}"
        else:
            return f"{line}.0", f"{line}.end"

    # 4. Intervalle fourni par Python 3.10+
    end_line = getattr(e, "end_lineno", line) or line
    end_col_raw = getattr(e, "end_offset", None)
    if end_col_raw is not None and (end_line > line or (end_col_raw - 1) > raw_col):
        start_col = max(0, min(raw_col, line_len))
        end_col = min(line_len, max(start_col + 1, end_col_raw - 1))
        return f"{line}.{start_col}", f"{end_line}.{end_col}"

    # 5. Position unique : mot ou jeton courant
    start_col = max(0, min(raw_col, max(0, line_len - 1)))
    end_col = start_col + 1
    if start_col < line_len and (line_str[start_col].isalnum() or line_str[start_col] == '_'):
        while end_col < line_len and (line_str[end_col].isalnum() or line_str[end_col] == '_'):
            end_col += 1

    return f"{line}.{start_col}", f"{line}.{end_col}"


def compute_runtime_error_range(line_str, lineno, error_type=None, error_msg="", col_offset=None):
    """Calcule l'intervalle de soulignement pour une erreur d'exécution (NameError, ZeroDivisionError, etc.)."""
    line_len = len(line_str)
    stripped = line_str.strip()
    first_non_ws = len(line_str) - len(line_str.lstrip())
    last_non_ws = len(line_str.rstrip())

    if not stripped:
        return f"{lineno}.0", f"{lineno}.end"

    msg = error_msg or ""

    # Pour NameError ou AttributeError, souligner le nom de la variable ou méthode
    if error_type in ("NameError", "AttributeError"):
        quoted_names = [q.strip() for q in re.findall(r"['«]([^'»]+)['»]", msg)]
        target_name = None
        if error_type == "AttributeError" and len(quoted_names) >= 2:
            target_name = quoted_names[1]
        elif quoted_names:
            target_name = quoted_names[0]

        if target_name:
            pattern = re.compile(r'\b' + re.escape(target_name) + r'\b')
            m = pattern.search(line_str)
            if m:
                return f"{lineno}.{m.start()}", f"{lineno}.{m.end()}"

    # Si un décalage de colonne est connu
    if col_offset is not None and col_offset >= 0:
        col = min(col_offset, line_len)
        start_col = max(0, min(col, max(0, line_len - 1)))
        end_col = start_col + 1
        if start_col < line_len and (line_str[start_col].isalnum() or line_str[start_col] == '_'):
            while start_col > 0 and (line_str[start_col - 1].isalnum() or line_str[start_col - 1] == '_'):
                start_col -= 1
            while end_col < line_len and (line_str[end_col].isalnum() or line_str[end_col] == '_'):
                end_col += 1
            return f"{lineno}.{start_col}", f"{lineno}.{end_col}"
        elif col < line_len:
            return f"{lineno}.{start_col}", f"{lineno}.{min(line_len, start_col + 1)}"

    # Par défaut : souligner le code non vide sur la ligne
    return f"{lineno}.{first_non_ws}", f"{lineno}.{last_non_ws}"


def highlight_error_in_editor(editor, lineno, col_offset, error_type, error_msg):
    """Applique le soulignement rouge sur la ligne de l'erreur dans l'éditeur ciblé."""
    try:
        text_widget = editor.get_text_widget()
        if not text_widget:
            return

        setup_tag(text_widget)
        text_widget.tag_remove(TAG_NAME, "1.0", "end")

        # Vérifier que le numéro de ligne est valide dans le document
        try:
            line_count = int(float(text_widget.index("end-1c").split('.')[0]))
        except Exception:
            line_count = 999999

        if lineno < 1 or lineno > line_count:
            return

        source = text_widget.get("1.0", "end-1c")
        try:
            line_str = text_widget.get(f"{lineno}.0", f"{lineno}.end")
        except Exception:
            return

        # Si SyntaxError, essayer ast.parse pour obtenir la précision maximale
        if error_type == "SyntaxError":
            try:
                ast.parse(source)
            except SyntaxError as e:
                start_idx, end_idx = get_syntax_error_range(text_widget, e)
                text_widget.tag_add(TAG_NAME, start_idx, end_idx)
                text_widget.tag_raise(TAG_NAME)
                try:
                    text_widget.see(f"{lineno}.0")
                except Exception:
                    pass
                return
            except Exception:
                pass

        # Calcul de la zone à souligner
        start_idx, end_idx = compute_runtime_error_range(line_str, lineno, error_type, error_msg, col_offset)
        text_widget.tag_add(TAG_NAME, start_idx, end_idx)
        text_widget.tag_raise(TAG_NAME)

        try:
            text_widget.see(f"{lineno}.0")
        except Exception:
            pass

        # S'assurer que l'éditeur ciblé est sélectionné dans le notebook
        wb = get_workbench()
        if wb:
            notebook = wb.get_editor_notebook()
            if notebook and notebook.get_current_editor() != editor:
                try:
                    notebook.select(editor)
                except Exception:
                    pass

    except Exception as e:
        logger.exception("Erreur lors de l'application du soulignement: %s", e)


def on_text_changed(event):
    """
    Appelé lors de toute modification du texte (frappe / saisie au clavier).
    NE SOULIGNE RIEN pendant la frappe : supprime immédiatement tout soulignement existant.
    """
    try:
        widget = getattr(event, "widget", None)
        if widget:
            widget.tag_remove(TAG_NAME, "1.0", "end")
    except Exception:
        pass


def on_command_accepted(event=None):
    """Dès qu'une commande est acceptée (début d'exécution), effacer les erreurs."""
    global _stderr_buffer, _execution_in_progress
    _stderr_buffer = ""
    _execution_in_progress = True
    clear_all_highlights()


def on_backend_restart(event=None):
    """En cas de redémarrage backend, effacer les erreurs."""
    global _stderr_buffer
    _stderr_buffer = ""
    clear_all_highlights()


def on_program_output(event):
    """Capture les messages d'erreur émis par le programme."""
    global _stderr_buffer
    try:
        stream = getattr(event, "stream_name", None)
        if not stream and hasattr(event, "get"):
            stream = event.get("stream_name")

        data = getattr(event, "data", "")
        if not data and hasattr(event, "get"):
            data = event.get("data", "")

        if stream == "stderr":
            _stderr_buffer += data
        elif "Traceback (most recent call last):" in data or "SyntaxError:" in data:
            _stderr_buffer += data
    except Exception as e:
        logger.debug("Erreur capture output: %s", e)


def on_toplevel_response(event=None):
    """
    Exécuté UNIQUEMENT à la fin de l'exécution d'une commande.
    C'est ici et seulement ici que les erreurs sont analysées et soulignées.
    """
    global _stderr_buffer, _execution_in_progress
    was_executing = _execution_in_progress
    _execution_in_progress = False

    wb = get_workbench()
    if not wb:
        return

    if not wb.get_option("view.highlight_syntax_errors", True):
        clear_all_highlights()
        _stderr_buffer = ""
        return

    try:
        # 1. Vérification de user_exception (backend CPython standard)
        user_exc = getattr(event, "user_exception", None)
        if not user_exc and hasattr(event, "get"):
            user_exc = event.get("user_exception")

        filename = None
        lineno = None
        col_offset = None
        error_type = None
        error_msg = ""

        if user_exc:
            filename = user_exc.get("filename")
            lineno = user_exc.get("lineno")
            col_offset = user_exc.get("col_offset")
            error_type = user_exc.get("type_name")
            error_msg = user_exc.get("message", "")

            # Si des frames sont listées, chercher une frame correspondant à un fichier ouvert
            items = user_exc.get("items", [])
            if items:
                for item in reversed(items):
                    if len(item) >= 4:
                        fn = item[2]
                        ln = item[3]
                        if fn and is_file_open_in_editors(fn):
                            filename = fn
                            lineno = ln
                            break

        # 2. Vérification du buffer stderr (MicroPython, ou autre backend)
        if not user_exc and _stderr_buffer:
            frames, tb_err_type, tb_err_msg, caret_col = parse_traceback_text(_stderr_buffer)
            if frames:
                chosen_fn, chosen_ln = frames[-1]
                for fn, ln in reversed(frames):
                    if is_file_open_in_editors(fn):
                        chosen_fn, chosen_ln = fn, ln
                        break
                filename = chosen_fn
                lineno = chosen_ln
            if tb_err_type:
                error_type = tb_err_type
            if tb_err_msg:
                error_msg = tb_err_msg
            if col_offset is None and caret_col is not None:
                col_offset = caret_col

        # 3. Application du soulignement si une erreur est présente
        has_error = bool(user_exc or error_type or (lineno is not None and ("Error" in _stderr_buffer or "Exception" in _stderr_buffer)))

        # Ignorer si la commande était une simple commande shell interactive sans script
        shell = get_shell()
        last_main = getattr(shell, "_last_main_file", None) if shell else None
        is_script_run = bool(last_main or (filename and is_file_open_in_editors(filename)) or was_executing)

        if has_error and lineno is not None and is_script_run:
            editor = find_target_editor(filename)
            if editor:
                highlight_error_in_editor(editor, lineno, col_offset, error_type, error_msg)
        else:
            # Exécution normale sans erreur
            clear_all_highlights()

    except Exception as e:
        logger.exception("Erreur dans on_toplevel_response: %s", e)
    finally:
        _stderr_buffer = ""


def bind_widget_events(text_widget):
    """Configure le tag et attache la suppression du soulignement lors de la saisie."""
    if not hasattr(text_widget, "_error_highlighter_bound"):
        text_widget._error_highlighter_bound = True
        setup_tag(text_widget)
        # Supprimer le soulignement dès que le texte est modifié par la frappe
        text_widget.bind("<<TextChange>>", on_text_changed, True)


def on_editor_created(event):
    """Initialise le tag et l'écouteur d'édition lors de la création d'un éditeur."""
    text_widget = getattr(event, "text_widget", None)
    if text_widget:
        bind_widget_events(text_widget)


def on_workbench_ready(event=None):
    """Configure tous les éditeurs ouverts au démarrage."""
    wb = get_workbench()
    if not wb:
        return
    editor_notebook = wb.get_editor_notebook()
    if editor_notebook:
        for editor in editor_notebook.get_all_editors():
            text_widget = editor.get_text_widget()
            if text_widget:
                bind_widget_events(text_widget)


def toggle_highlight():
    """Active ou désactive le soulignement des erreurs après exécution."""
    wb = get_workbench()
    if not wb:
        return
    current = wb.get_option("view.highlight_syntax_errors", True)
    wb.set_option("view.highlight_syntax_errors", not current)
    if not wb.get_option("view.highlight_syntax_errors"):
        clear_all_highlights()


def load_plugin():
    """Point d'entrée du plugin pour Thonny."""
    wb = get_workbench()
    wb.set_default("view.highlight_syntax_errors", True)

    lang = wb.get_option("general.language", "fr_FR")
    label = "Souligner les erreurs d'exécution" if lang.startswith("fr") else "Highlight execution errors"
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

    # Écouteurs de frappe : supprime tout soulignement dès qu'on tape
    wb.bind_class("EditorCodeViewText", "<<TextChange>>", on_text_changed, True)
    wb.bind("EditorTextCreated", on_editor_created, True)

    # Écouteurs d'exécution : capture et souligne UNIQUEMENT après exécution
    wb.bind("CommandAccepted", on_command_accepted, True)
    wb.bind("BackendRestart", on_backend_restart, True)
    wb.bind("ProgramOutput", on_program_output, True)
    wb.bind("ToplevelResponse", on_toplevel_response, True)

    wb.bind("WorkbenchReady", on_workbench_ready, True)

    if getattr(wb, "ready", False):
        on_workbench_ready()

    logger.info("Plugin thonny_error_highlighter (post-execution) prêt.")
