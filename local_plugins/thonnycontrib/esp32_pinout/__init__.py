"""
ESP32 Pinout View plugin for ThonnySc.
Provides an interactive, color-coded pinout guide for ESP32 boards
with automatic MicroPython code generation and insertion.
"""
import tkinter as tk
from tkinter import ttk
from thonny import get_workbench
from thonny.languages import tr
from thonny.misc_utils import copy_to_clipboard

# Color coding for pin types
PIN_COLORS = {
    "power": "#EF4444",   # Red
    "gnd": "#4B5563",     # Dark Gray
    "gpio": "#10B981",    # Green
    "adc": "#3B82F6",     # Blue
    "dac": "#8B5CF6",     # Purple
    "serial": "#F59E0B",  # Amber/Yellow
    "flash": "#D97706",   # Orange
}

# Detailed capabilities for each pin
PIN_DB_30PIN = {
    # Left Side
    "L1": {"name": "EN", "gpio": None, "type": "power", "desc": "Reset / Enclencher (Bouton EN)"},
    "L2": {"name": "VP", "gpio": 36, "type": "adc", "desc": "GPIO 36 / Entrée Analogique ADC1_CH0 / Capteur Hall"},
    "L3": {"name": "VN", "gpio": 39, "type": "adc", "desc": "GPIO 39 / Entrée Analogique ADC1_CH3 / Capteur Hall"},
    "L4": {"name": "D34", "gpio": 34, "type": "adc", "desc": "GPIO 34 / Entrée Analogique ADC1_CH6 (Entrée seule)"},
    "L5": {"name": "D35", "gpio": 35, "type": "adc", "desc": "GPIO 35 / Entrée Analogique ADC1_CH7 (Entrée seule)"},
    "L6": {"name": "D32", "gpio": 32, "type": "gpio", "desc": "GPIO 32 / ADC1_CH4 / Touch9 / Horloge XTAL"},
    "L7": {"name": "D33", "gpio": 33, "type": "gpio", "desc": "GPIO 33 / ADC1_CH5 / Touch8 / Horloge XTAL"},
    "L8": {"name": "D25", "gpio": 25, "type": "dac", "desc": "GPIO 25 / DAC1 (Sortie Analogique 8-bit) / ADC2_CH8"},
    "L9": {"name": "D26", "gpio": 26, "type": "dac", "desc": "GPIO 26 / DAC2 (Sortie Analogique 8-bit) / ADC2_CH9"},
    "L10": {"name": "D27", "gpio": 27, "type": "gpio", "desc": "GPIO 27 / ADC2_CH7 / Touch7 / PWM / HSPI_CS"},
    "L11": {"name": "D14", "gpio": 14, "type": "gpio", "desc": "GPIO 14 / ADC2_CH6 / Touch6 / HSPI_CLK / PWM"},
    "L12": {"name": "D12", "gpio": 12, "type": "gpio", "desc": "GPIO 12 / ADC2_CH5 / Touch5 / HSPI_MISO / JTAG"},
    "L13": {"name": "D13", "gpio": 13, "type": "gpio", "desc": "GPIO 13 / ADC2_CH4 / Touch4 / HSPI_MOSI"},
    "L14": {"name": "GND", "gpio": None, "type": "gnd", "desc": "Masse / Ground (0V)"},
    "L15": {"name": "VIN", "gpio": None, "type": "power", "desc": "Alimentation 5V (Entrée USB regulée)"},
    
    # Right Side
    "R1": {"name": "GND", "gpio": None, "type": "gnd", "desc": "Masse / Ground (0V)"},
    "R2": {"name": "D23", "gpio": 23, "type": "gpio", "desc": "GPIO 23 / VSPI_MOSI"},
    "R3": {"name": "D22", "gpio": 22, "type": "gpio", "desc": "GPIO 22 / I2C_SCL (Horloge I2C par défaut)"},
    "R4": {"name": "TX0", "gpio": 1, "type": "serial", "desc": "GPIO 1 / U0TXD (Liaison série console/téléversement)"},
    "R5": {"name": "RX0", "gpio": 3, "type": "serial", "desc": "GPIO 3 / U0RXD (Liaison série console/téléversement)"},
    "R6": {"name": "D21", "gpio": 21, "type": "gpio", "desc": "GPIO 21 / I2C_SDA (Données I2C par défaut)"},
    "R7": {"name": "D19", "gpio": 19, "type": "gpio", "desc": "GPIO 19 / VSPI_MISO"},
    "R8": {"name": "D18", "gpio": 18, "type": "gpio", "desc": "GPIO 18 / VSPI_CLK"},
    "R9": {"name": "D5", "gpio": 5, "type": "gpio", "desc": "GPIO 5 / VSPI_CS / PWM"},
    "R10": {"name": "D17", "gpio": 17, "type": "gpio", "desc": "GPIO 17 / UART2_TXD"},
    "R11": {"name": "D16", "gpio": 16, "type": "gpio", "desc": "GPIO 16 / UART2_RXD"},
    "R12": {"name": "D4", "gpio": 4, "type": "gpio", "desc": "GPIO 4 / ADC2_CH0 / Touch0 / PWM"},
    "R13": {"name": "D2", "gpio": 2, "type": "gpio", "desc": "GPIO 2 / LED intégrée (Bleue) / ADC2_CH2 / Touch2"},
    "R14": {"name": "D15", "gpio": 15, "type": "gpio", "desc": "GPIO 15 / ADC2_CH3 / Touch3 / HSPI_CS / Boot Strap"},
    "R15": {"name": "3V3", "gpio": None, "type": "power", "desc": "Sortie alimentation régulée 3.3V"},
}

