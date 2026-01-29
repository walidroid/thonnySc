from thonny import get_workbench
import tkinter as tk

def init_plugin():
    wb = get_workbench()
    
    # --- DISABLE THONNY DEFAULT AUTOCOMPLETE ---
    # We force disable the built-in autocomplete options
    wb.set_option("edit.tab_complete_in_editor", False)
    wb.set_option("edit.tab_complete_in_shell", False)
    
    wb.bind("WorkbenchReady", on_ready)
    wb.bind("EditorTextCreated", on_editor_created)
    print("✅ Plugin Snippets & Autoclose Intelligent chargé")

def on_ready(event):
    wb = get_workbench()
    editor_notebook = wb.get_editor_notebook()
    if editor_notebook:
        editor = editor_notebook.get_current_editor()
        if editor:
            text_widget = editor.get_text_widget()
            bind_events(text_widget)
            disable_default_trigger(text_widget)

def on_editor_created(event):
    bind_events(event.text_widget)
    disable_default_trigger(event.text_widget)

def disable_default_trigger(text_widget):
    """
    Unbinds the default Thonny autocomplete trigger (Control-Space)
    so only our plugin logic runs (or nothing runs).
    """
    try:
        # Prevent Thonny from launching its own completion popup
        text_widget.unbind("<Control-space>")
        # Also try unbinding from the class level just in case, though risky if used by others
        # text_widget.unbind_class("EditorText", "<Control-space>") 
    except Exception:
        pass

def bind_events(text_widget):
    # --- 1. GESTION PRIORITAIRE (POUR BACKSPACE) ---
    # Thonny intercepte souvent BackSpace. Pour passer DEVANT lui, 
    # on ajoute un tag personnalisé en tout premier dans la liste des priorités.
    priority_tag = "SimpleAutocompletePriority"
    tags = list(text_widget.bindtags())
    
    if priority_tag not in tags:
        # Insertion en position 0 (Priorité absolue)
        tags.insert(0, priority_tag)
        text_widget.bindtags(tuple(tags))
        
        # On lie BackSpace à ce tag spécial
        # bind_class s'applique à ce tag partout où il est utilisé
        text_widget.bind_class(priority_tag, "<BackSpace>", on_backspace)

    # --- 2. GESTION NORMALE (INSERTION) ---
    # Pour l'ajout de caractères, l'ordre standard fonctionne bien
    text_widget.bind("<KeyPress>", on_key_press, add="+")
    text_widget.bind("<KeyRelease>", on_key_release_trigger, add="+")

def on_backspace(event):
    """
    Supprime la paire complète (ex: "" ou []) si on efface l'ouvrant.
    S'exécute AVANT le Backspace standard de Thonny.
    """
    text_widget = event.widget
    
    try:
        # On regarde ce qui entoure le curseur
        # insert-1c = le caractère qu'on va effacer (gauche)
        # insert = le caractère juste après (droite)
        prev_char = text_widget.get("insert-1c", "insert")
        next_char = text_widget.get("insert", "insert+1c")
    except:
        return None

    # Liste des paires à gérer
    pairs = {"(": ")", "[": "]", "'": "'", '"': '"', "{": "}"}
    
    # Si on est pile au milieu d'une paire vide (ex: "|")
    if prev_char in pairs and next_char == pairs[prev_char]:
        # On supprime MANUELLEMENT les deux caractères
        text_widget.delete("insert-1c", "insert+1c")
        
        # IMPORTANT : "break" empêche Thonny d'exécuter son propre Backspace ensuite
        # (ce qui éviterait une double suppression ou des erreurs)
        return "break"
        
    # Si la condition n'est pas remplie, on laisse Thonny faire son travail normal
    return None

def on_key_release_trigger(event):
    """Vérifie et remplace le mot-clé immédiatement après la frappe"""
    text = event.widget
    
    # Optimisation : On ne vérifie que si nécessaire
    if not event.char or (not event.char.isalnum() and event.char not in [" ", "_"]):
        return

    if text.index("insert") == "1.0":
        return

    cursor_pos = text.index("insert")
    line_start = text.index("insert linestart")
    line_text = text.get(line_start, cursor_pos)
    
    # Dictionnaire des raccourcis
    snippets = {
        "for":     ("for i in range():", 2),
        "while":   ("while :", 1),
        "if":      ("if :", 1),
        "elif":    ("elif :", 1),
        "else":    ("else :", 0),
        "def":     ("def ():", 3),
        "true":    ("True", 0),
        "false":   ("False", 0),
        "print":   ("print()", 1),
        "input":   ("input()", 1),
        "randint": ("randint(,)", 2),
        "numpy":   ("numpy import array ", 0),
        "random":  ("random import randint ", 0),
        "set":     ("setText()", 1)
    }
    
    sorted_keys = sorted(snippets.keys(), key=len, reverse=True)
    
    match = None
    for key in sorted_keys:
        if line_text.endswith(key):
            # Vérification frontière (mot entier)
            start_index = len(line_text) - len(key)
            if start_index > 0:
                char_before = line_text[start_index - 1]
                if char_before.isalnum() or char_before == "_":
                    continue 
            
            match = key
            break
            
    if match:
        content, back_step = snippets[match]
        start_delete = f"insert-{len(match)}c"
        text.delete(start_delete, "insert")
        text.insert("insert", content)
        if back_step > 0:
            text.mark_set("insert", f"insert-{back_step}c")

def on_key_press(event):
    """
    Gère la fermeture automatique intelligente.
    """
    char = event.char
    text_widget = event.widget
    pairs = {"(": ")", "[": "]", "'": "'", '"': '"'}
    
    if char in pairs:
        # --- 1. Vérification du SUIVANT ---
        try:
            next_char = text_widget.get("insert", "insert+1c")
        except:
            next_char = ""
            
        allowed_followers = ["", "\n", " ", "\t", ")", "]", "}", ",", ":", ";"]
        
        if next_char not in allowed_followers:
             return None 
        
        # --- 2. Vérification du PRÉCÉDENT ---
        if char in ['"', "'"]:
            try:
                prev_char = text_widget.get("insert-1c", "insert")
            except:
                prev_char = ""
            
            if prev_char.isalnum() or prev_char == "_":
                is_prefix = False
                if prev_char.lower() in ['f', 'r', 'b', 'u']:
                    try:
                        prev_prev = text_widget.get("insert-2c", "insert-1c")
                        if not prev_prev.isalnum() and prev_prev != "_":
                            is_prefix = True
                    except:
                        is_prefix = True
                
                if not is_prefix:
                    return None

        text_widget.insert("insert", char + pairs[char])
        text_widget.mark_set("insert", "insert-1c")
        return "break"
