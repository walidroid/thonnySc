import tkinter as tk


def show_popup(text_widget, message):
    popup = tk.Toplevel()
    popup.overrideredirect(True)
    popup.attributes("-topmost", True)

    label = tk.Label(
        popup,
        text=message,
        background="#ffffe0",
        relief="solid",
        borderwidth=1,
        font=("Consolas", 10)
    )
    label.pack()

    # Position near cursor
    x = text_widget.winfo_pointerx()
    y = text_widget.winfo_pointery() + 20
    popup.geometry(f"+{x}+{y}")

    # Auto close after 3 seconds
    popup.after(3000, popup.destroy)