PIN_DB_38PIN = {
    # Left Side
    "L1": {"name": "3V3", "gpio": None, "type": "power", "desc": "Sortie alimentation régulée 3.3V"},
    "L2": {"name": "EN", "gpio": None, "type": "power", "desc": "Reset / Enclencher (Bouton EN)"},
    "L3": {"name": "D36", "gpio": 36, "type": "adc", "desc": "GPIO 36 / Entrée Analogique ADC1_CH0 / Capteur Hall"},
    "L4": {"name": "D39", "gpio": 39, "type": "adc", "desc": "GPIO 39 / Entrée Analogique ADC1_CH3 / Capteur Hall"},
    "L5": {"name": "D34", "gpio": 34, "type": "adc", "desc": "GPIO 34 / Entrée Analogique ADC1_CH6 (Entrée seule)"},
    "L6": {"name": "D35", "gpio": 35, "type": "adc", "desc": "GPIO 35 / Entrée Analogique ADC1_CH7 (Entrée seule)"},
    "L7": {"name": "D32", "gpio": 32, "type": "gpio", "desc": "GPIO 32 / ADC1_CH4 / Touch9"},
    "L8": {"name": "D33", "gpio": 33, "type": "gpio", "desc": "GPIO 33 / ADC1_CH5 / Touch8"},
    "L9": {"name": "D25", "gpio": 25, "type": "dac", "desc": "GPIO 25 / DAC1 (Sortie Analogique) / ADC2_CH8"},
    "L10": {"name": "D26", "gpio": 26, "type": "dac", "desc": "GPIO 26 / DAC2 / ADC2_CH9"},
    "L11": {"name": "D27", "gpio": 27, "type": "gpio", "desc": "GPIO 27 / ADC2_CH7 / Touch7"},
    "L12": {"name": "D14", "gpio": 14, "type": "gpio", "desc": "GPIO 14 / ADC2_CH6 / Touch6 / HSPI_CLK"},
    "L13": {"name": "D12", "gpio": 12, "type": "gpio", "desc": "GPIO 12 / ADC2_CH5 / Touch5 / HSPI_MISO"},
    "L14": {"name": "D13", "gpio": 13, "type": "gpio", "desc": "GPIO 13 / ADC2_CH4 / Touch4 / HSPI_MOSI"},
    "L15": {"name": "GND", "gpio": None, "type": "gnd", "desc": "Masse / Ground (0V)"},
    "L16": {"name": "D9", "gpio": 9, "type": "flash", "desc": "GPIO 9 / Connecté au Flash SPI interne (⚠️ Évitez de brancher !)"},
    "L17": {"name": "D10", "gpio": 10, "type": "flash", "desc": "GPIO 10 / Connecté au Flash SPI interne (⚠️ Évitez de brancher !)"},
    "L18": {"name": "D11", "gpio": 11, "type": "flash", "desc": "GPIO 11 / Connecté au Flash SPI interne (⚠️ Évitez de brancher !)"},
    "L19": {"name": "5V", "gpio": None, "type": "power", "desc": "Entrée alimentation 5V (VIN)"},
    
    # Right Side
    "R1": {"name": "GND", "gpio": None, "type": "gnd", "desc": "Masse / Ground (0V)"},
    "R2": {"name": "D23", "gpio": 23, "type": "gpio", "desc": "GPIO 23 / VSPI_MOSI"},
    "R3": {"name": "D22", "gpio": 22, "type": "gpio", "desc": "GPIO 22 / I2C_SCL (Horloge I2C)"},
    "R4": {"name": "TX0", "gpio": 1, "type": "serial", "desc": "GPIO 1 / U0TXD (Console liaison série)"},
    "R5": {"name": "RX0", "gpio": 3, "type": "serial", "desc": "GPIO 3 / U0RXD (Console liaison série)"},
    "R6": {"name": "D21", "gpio": 21, "type": "gpio", "desc": "GPIO 21 / I2C_SDA (Données I2C)"},
    "R7": {"name": "D19", "gpio": 19, "type": "gpio", "desc": "GPIO 19 / VSPI_MISO"},
    "R8": {"name": "D18", "gpio": 18, "type": "gpio", "desc": "GPIO 18 / VSPI_CLK"},
    "R9": {"name": "D5", "gpio": 5, "type": "gpio", "desc": "GPIO 5 / VSPI_CS / PWM"},
    "R10": {"name": "D17", "gpio": 17, "type": "gpio", "desc": "GPIO 17 / UART2_TXD"},
    "R11": {"name": "D16", "gpio": 16, "type": "gpio", "desc": "GPIO 16 / UART2_RXD"},
    "R12": {"name": "D4", "gpio": 4, "type": "gpio", "desc": "GPIO 4 / ADC2_CH0 / Touch0"},
    "R13": {"name": "D2", "gpio": 2, "type": "gpio", "desc": "GPIO 2 / LED Bleue intégrée / ADC2_CH2 / Touch2"},
    "R14": {"name": "D15", "gpio": 15, "type": "gpio", "desc": "GPIO 15 / ADC2_CH3 / Touch3 / HSPI_CS"},
    "R15": {"name": "D8", "gpio": 8, "type": "flash", "desc": "GPIO 8 / Connecté au Flash SPI interne (⚠️ Évitez de brancher !)"},
    "R16": {"name": "D7", "gpio": 7, "type": "flash", "desc": "GPIO 7 / Connecté au Flash SPI interne (⚠️ Évitez de brancher !)"},
    "R17": {"name": "D6", "gpio": 6, "type": "flash", "desc": "GPIO 6 / Connecté au Flash SPI interne (⚠️ Évitez de brancher !)"},
    "R18": {"name": "GND", "gpio": None, "type": "gnd", "desc": "Masse / Ground (0V)"},
    "R19": {"name": "3V3", "gpio": None, "type": "power", "desc": "Sortie alimentation régulée 3.3V"},
}


