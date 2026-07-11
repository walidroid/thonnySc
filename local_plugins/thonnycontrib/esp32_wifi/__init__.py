"""
ESP32 Wi-Fi Configuration Wizard for MicroPython in ThonnySc.
Provides an interactive GUI to scan local networks, test connections,
and write auto-connecting scripts to the ESP32 filesystem.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from thonny import get_workbench, get_runner
from thonny.languages import tr
from thonny.common import ToplevelCommand, InlineCommand


class WifiWizardDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title(tr("Assistant Wi-Fi ESP32"))
        
        # Center the dialog relative to Thonny main window
        self.geometry("450x380")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        
        # Internal states
        self.scanned_ssids = []
        self.accumulated_scan_output = ""
        self.accumulated_connect_output = ""
        self.test_success = False
        self.test_ip = ""
        self.scan_in_progress = False
        self.connect_in_progress = False
        
        self._build_ui()
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        # Main margins frame
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill="both", expand=True)
        
        # Header title
        title_lbl = ttk.Label(
            main_frame, 
            text="Configuration Wi-Fi pour MicroPython (ESP32)", 
            font=("Segoe UI", 11, "bold")
        )
        title_lbl.pack(pady=(0, 15))
        
        # 1. SSID Frame
        ssid_frame = ttk.LabelFrame(main_frame, text=" 1. Réseau Wi-Fi ", padding="10")
        ssid_frame.pack(fill="x", pady=(0, 10))
        
        combo_frame = ttk.Frame(ssid_frame)
        combo_frame.pack(fill="x")
        
        self.ssid_var = tk.StringVar()
        self.ssid_combo = ttk.Combobox(
            combo_frame, 
            textvariable=self.ssid_var, 
            values=self.scanned_ssids
        )
        self.ssid_combo.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.scan_btn = ttk.Button(
            combo_frame, 
            text="Scanner", 
            command=self.start_wifi_scan
        )
        self.scan_btn.pack(side="right")
        
        # 2. Password Frame
        pass_frame = ttk.LabelFrame(main_frame, text=" 2. Clé de Sécurité (Mot de Passe) ", padding="10")
        pass_frame.pack(fill="x", pady=(0, 10))
        
        self.pass_var = tk.StringVar()
        self.pass_entry = ttk.Entry(
            pass_frame, 
            textvariable=self.pass_var, 
            show="*"
        )
        self.pass_entry.pack(fill="x", pady=(0, 5))
        
        self.show_pass_var = tk.BooleanVar(value=False)
        self.show_pass_chk = ttk.Checkbutton(
            pass_frame, 
            text="Afficher le mot de passe", 
            variable=self.show_pass_var,
            command=self.toggle_password_visibility
        )
        self.show_pass_chk.pack(anchor="w")
        
        # 3. Actions buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill="x", pady=(10, 10))
        
        self.test_btn = ttk.Button(
            action_frame, 
            text="Tester la Connexion", 
            command=self.start_connection_test
        )
        self.test_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.save_btn = ttk.Button(
            action_frame, 
            text="Enregistrer sur l'ESP32", 
            command=self.save_and_configure
        )
        self.save_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        # 4. Status Panel
        status_frame = ttk.LabelFrame(main_frame, text=" Statut / Log ", padding="10")
        status_frame.pack(fill="both", expand=True)
        
        self.status_lbl = ttk.Label(
            status_frame, 
            text="Prêt. Sélectionnez un réseau ou cliquez sur Scanner.", 
            wraplength=380,
            justify="left"
        )
        self.status_lbl.pack(fill="both", expand=True)

    def toggle_password_visibility(self):
        if self.show_pass_var.get():
            self.pass_entry.config(show="")
        else:
            self.pass_entry.config(show="*")

    def start_wifi_scan(self):
        if self.scan_in_progress or self.connect_in_progress:
            return
        
        if not get_runner().is_waiting_toplevel_command():
            messagebox.showwarning(
                tr("Terminal occupé"),
                tr("Veuillez arrêter le programme en cours dans le terminal avant de scanner.")
            )
            return
            
        self.scan_in_progress = True
        self.scan_btn.config(state="disabled")
        self.test_btn.config(state="disabled")
        self.save_btn.config(state="disabled")
        self.status_lbl.config(text="Balayage des réseaux Wi-Fi sur l'ESP32 en cours... Veuillez patienter.")
        
        self.scanned_ssids.clear()
        self.ssid_combo["values"] = []
        self.accumulated_scan_output = ""
        
        # Bind events
        get_workbench().bind("ProgramOutput", self.on_scan_output, True)
        get_workbench().bind("ToplevelResponse", self.on_scan_complete, True)
        
        # Execute scanning script in backend
        scan_code = (
            "import network; "
            "w = network.WLAN(network.STA_IF); "
            "w.active(True); "
            "[print('SSID_FOUND:' + n[0].decode('utf-8')) for n in w.scan() if n[0]]"
        )
        get_runner().send_command(ToplevelCommand("execute_source", source=scan_code))

    def on_scan_output(self, event):
        self.accumulated_scan_output += event.text
        while "\n" in self.accumulated_scan_output:
            line, self.accumulated_scan_output = self.accumulated_scan_output.split("\n", 1)
            line = line.strip()
            if line.startswith("SSID_FOUND:"):
                ssid = line[len("SSID_FOUND:"):].strip()
                if ssid and ssid not in self.scanned_ssids:
                    self.scanned_ssids.append(ssid)
                    self.ssid_combo["values"] = self.scanned_ssids
                    if not self.ssid_var.get():
                        self.ssid_var.set(ssid)

    def on_scan_complete(self, event):
        self.cleanup_bindings()
        self.scan_in_progress = False
        self.scan_btn.config(state="normal")
        self.test_btn.config(state="normal")
        self.save_btn.config(state="normal")
        
        if self.scanned_ssids:
            self.status_lbl.config(
                text=f"Balayage terminé. {len(self.scanned_ssids)} réseaux trouvés.\n"
                     f"Choisissez un SSID et saisissez le mot de passe."
            )
        else:
            self.status_lbl.config(
                text="Aucun réseau Wi-Fi détecté. Assurez-vous que l'ESP32 est allumé et à proximité."
            )

    def start_connection_test(self):
        if self.scan_in_progress or self.connect_in_progress:
            return
            
        ssid = self.ssid_var.get().strip()
        password = self.pass_var.get()
        
        if not ssid:
            messagebox.showwarning(tr("Champs requis"), tr("Veuillez saisir ou sélectionner un réseau (SSID)."))
            return
            
        if not get_runner().is_waiting_toplevel_command():
            messagebox.showwarning(
                tr("Terminal occupé"),
                tr("Veuillez arrêter le programme en cours dans le terminal avant de tester.")
            )
            return
            
        self.connect_in_progress = True
        self.scan_btn.config(state="disabled")
        self.test_btn.config(state="disabled")
        self.save_btn.config(state="disabled")
        self.status_lbl.config(text=f"Tentative de connexion à '{ssid}' (10 sec max)... Veuillez patienter.")
        
        self.accumulated_connect_output = ""
        self.test_success = False
        self.test_ip = ""
        
        # Bind events
        get_workbench().bind("ProgramOutput", self.on_connect_output, True)
        get_workbench().bind("ToplevelResponse", self.on_connect_complete, True)
        
        # Escape quotes
        s_escaped = ssid.replace("'", "\\'")
        p_escaped = password.replace("'", "\\'")
        
        connect_code = f"""
