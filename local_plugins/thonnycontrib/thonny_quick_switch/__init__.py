from thonny import get_workbench
from thonny.languages import tr
import tkinter as tk
import tkinter.messagebox as mb


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


def open_interpreter_config():
    """Ouvre la fenêtre de configuration de l'interpréteur actuel"""
    wb = get_workbench()
    if wb:
        wb.show_options("interpreter")


def open_esp32_config():
    """Bascule vers le mode ESP32 et ouvre directement sa configuration (choix du port COM, etc.)"""
    wb = get_workbench()
    if not wb:
        return
    current = wb.get_option("run.backend_name")
    if current != "ESP32":
        set_interpreter("ESP32")
    wb.show_options("interpreter")


def open_esp32_flasher():
    """Ouvre l'assistant esptool pour flasher le firmware MicroPython sur la carte ESP32"""
    wb = get_workbench()
    if not wb:
        return
    try:
        from thonny.plugins.micropython.esptool_dialog import try_launch_esptool_dialog
        try_launch_esptool_dialog(wb, "MicroPython")
    except Exception as e:
        mb.showerror("Erreur", f"Impossible d'ouvrir l'outil de flashage : {e}")


def show_esp32_guide():
    """Affiche le guide etape par etape pour configurer et flasher l'ESP32"""
    wb = get_workbench()
    lang = wb.get_option("general.language", "fr_FR") if wb else "fr_FR"
    if lang.startswith("fr"):
        msg = (
            "Guide pour configurer et installer MicroPython sur ESP32 :\n\n"
            "1- Laisse ta carte branchée en USB.\n"
            "2- Dans ton installateur, garde :\n"
            "   MicroPython family: ESP32\n"
            "   variant: Espressif • ESP32 / WROOM\n"
            "   Target: COM5 (ou le port COM de ta carte)\n"
            "   ☑ Erase all flash\n"
            "3- Clique sur Installer.\n"
            "4- Dès que la connexion commence, maintiens le bouton BOOT de l'ESP32 enfoncé.\n"
            "5- Garde-le appuyé pendant quelques secondes.\n"
            "6- Relâche BOOT lorsque l'installation commence réellement.\n\n"
            "Voulez-vous ouvrir l'installateur (esptool) maintenant ?"
        )
        title = "Guide de configuration ESP32"
    else:
        msg = (
            "Steps to configure and install MicroPython on ESP32:\n\n"
            "1- Keep your board connected via USB.\n"
            "2- In your installer, keep:\n"
            "   MicroPython family: ESP32\n"
            "   variant: Espressif • ESP32 / WROOM\n"
            "   Target: COM5 (or your detected COM port)\n"
            "   ☑ Erase all flash\n"
            "3- Click Install.\n"
            "4- As soon as connection begins, press and hold the BOOT button on the ESP32.\n"
            "5- Keep it pressed for a few seconds.\n"
            "6- Release BOOT when the installation actually begins.\n\n"
            "Would you like to open the installer (esptool) now?"
        )
        title = "ESP32 Configuration Guide"

    if mb.askyesno(title, msg):
        open_esp32_flasher()


def get_menu_labels():
    wb = get_workbench()
    lang = wb.get_option("general.language", "fr_FR") if wb else "fr_FR"
    if lang.startswith("fr"):
        return {
            "menu_title": "Interpréteur",
            "py_mode": "Mode : Python 3",
            "esp_mode": "Mode : ESP32",
            "config_interpreter": "Configurer l'interpréteur...",
            "config_esp32": "Configurer la carte ESP32...",
            "flash_esp32": "Flasher le firmware ESP32 (esptool)...",
            "guide_esp32": "Guide de configuration ESP32 (BOOT)...",
        }
    else:
        return {
            "menu_title": "Interpreter",
            "py_mode": "Mode: Python 3",
            "esp_mode": "Mode: ESP32",
            "config_interpreter": "Configure interpreter...",
            "config_esp32": "Configure ESP32 board...",
            "flash_esp32": "Flash ESP32 firmware (esptool)...",
            "guide_esp32": "ESP32 setup guide (BOOT button)...",
        }


def load_plugin():
    wb = get_workbench()

    def create_custom_menu():
        try:
            menu_path = wb.cget("menu")
            if not menu_path:
                wb.after(200, create_custom_menu)
                return
                
            main_menubar = wb.nametowidget(menu_path)
            labels = get_menu_labels()
            
            # Check if Interpréteur menu already exists to prevent duplicates
            try:
                for i in range(main_menubar.index("end") + 1):
                    if main_menubar.type(i) == "cascade" and main_menubar.entrycget(i, "label") in ("Interpréteur", "Interpreter"):
                        return
            except Exception:
                pass
                
            mode_menu = tk.Menu(main_menubar, tearoff=0)
            
            def refresh_labels():
                """Met à jour les coches ✓ et les options au clic sur le menu"""
                mode_menu.delete(0, "end")
                current = wb.get_option("run.backend_name")
                lbls = get_menu_labels()
                
                py_prefix = "✓ " if current == "LocalCPython" else "    "
                mode_menu.add_command(
                    label=f"{py_prefix}{lbls['py_mode']}", 
                    command=lambda: set_interpreter("LocalCPython")
                )
                
                esp_prefix = "✓ " if current == "ESP32" else "    "
                mode_menu.add_command(
                    label=f"{esp_prefix}{lbls['esp_mode']}", 
                    command=lambda: set_interpreter("ESP32")
                )

                mode_menu.add_separator()

                # Option pour configurer l'interpréteur
                mode_menu.add_command(
                    label=lbls["config_interpreter"],
                    command=open_interpreter_config
                )

                # Option spécifique pour configurer la carte ESP32 (sélection port COM, etc.)
                mode_menu.add_command(
                    label=lbls["config_esp32"],
                    command=open_esp32_config
                )

                # Option pour flasher le firmware MicroPython sur la carte ESP32
                mode_menu.add_command(
                    label=lbls["flash_esp32"],
                    command=open_esp32_flasher
                )

                # Guide d'aide pas-à-pas pour ESP32 (BOOT)
                mode_menu.add_command(
                    label=lbls["guide_esp32"],
                    command=show_esp32_guide
                )

            mode_menu.configure(postcommand=refresh_labels)
            main_menubar.add_cascade(label=labels["menu_title"], menu=mode_menu)
            
            # Appliquer la couleur au démarrage
            apply_theme_to_editors()
            
        except Exception:
            pass

    # Initialisation du menu personnalisé
    wb.after(500, create_custom_menu)
    
    # Enregistrer également les commandes dans le workbench (outils / raccourcis)
    try:
        lbls = get_menu_labels()
        wb.add_command(
            "configure_interpreter_quick",
            "tools",
            lbls["config_interpreter"],
            open_interpreter_config,
            group=75,
        )
        wb.add_command(
            "configure_esp32_quick",
            "tools",
            lbls["config_esp32"],
            open_esp32_config,
            group=76,
        )
        wb.add_command(
            "flash_esp32_quick",
            "tools",
            lbls["flash_esp32"],
            open_esp32_flasher,
            group=77,
        )
        wb.add_command(
            "guide_esp32_quick",
            "tools",
            lbls["guide_esp32"],
            show_esp32_guide,
            group=78,
        )
    except Exception:
        pass
    
    # S'assurer que les nouveaux fichiers créés prennent aussi la couleur
    wb.bind("EditorTextCreated", lambda e: apply_theme_to_editors(), True)
    # S'assurer que le thème est mis à jour quand le moteur redémarre
    wb.bind("BackendRestart", lambda e: apply_theme_to_editors(), True)
