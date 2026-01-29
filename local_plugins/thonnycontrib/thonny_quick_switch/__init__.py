from thonny import get_workbench
import tkinter as tk

def get_colors():
    """Définit les couleurs selon l'interprète actif"""
    current = get_workbench().get_option("run.backend_name")
    if current == "ESP32":
        return "#fff4e6"  # Orange très pâle (ESP32)
    return "#f0f7ff"      # Bleu très pâle (Python)

def apply_theme_to_editors():
    """Applique la couleur de fond à tous les éditeurs ouverts"""
    wb = get_workbench()
    bg_color = get_colors()
    
    # On parcourt tous les éditeurs ouverts
    for editor in wb.get_editor_notebook().get_all_editors():
        text_widget = editor.get_text_widget()
        text_widget.configure(background=bg_color)

def set_interpreter(backend_id):
    """Change l'interpréteur et rafraîchit l'interface"""
    wb = get_workbench()
    wb.set_option("run.backend_name", backend_id)
    try:
        wb.restart_backend(clean=True)
    except:
        pass
    # Appliquer le changement visuel immédiatement
    apply_theme_to_editors()

def load_plugin():
    wb = get_workbench()

    def create_custom_menu():
        try:
            # Récupération sécurisée de la barre de menu
            menu_path = wb.cget("menu")
            if not menu_path:
                wb.after(200, create_custom_menu)
                return
                
            main_menubar = wb.nametowidget(menu_path)
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
    wb.bind("BackendRestarted", lambda e: apply_theme_to_editors(), True)