import network
import time
w = network.WLAN(network.STA_IF)
w.active(True)
w.connect('{s_escaped}', '{p_escaped}')
connected = False
for _ in range(10):
    if w.isconnected():
        connected = True
        break
    time.sleep(1)
if connected:
    print("CONNECT_RESULT:SUCCESS:" + w.ifconfig()[0])
else:
    print("CONNECT_RESULT:FAILED")
"""
        get_runner().send_command(ToplevelCommand("execute_source", source=connect_code))

    def on_connect_output(self, event):
        self.accumulated_connect_output += event.text
        while "\n" in self.accumulated_connect_output:
            line, self.accumulated_connect_output = self.accumulated_connect_output.split("\n", 1)
            line = line.strip()
            if "CONNECT_RESULT:SUCCESS:" in line:
                self.test_success = True
                self.test_ip = line.split("CONNECT_RESULT:SUCCESS:")[1].strip()
            elif "CONNECT_RESULT:FAILED" in line:
                self.test_success = False

    def on_connect_complete(self, event):
        self.cleanup_bindings()
        self.connect_in_progress = False
        self.scan_btn.config(state="normal")
        self.test_btn.config(state="normal")
        self.save_btn.config(state="normal")
        
        if self.test_success:
            self.status_lbl.config(
                text=f"Connexion RÉUSSIE sur la carte ESP32 !\n"
                     f"Adresse IP : {self.test_ip}\n"
                     f"Vous pouvez maintenant enregistrer la configuration sur la carte."
            )
        else:
            self.status_lbl.config(
                text="ÉCHEC de la connexion.\n"
                     "Veuillez vérifier le SSID et le mot de passe saisis."
            )

    def save_and_configure(self):
        if self.scan_in_progress or self.connect_in_progress:
            return
            
        ssid = self.ssid_var.get().strip()
        password = self.pass_var.get()
        
        if not ssid:
            messagebox.showwarning(tr("Champs requis"), tr("Veuillez saisir ou sélectionner un réseau (SSID)."))
            return
            
        if not get_runner().ready_for_remote_file_operations(show_message=True):
            return
            
        # Escape quotes
        s_escaped = ssid.replace("'", "\\'")
        p_escaped = password.replace("'", "\\'")
        
        wifi_code = f"""# Fichier de configuration Wi-Fi auto-généré
