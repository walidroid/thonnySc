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
        get_workbench().get_menu("pyqt5").delete(1, "end")
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
            '0.0','from PyQt5.uic import loadUi\n'+
            'from PyQt5.QtWidgets import QApplication\n'+
            '\n'+mytxt+'\n'+
            'app = QApplication([])\n'+
            'windows = loadUi ("'+ path +'")\n'+
            'windows.show()\n'+
            btnstxt+'\n'
            'app.exec_()'
            )
def find_qt_designer():
    """Find Qt Designer executable in common locations."""
    import shutil
    import zipfile
    
    # Check PATH using shutil.which
    designer_qt5 = shutil.which("pyqt5_qt5_designer.exe")
    if designer_qt5:
        return designer_qt5
    
    designer_in_path = shutil.which("designer.exe")
    if designer_in_path:
        return designer_in_path

    # Check for bundled version first (if running as frozen app)
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
        bundled_designer = os.path.join(app_dir, "Qt Designer", "designer.exe")
        if os.path.isfile(bundled_designer):
            return bundled_designer
            
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
    Opens Qt Designer with the current UI file.
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
        # Use os.startfile for true process independence (like double-clicking)
        # This completely detaches Qt Designer from Thonny
        if qt_ui_file:
            # For opening with a file, we need to use the 'open' verb with the file
            # and let Windows associate it with the designer, OR use subprocess with shell=True
            os.startfile(qt_ui_file, 'open')
            print(f"✓ Ouvert {qt_ui_file} dans Qt Designer")
        else:
            os.startfile(designer_exe)
            print(f"✓ Qt Designer lancé")
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
        "pyqt5",
        tr("Ajouter code PyQt5"),
        add_pyqt_code,
	    default_sequence=select_sequence("<Control-Shift-B>", "<Command-Shift-B>"),
        include_in_toolbar = True,
	    caption  = "PyQt",
        image = image_path
    )
    get_workbench().add_command(
        "pyqt5_open_in_designer",
        "pyqt5",
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
