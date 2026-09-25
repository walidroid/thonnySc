from thonny import get_workbench
import tkinter as tk

def get_colors():
    """Définit les couleurs selon l'interprète actif et le thème (clair ou sombre)"""
    wb = get_workbench()
    current = wb.get_option("run.backend_name") if wb else "LocalCPython"
    
    # Check if the active theme is a dark theme
    is_dark = False
    try:
        from thonny.codeview import get_syntax_options_for_tag
        text_opts = get_syntax_options_for_tag("TEXT")
        bg = text_opts.get("background", "#ffffff")
        if bg.startswith("#") and len(bg) == 7:
            r, g, b = int(bg[1:3], 16), int(bg[3:5], 16), int(bg[5:7], 16)
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            if luminance < 128:
                is_dark = True
    except Exception:
        pass

    if is_dark:
        return "#2d241c" if current == "ESP32" else "#1c242d"
    else:
        return "#fff4e6" if current == "ESP32" else "#f0f7ff"

def apply_theme_to_editors():
    """Applique la couleur de fond à tous les éditeurs ouverts"""
    wb = get_workbench()
    if not wb:
        return
    bg_color = get_colors()
    
    try:
        notebook = wb.get_editor_notebook()
        if notebook:
            for editor in notebook.get_all_editors():
                try:
                    text_widget = editor.get_text_widget()
                    text_widget.configure(background=bg_color)
                except Exception:
                    pass
    except Exception:
        pass

def set_interpreter(backend_id):
    """Change l'interpréteur et rafraîchit l'interface"""
    wb = get_workbench()
    if not wb:
        return
    wb.set_option("run.backend_name", backend_id)
    try:
        wb.restart_backend(clean=True)
    except Exception:
        pass
    # Appliquer le changement visuel immédiatement
    apply_theme_to_editors()

def load_plugin():
    wb = get_workbench()

    def create_custom_menu():
        try:
            menu_path = wb.cget("menu")
            if not menu_path:
                wb.after(200, create_custom_menu)
                return
                
            main_menubar = wb.nametowidget(menu_path)
            
            # Check if Interpréteur menu already exists to prevent duplicates
            try:
                for i in range(main_menubar.index("end") + 1):
                    if main_menubar.type(i) == "cascade" and main_menubar.entrycget(i, "label") == "Interpréteur":
                        return
            except Exception:
                pass
                
            mode_menu = tk.Menu(main_menubar, tearoff=0)
            
            def refresh_labels():
                """Met à jour les coches ✓ au clic sur le menu"""
                mode_menu.delete(0, "end")
                current = wb.get_option("run.backend_name")
                
                py_prefix = "✓ " if current == "LocalCPython" else "    "
                mode_menu.add_command(
                    label=f"{py_prefix}Mode : Python 3", 
                    command=lambda: set_interpreter("LocalCPython")
                )
                
                esp_prefix = "✓ " if current == "ESP32" else "    "
                mode_menu.add_command(
                    label=f"{esp_prefix}Mode : ESP32", 
                    command=lambda: set_interpreter("ESP32")
                )

            mode_menu.configure(postcommand=refresh_labels)
            main_menubar.add_cascade(label="Interpréteur", menu=mode_menu)
            
            # Appliquer la couleur au démarrage
            apply_theme_to_editors()
            
        except Exception:
            pass

    # Initialisation
    wb.after(500, create_custom_menu)
    
    # S'assurer que les nouveaux fichiers créés prennent aussi la couleur
    wb.bind("EditorTextCreated", lambda e: apply_theme_to_editors(), True)
    # S'assurer que le thème est mis à jour quand le moteur redémarre
    wb.bind("BackendRestart", lambda e: apply_theme_to_editors(), True)