class Esp32PinoutView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#1e1e1e")
        
        # --- Top Control Panel ---
        self.control_frame = tk.Frame(self, bg="#2d2d2d", pady=5)
        self.control_frame.pack(fill="x", side="top")
        
        # Board Selector
        tk.Label(self.control_frame, text="Carte :", bg="#2d2d2d", fg="white", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, padx=5, sticky="w")
        self.board_var = tk.StringVar(value="30pin")
        self.board_menu = ttk.Combobox(self.control_frame, textvariable=self.board_var, values=["30pin", "38pin"], state="readonly", width=10)
        self.board_menu.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        self.board_menu.bind("<<ComboboxSelected>>", self.on_board_change)
        
        # Snippet Mode Selector
        tk.Label(self.control_frame, text="Code :", bg="#2d2d2d", fg="white", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, padx=5, sticky="w")
        self.snippet_var = tk.StringVar(value="Pin.OUT")
        self.snippet_menu = ttk.Combobox(self.control_frame, textvariable=self.snippet_var, values=["Pin.OUT", "Pin.IN", "ADC", "PWM", "GPIO"], state="readonly", width=10)
        self.snippet_menu.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        # --- Legend Frame ---
        self.legend_frame = tk.Frame(self, bg="#1e1e1e", pady=3)
        self.legend_frame.pack(fill="x", side="top")
        self.draw_legend()
        
        # --- Scrollable Canvas ---
        self.canvas_container = tk.Frame(self, bg="#1e1e1e")
        self.canvas_container.pack(fill="both", expand=True)
        
        self.canvas = tk.Canvas(self.canvas_container, bg="#1e1e1e", highlightthickness=0, width=280)
        self.scrollbar = ttk.Scrollbar(self.canvas_container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Bind scrolling events
        self.canvas.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind_all("<Button-4>", self.on_mousewheel)
        self.canvas.bind_all("<Button-5>", self.on_mousewheel)
        
        # --- Bottom Details Panel ---
        self.details_frame = tk.LabelFrame(self, text="Détails de la Broche", bg="#2d2d2d", fg="#3B82F6", font=("Segoe UI", 9, "bold"), padx=8, pady=8)
        self.details_frame.pack(fill="x", side="bottom", padx=5, pady=5)
        
        self.details_label = tk.Label(self.details_frame, text="Cliquez sur une broche pour copier/insérer le code MicroPython.", bg="#2d2d2d", fg="#e0e0e0", wraplength=240, justify="left", font=("Segoe UI", 9))
        self.details_label.pack(fill="x")
        
        # Draw Initial Board
        self.current_db = PIN_DB_30PIN
        self.drawn_pins = {}
        self.redraw_board()

    def draw_legend(self):
        # Draw small color dots for legend
        legend_data = [
            ("Power", PIN_COLORS["power"]),
            ("GND", PIN_COLORS["gnd"]),
            ("GPIO", PIN_COLORS["gpio"]),
            ("ADC", PIN_COLORS["adc"]),
            ("DAC", PIN_COLORS["dac"]),
            ("UART", PIN_COLORS["serial"]),
            ("Flash", PIN_COLORS["flash"])
        ]
        
        frame = tk.Frame(self.legend_frame, bg="#1e1e1e")
        frame.pack(anchor="center")
        
        col = 0
        for label, color in legend_data:
            dot_canvas = tk.Canvas(frame, width=12, height=12, bg="#1e1e1e", highlightthickness=0)
            dot_canvas.create_oval(2, 2, 10, 10, fill=color, outline="white", width=0.5)
            dot_canvas.grid(row=0, column=col*2, padx=(4, 1))
            
            lbl = tk.Label(frame, text=label, bg="#1e1e1e", fg="#a0a0a0", font=("Segoe UI", 8))
            lbl.grid(row=0, column=col*2+1, padx=(0, 4))
            col += 1

    def on_board_change(self, event=None):
        board_type = self.board_var.get()
        if board_type == "30pin":
            self.current_db = PIN_DB_30PIN
        else:
            self.current_db = PIN_DB_38PIN
        self.redraw_board()

    def on_mousewheel(self, event):
        # Allow scrolling only if view is active and mapped
        if not self.winfo_ismapped():
            return
        
        if event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    def redraw_board(self):
        self.canvas.delete("all")
        self.drawn_pins.clear()
        
        db = self.current_db
        is_38pin = (self.board_var.get() == "38pin")
        num_pins_side = 19 if is_38pin else 15
        
        # Metrics
        board_h = 100 + num_pins_side * 24
        cx = 135
        board_w = 90
        
        # 1. Draw Board PCB
        self.canvas.create_rectangle(cx - board_w//2, 30, cx + board_w//2, 30 + board_h, fill="#1c1c1c", outline="#2e2e2e", width=2)
        
        # 2. Draw ESP32-WROOM Metal Shield
        self.canvas.create_rectangle(cx - 36, 45, cx + 36, 120, fill="#cccccc", outline="#b3b3b3", width=1)
        self.canvas.create_text(cx, 82, text="ESP32-WROOM-32", fill="#333333", font=("Segoe UI", 8, "bold"))
        
        # Draw Gold Antenna Trace
        self.canvas.create_rectangle(cx - 36, 12, cx + 36, 45, fill="#111111", outline="#222222")
        # Draw PCB Gold traces inside antenna
        for ax in range(cx - 30, cx + 30, 8):
            self.canvas.create_line(ax, 20, ax + 4, 38, fill="#d4af37", width=1.5)
            self.canvas.create_line(ax + 4, 38, ax + 8, 20, fill="#d4af37", width=1.5)
            
        # 3. Draw USB Connector (bottom)
        self.canvas.create_rectangle(cx - 15, 30 + board_h - 10, cx + 15, 30 + board_h + 4, fill="#404040", outline="#606060")
        
        # 4. Draw Boot & EN Buttons
        self.canvas.create_rectangle(cx - 35, 30 + board_h - 25, cx - 20, 30 + board_h - 15, fill="#2c2c2c", outline="#404040")
        self.canvas.create_text(cx - 27, 30 + board_h - 20, text="EN", fill="#a0a0a0", font=("Segoe UI", 6))
        
        self.canvas.create_rectangle(cx + 20, 30 + board_h - 25, cx + 35, 30 + board_h - 15, fill="#2c2c2c", outline="#404040")
        self.canvas.create_text(cx + 27, 30 + board_h - 20, text="BOOT", fill="#a0a0a0", font=("Segoe UI", 6))
        
        # 5. Draw Pins
        for i in range(num_pins_side):
            # Y Coordinate
            y = 150 + i * 23
            
            # Left Pin Data
            l_key = f"L{i+1}"
            l_data = db[l_key]
            l_color = PIN_COLORS[l_data["type"]]
            
            # Draw Left Pin Shape
            l_rect_id = self.canvas.create_rectangle(cx - board_w//2 - 8, y - 6, cx - board_w//2, y + 6, fill=l_color, outline="white", width=0.5)
            # Draw Left Label
            l_text_id = self.canvas.create_text(cx - board_w//2 - 12, y, text=l_data["name"], fill="white", anchor="e", font=("Segoe UI", 9, "bold"))
            
            self.drawn_pins[l_rect_id] = l_data
            self.drawn_pins[l_text_id] = l_data
            
            # Bind Events
            self.canvas.tag_bind(l_rect_id, "<Enter>", lambda e, rid=l_rect_id, tid=l_text_id: self.on_pin_enter(rid, tid))
            self.canvas.tag_bind(l_rect_id, "<Leave>", lambda e, rid=l_rect_id, tid=l_text_id: self.on_pin_leave(rid, tid))
            self.canvas.tag_bind(l_rect_id, "<Button-1>", lambda e, data=l_data: self.on_pin_click(data))
            
            self.canvas.tag_bind(l_text_id, "<Enter>", lambda e, rid=l_rect_id, tid=l_text_id: self.on_pin_enter(rid, tid))
            self.canvas.tag_bind(l_text_id, "<Leave>", lambda e, rid=l_rect_id, tid=l_text_id: self.on_pin_leave(rid, tid))
            self.canvas.tag_bind(l_text_id, "<Button-1>", lambda e, data=l_data: self.on_pin_click(data))
            
            # Right Pin Data
            r_key = f"R{i+1}"
            r_data = db[r_key]
            r_color = PIN_COLORS[r_data["type"]]
            
            # Draw Right Pin Shape
            r_rect_id = self.canvas.create_rectangle(cx + board_w//2, y - 6, cx + board_w//2 + 8, y + 6, fill=r_color, outline="white", width=0.5)
            # Draw Right Label
            r_text_id = self.canvas.create_text(cx + board_w//2 + 12, y, text=r_data["name"], fill="white", anchor="w", font=("Segoe UI", 9, "bold"))
            
            self.drawn_pins[r_rect_id] = r_data
            self.drawn_pins[r_text_id] = r_data
            
            # Bind Events
            self.canvas.tag_bind(r_rect_id, "<Enter>", lambda e, rid=r_rect_id, tid=r_text_id: self.on_pin_enter(rid, tid))
            self.canvas.tag_bind(r_rect_id, "<Leave>", lambda e, rid=r_rect_id, tid=r_text_id: self.on_pin_leave(rid, tid))
            self.canvas.tag_bind(r_rect_id, "<Button-1>", lambda e, data=r_data: self.on_pin_click(data))
            
            self.canvas.tag_bind(r_text_id, "<Enter>", lambda e, rid=r_rect_id, tid=r_text_id: self.on_pin_enter(rid, tid))
            self.canvas.tag_bind(r_text_id, "<Leave>", lambda e, rid=r_rect_id, tid=r_text_id: self.on_pin_leave(rid, tid))
            self.canvas.tag_bind(r_text_id, "<Button-1>", lambda e, data=r_data: self.on_pin_click(data))
            
        # Update Scroll Region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_pin_enter(self, rect_id, text_id):
        self.canvas.itemconfig(rect_id, width=2, outline="#FFD700")  # Gold highlight border
        self.canvas.itemconfig(text_id, fill="#FFD700")              # Gold text

    def on_pin_leave(self, rect_id, text_id):
        self.canvas.itemconfig(rect_id, width=0.5, outline="white")  # Restore outline
        self.canvas.itemconfig(text_id, fill="white")                # Restore text

    def on_pin_click(self, pin_data):
        name = pin_data["name"]
        gpio = pin_data["gpio"]
        desc = pin_data["desc"]
        
        # 1. Update Details Description Panel
        info_str = f"Broche {name} : {desc}"
        
        # 2. Code Generation
        snippet = ""
        if gpio is not None:
            mode = self.snippet_var.get()
            if mode == "Pin.OUT":
                snippet = f"from machine import Pin\np{gpio} = Pin({gpio}, Pin.OUT)"
            elif mode == "Pin.IN":
                snippet = f"from machine import Pin\np{gpio} = Pin({gpio}, Pin.IN, Pin.PULL_UP)"
            elif mode == "ADC":
                snippet = f"from machine import ADC, Pin\nadc{gpio} = ADC(Pin({gpio}))"
            elif mode == "PWM":
                snippet = f"from machine import Pin, PWM\npwm{gpio} = PWM(Pin({gpio}), freq=5000, duty=512)"
            else: # "GPIO"
                snippet = str(gpio)
                
            info_str += f"\n\n👉 Copié & Inséré :\n{snippet.replace(chr(10), ' | ')}"
            
            # Copy to Clipboard
            try:
                copy_to_clipboard(snippet)
            except Exception as ce:
                # Fallback if workbench helper fails
                self.clipboard_clear()
                self.clipboard_append(snippet)
            
            # Insert directly at the user's cursor in the active editor
            try:
                editor = get_workbench().get_editor_notebook().get_current_editor()
                if editor:
                    code_view = editor.get_code_view()
                    if code_view:
                        # Insert snippet followed by newline if it's multiple lines
                        text_to_insert = snippet + "\n" if "\n" in snippet else snippet
                        code_view.text.insert(tk.INSERT, text_to_insert)
                        code_view.text.focus_set()
            except Exception as ie:
                pass
        else:
            info_str += "\n\n(Broche d'alimentation/masse - aucun code généré)"
            
        self.details_label.config(text=info_str)


def load_plugin() -> None:
    # Add view to the right sidebar ("e" = East)
    get_workbench().add_view(Esp32PinoutView, "ESP32 Pinout", "e")
