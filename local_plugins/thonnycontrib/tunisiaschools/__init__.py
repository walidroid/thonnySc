import os
import subprocess
import sys
from datetime import date
from thonny import get_workbench
from thonny.languages import tr
from thonny.ui_utils import select_sequence,askopenfilename
# from .UIViewer import UiViewerPlugin

from xml.dom import minidom
global qt_ui_file
qt_ui_file =""

def usefull_commands(w):
    def add_cmd(w ,id, label , fct ):
        get_workbench()._publish_command(
                    "pyqt_text_"+w.attributes['name'].value+id,
                    "pyqt5",
                    label +w.attributes['name'].value ,
                    lambda: get_workbench().get_editor_notebook().get_current_editor().get_code_view().text.insert('insert',"windows."+w.attributes['name'].value +fct)
                )
    add_cmd(w,"text","Contenu de ",".text()")
    add_cmd(w,"settext","Changer le contenu de ",".setText()")
    add_cmd(w,"clear","Effacer le contenu de ",".clear()")
    add_cmd(w,"show","Afficher ",".show()")

    
    
def add_pyqt_code():
    
    btnstxt = ""
    mytxt = ""
    path = askopenfilename(
                filetypes=[("Fichiers UI", ".ui"), (tr("Tous les fichiers"), ".*")], parent=get_workbench()
            )
    if path:
        global qt_ui_file
        qt_ui_file = path
        # Menu cleanup removed - commands are now in the Tools menu
        # get_workbench().get_view("UiViewerPlugin").load_new_ui_file(path)
        # get_workbench().show_view("UiViewerPlugin",True)
        file = minidom.parse(path)
        widgets = file.getElementsByTagName('widget')
        for w in widgets:
            if w.attributes['class'].value == "QPushButton" : #Bouton
                btnstxt = btnstxt + "windows."+w.attributes['name'].value +".clicked.connect ( "+  w.attributes['name'].value +"_click )\n"
                mytxt = mytxt + "def "+  w.attributes['name'].value +"_click():\n    pass\n" 
            elif w.attributes['class'].value in [ "QLineEdit", "QLabel"] : #Zone de texte ou Libellé
                #btnstxt = btnstxt + "windows."+w.attributes['name'].value +".clicked.connect ( "+  w.attributes['name'].value +"_click )"+chr(13)+chr(10)
                usefull_commands(w)
                
            

        get_workbench().get_editor_notebook().get_current_editor().get_code_view().text.insert(
            '0.0',
            'import sys\n'
            'import faulthandler\n'
            'import traceback\n'
            'from PyQt5.uic import loadUi\n'
            'from PyQt5.QtWidgets import QApplication\n'
            '\n'
            '# Activer faulthandler pour afficher les erreurs natives (segfault)\n'
            'faulthandler.enable()\n'
            '\n'
            '# Intercepter les exceptions non gérées dans la boucle Qt\n'
            'def _excepthook(exc_type, exc_value, exc_tb):\n'
            '    traceback.print_exception(exc_type, exc_value, exc_tb)\n'
            '    sys.exit(1)\n'
            'sys.excepthook = _excepthook\n'
            '\n'
            + mytxt + '\n'
            'try:\n'
            '    app = QApplication([])\n'
            '    windows = loadUi("' + path + '")\n'
            '    windows.show()\n'
            '    ' + btnstxt.replace('\n', '\n    ') + '\n'
            '    app.exec_()\n'
            'except Exception as e:\n'
            '    print(f"Erreur: {type(e).__name__}: {e}", file=sys.stderr)\n'
            '    traceback.print_exc()\n'
            '    sys.exit(1)\n'
            )