def connect():
    import network
    import time
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connexion au reseau '{s_escaped}'...")
        wlan.connect('{s_escaped}', '{p_escaped}')
        for _ in range(10):
            if wlan.isconnected():
                break
            time.sleep(1)
    if wlan.isconnected():
        print("Wi-Fi Connecte! IP:", wlan.ifconfig()[0])
    else:
        print("Echec de la connexion Wi-Fi!")

connect()
"""
        
        self.status_lbl.config(text="Écriture de wifi.py sur l'ESP32...")
        self.update()
        
        # Save wifi.py
        try:
            write_res = get_runner().send_command_and_wait(
                InlineCommand(
                    "write_file",
                    path="wifi.py",
                    content_bytes=wifi_code.encode("utf-8"),
                    blocking=True,
                    description="Sauvegarde de wifi.py"
                ),
                dialog_title="Enregistrement"
            )
            if "error" in write_res:
                messagebox.showerror(tr("Erreur"), f"Impossible d'écrire wifi.py : {write_res['error']}")
                return
        except Exception as e:
            messagebox.showerror(tr("Erreur"), f"Erreur lors de la sauvegarde de wifi.py : {e}")
            return
            
        # Read and modify boot.py
        self.status_lbl.config(text="Lecture de boot.py sur l'ESP32...")
        self.update()
        
        boot_content = ""
        try:
            read_res = get_runner().send_command_and_wait(
                InlineCommand("read_file", path="boot.py", description="Lecture de boot.py"),
                dialog_title="Lecture"
            )
            if "content_bytes" in read_res:
                boot_content = read_res["content_bytes"].decode("utf-8")
        except Exception:
            pass # File doesn't exist, which is fine, we'll write a new one
            
        if "import wifi" not in boot_content:
            self.status_lbl.config(text="Configuration du démarrage automatique (boot.py)...")
            self.update()
            
            if boot_content and not boot_content.endswith("\n"):
                boot_content += "\n"
            boot_content += (
                "\n# --- Wi-Fi Auto-connect ---\n"
                "try:\n"
                "    import wifi\n"
                "except Exception as e:\n"
                "    print('Erreur Wi-Fi:', e)\n"
            )
            
            try:
                write_res = get_runner().send_command_and_wait(
                    InlineCommand(
                        "write_file",
                        path="boot.py",
                        content_bytes=boot_content.encode("utf-8"),
                        blocking=True,
                        description="Mise a jour de boot.py"
                    ),
                    dialog_title="Sauvegarde de boot.py"
                )
                if "error" in write_res:
                    messagebox.showerror(tr("Erreur"), f"Impossible de modifier boot.py : {write_res['error']}")
                    return
            except Exception as e:
                messagebox.showerror(tr("Erreur"), f"Erreur lors de la modification de boot.py : {e}")
                return
                
        self.status_lbl.config(text="Configuration Wi-Fi enregistrée avec succès !")
        messagebox.showinfo(
            tr("Succès"),
            tr("La configuration Wi-Fi a été enregistrée avec succès sur la carte ESP32 !")
        )

    def cleanup_bindings(self):
        try:
            get_workbench().unbind("ProgramOutput", self.on_scan_output)
        except Exception:
            pass
        try:
            get_workbench().unbind("ToplevelResponse", self.on_scan_complete)
        except Exception:
            pass
        try:
            get_workbench().unbind("ProgramOutput", self.on_connect_output)
        except Exception:
            pass
        try:
            get_workbench().unbind("ToplevelResponse", self.on_connect_complete)
        except Exception:
            pass

    def on_close(self):
        self.cleanup_bindings()
        self.destroy()


def _open_wifi_wizard():
    dialog = WifiWizardDialog(get_workbench())
    dialog.focus_set()


def load_plugin() -> None:
    get_workbench().add_command(
        "OpenESP32WifiWizard",
        "tools",
        tr("Assistant Wi-Fi ESP32..."),
        _open_wifi_wizard,
        group=80,
    )
