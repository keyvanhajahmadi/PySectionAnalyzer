import tkinter as tk
import subprocess
import os
import sys


def find_exe(name):
    d = os.path.dirname(os.path.abspath(sys.argv[0]))
    for cand in [os.path.join(d, name), os.path.join(d, "dist", name)]:
        if os.path.exists(cand):
            return cand
    return os.path.join(d, "dist", name)


def resource_path(name):
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, name)
    return os.path.join(os.path.dirname(__file__), name)


root = tk.Tk()
root.title("PyStructAnalyzer")
root.configure(bg="#1e1e2e")

try:
    ico = resource_path("logo.ico")
    if os.path.exists(ico):
        root.iconbitmap(ico)
except:
    pass

win_w, win_h = 600, 520
sw = root.winfo_screenwidth()
sh = root.winfo_screenheight()
root.geometry(f"{win_w}x{win_h}+{(sw - win_w) // 2}+{(sh - win_h) // 2}")
root.resizable(False, False)

C = {"base": "#1e1e2e", "mantle": "#181825",
     "blue": "#aad16e", "green": "#8bb84e",
     "teal": "#edd494", "lavender": "#c5df8a",
     "surface0": "#313244", "surface2": "#585b70",
     "overlay0": "#6c7086", "text": "#cdd6f4",
     "subtext0": "#a6adc8"}
F = {"big": ("Segoe UI", 14, "bold"),
      "norm": ("Segoe UI", 11),
      "small": ("Segoe UI", 9)}

# Logo image
try:
    logo_path = resource_path("logo.png")
    logo_img = tk.PhotoImage(file=logo_path)
    lw, lh = logo_img.width(), logo_img.height()
    max_sz = 220
    if lw > max_sz or lh > max_sz:
        f = max(lw // max_sz, lh // max_sz)
        if f > 1:
            logo_img = logo_img.subsample(f, f)
    lbl_logo = tk.Label(root, image=logo_img, bg=C["base"])
    lbl_logo.image = logo_img
    lbl_logo.pack(pady=(40, 10))
except Exception as e:
    tk.Label(root, text="PyStructAnalyzer", bg=C["base"],
             fg=C["blue"], font=("Segoe UI", 20, "bold")).pack(pady=(60, 10))

tk.Label(root, text="Select Language", bg=C["base"],
         fg=C["overlay0"], font=F["norm"]).pack(pady=(0, 20))

btn_fr = tk.Frame(root, bg=C["base"])
btn_fr.pack()


def mk_btn(text, color, hover, cmd):
    f = tk.Frame(btn_fr, bg=color, cursor="hand2", padx=40, pady=12)
    f.pack(side="left", padx=15)
    f.bind("<Button-1>", lambda e: cmd())
    f.bind("<Enter>", lambda e: f.config(bg=hover))
    f.bind("<Leave>", lambda e: f.config(bg=color))
    l = tk.Label(f, text=text, bg=color, fg=C["base"], font=F["big"])
    l.pack()
    l.bind("<Button-1>", lambda e: cmd())


def run_persian():
    root.destroy()
    p = find_exe("TrussAnalyzer.exe")
    if os.path.exists(p):
        subprocess.Popen([p])
    else:
        tk.messagebox.showerror("Error", f"TrussAnalyzer.exe not found:\n{p}")


def run_english():
    root.destroy()
    p = find_exe("TrussAnalyzer_EN.exe")
    if os.path.exists(p):
        subprocess.Popen([p])
    else:
        tk.messagebox.showerror("Error", f"TrussAnalyzer_EN.exe not found:\n{p}")


mk_btn("English", C["blue"], C["lavender"], run_english)
mk_btn("\u0641\u0627\u0631\u0633\u06cc", C["green"], C["teal"], run_persian)

footer = tk.Frame(root, bg=C["mantle"])
footer.pack(fill="x", side="bottom")
tk.Frame(footer, bg=C["surface2"], height=1).pack(fill="x")
tk.Label(footer, text="v2.0  |  Keyvan HajAhmadi  |  2026",
         bg=C["mantle"], fg=C["overlay0"], font=F["small"]).pack(pady=6)

root.mainloop()