def find_qt_designer():
    """Find Qt Designer executable in common locations."""
    import shutil
    import zipfile
    
    # Check for bundled version first (if running as frozen app)
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
        
        # Check qt5_applications standalone designer FIRST (ThonnyTN approach - no version mismatch)
        qt5_apps_designer = os.path.join(app_dir, "Python", "Lib", "site-packages", "qt5_applications", "Qt", "bin", "designer.exe")
        if os.path.isfile(qt5_apps_designer):
            return qt5_apps_designer
        
        # Check PyQt5 bundled designer as fallback
        pyqt5_designer = os.path.join(app_dir, "Python", "Lib", "site-packages", "PyQt5", "Qt5", "bin", "designer.exe")
        if os.path.isfile(pyqt5_designer):
            return pyqt5_designer
        
        # Check dedicated Qt Designer folder
        bundled_designer = os.path.join(app_dir, "Qt Designer", "designer.exe")
        if os.path.isfile(bundled_designer):
            return bundled_designer
    
    # Check PATH - look for qt5_applications designer first
    designer_qt5 = shutil.which("pyqt5_qt5_designer.exe")
    if designer_qt5:
        return designer_qt5
    
    designer_in_path = shutil.which("designer.exe")
    if designer_in_path:
        return designer_in_path
            
    # Check project root (for development/portable versions)
    # This file is in local_plugins/thonnycontrib/tunisiaschools/
    # Root is 3 levels up: tunisiaschools -> thonnycontrib -> local_plugins -> thonnySc
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    
    local_designer_dir = os.path.join(project_root, "Qt Designer")
    local_designer_exe = os.path.join(local_designer_dir, "designer.exe")
    
    if os.path.isfile(local_designer_exe):
        return local_designer_exe
        
    # Check for zip file in root if exe is missing
    zip_path = os.path.join(project_root, "qt-designer.zip")
    if os.path.isfile(zip_path):
        try:
            print(f"Extracting {zip_path}...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(project_root)
            
            if os.path.isfile(local_designer_exe):
                print("[OK] Extracted Qt Designer successfully")
                return local_designer_exe
        except Exception as e:
            print(f"[ERROR] Failed to extract qt-designer.zip: {e}")
    
    # Try common install locations
    locations = [
        "C:\\Program Files (x86)\\Qt Designer\\designer.exe",
        "C:\\Program Files\\Qt Designer\\designer.exe",
    ]
    
    for loc in locations:
        if os.path.isfile(loc):
            return loc
            
    return None

def open_in_designer():
    """
    Opens Qt Designer directly.
    Shows error messages if Qt Designer is not found.
    """
    designer_exe = find_qt_designer()
    
    if not designer_exe:
        try:
            from tkinter import messagebox
            messagebox.showerror(
                "Qt Designer non trouvé",
                "Qt Designer n'a pas été trouvé sur cet ordinateur.\n\n"
                "Pour installer Qt Designer:\n"
                "1. Ouvrez le terminal (cmd)\n"
                "2. Exécutez: pip install pyqt5_qt5_designer\n\n"
                "Ou téléchargez depuis:\n"
                "https://build-system.fman.io/qt-designer-download"
            )
        except:
            print("✗ Erreur: Qt Designer n'a pas été trouvé.")
            print("  Veuillez installer: pip install pyqt5_qt5_designer")
        return False
    
    global qt_ui_file
    try:
        # Always launch designer.exe directly using subprocess
        # This ensures it opens reliably even without file associations
        cmd = [designer_exe]
        if qt_ui_file and os.path.isfile(qt_ui_file):
            cmd.append(qt_ui_file)
            print(f"✓ Ouvert {qt_ui_file} dans Qt Designer")
        else:
            print(f"✓ Qt Designer lancé: {designer_exe}")
        
        # Use subprocess with CREATE_NEW_PROCESS_GROUP to fully detach from Thonny
        subprocess.Popen(
            cmd,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS if sys.platform == 'win32' else 0,
            close_fds=True,
        )
        return True
    except Exception as e:
        try:
            from tkinter import messagebox
            messagebox.showerror(
                "Erreur",
                f"Erreur lors du lancement de Qt Designer:\n{e}"
            )
        except:
            print(f"✗ Erreur lors du lancement de Qt Designer: {e}")
        return False



def load_plugin():
    # get_workbench().add_view(UiViewerPlugin, tr("QT UI Viewer"), "s")
    
    
    image_path = os.path.join(os.path.dirname(__file__), "res", "code-pyqt.png")
    designer_image_path = os.path.join(os.path.dirname(__file__), "res", "qt-designer.png")
	
    get_workbench().add_command(
        "selmen_command",
        "tools",
        tr("Ajouter code PyQt5"),
        add_pyqt_code,
	    default_sequence=select_sequence("<Control-Shift-B>", "<Command-Shift-B>"),
        include_in_toolbar = True,
	    caption  = "PyQt",
        image = image_path
    )
    get_workbench().add_command(
        "pyqt5_open_in_designer",
        "tools",
        tr("Ouvrir dans Designer"),
        open_in_designer,
	    #default_sequence=select_sequence("<Control-Shift-B>", "<Command-Shift-B>"),
        include_in_toolbar = True,
	    caption  = "PyQt",
        image = designer_image_path
    )
    # Changement de dossier de sauvegarde : 

    # en cas ou la date est erroné sur le pc

    cwd = 'C:\\'
    get_workbench().set_local_cwd(cwd)

    # Ne pas ouvrir les derniers fichiers 

    get_workbench().set_option("file.current_file", "")
    get_workbench().set_option("file.open_files", "")
