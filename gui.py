import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font
import math
import centroid
from main import centroid_spandrel_integral


C = {
    "base":      "#1e1e2e",
    "mantle":    "#181825",
    "crust":     "#11111b",
    "surface0":  "#313244",
    "surface1":  "#45475a",
    "surface2":  "#585b70",
    "overlay0":  "#6c7086",
    "text":      "#cdd6f4",
    "subtext1":  "#bac2de",
    "subtext0":  "#a6adc8",
    "blue":      "#aad16e",
    "lavender":  "#c5df8a",
    "sapphire":  "#e8c87a",
    "teal":      "#edd494",
    "green":     "#8bb84e",
    "yellow":    "#f9e2af",
    "peach":     "#fab387",
    "pink":      "#f38ba8",
}


class CentroidGUI:
    def __init__(self, root, parent=None):
        self.root = root
        self.parent = parent if parent is not None else root
        self.parent.configure(bg=C["mantle"])
        if parent is None:
            self.root.title("محاسبه‌گر مرکز سطح مرکب")
            self.root.state("zoomed")
            self.root.resizable(True, True)
            self.root.minsize(960, 680)
            self.root.configure(bg=C["mantle"])

        self.fullscreen = False
        self.root.bind("<F11>", self._toggle_fullscreen)
        self.root.bind("<Escape>", self._exit_fullscreen)

        self.font_family = self._pick_font()
        self.F = {
            "norm":   (self.font_family, 10),
            "bold":   (self.font_family, 10, "bold"),
            "big":    (self.font_family, 12, "bold"),
            "title":  (self.font_family, 15, "bold"),
            "result": (self.font_family, 13, "bold"),
        }

        self.shapes = {
            "مستطیل": {
                "icon": "▭", "params": [("l", "طول (l)"), ("h", "ارتفاع (h)")],
                "func": lambda p: centroid.mostatil(p["l"], p["h"]),
                "area": lambda p: p["l"] * p["h"],
            },
            "مثلث": {
                "icon": "△", "params": [("h", "ارتفاع (h)"), ("b", "قاعده (b)")],
                "func": lambda p: centroid.mosalas(p["h"]),
                "area": lambda p: p["b"] * p["h"] / 2,
            },
            "ربع دایره": {
                "icon": "◔", "params": [("r", "شعاع (r)")],
                "func": lambda p: centroid.robdaire(p["r"]),
                "area": lambda p: math.pi * p["r"] ** 2 / 4,
            },
            "نیم دایره": {
                "icon": "◖", "params": [("r", "شعاع (r)")],
                "func": lambda p: centroid.nimdaiere(p["r"]),
                "area": lambda p: math.pi * p["r"] ** 2 / 2,
            },
            "ربع بیضی": {
                "icon": "⬜", "params": [("a", "نیم‌محور a"), ("b", "نیم‌محور b")],
                "func": lambda p: centroid.robbeizi(p["a"], p["b"]),
                "area": lambda p: math.pi * p["a"] * p["b"] / 4,
            },
            "نیم بیضی": {
                "icon": "⬛", "params": [("a", "نیم‌محور a"), ("b", "نیم‌محور b")],
                "func": lambda p: centroid.nimbeiezi(p["a"], p["b"]),
                "area": lambda p: math.pi * p["a"] * p["b"] / 2,
            },
            "سهموی": {
                "icon": "∪", "params": [("s", "قاعده (a)"), ("b", "ارتفاع (h)")],
                "func": lambda p: centroid.sahmavi(p["s"], p["b"]),
                "area": lambda p: 2 * p["s"] * p["b"] / 3,
            },
            "نیم سهموی": {
                "icon": "∩", "params": [("a", "قاعده (a)"), ("h", "ارتفاع (h)")],
                "func": lambda p: centroid.robsahamavi(p["a"], p["h"]),
                "area": lambda p: p["a"] * p["h"] / 2,
            },
            "اسپاندرول": {
                "icon": "∫", "params": [("a", "قاعده (a)"), ("h", "ارتفاع (h)"), ("n", "توان (n)")],
                "func": lambda p: centroid_spandrel_integral(p["a"], p["h"], p["n"]),
                "area": lambda p: p["a"] * p["h"] * p["n"] / (p["n"] + 1),
            },
        }

        self.entries = {}
        self.param_frame = None
        self.x_sum = self.y_sum = self.area_sum = 0.0
        self.canvas_parts = []
        self.scale = 8.0
        self.origin = (400, 360)
        self.row_index = 0
        self.pulse_phase = 0

        self._build_styles()
        self._build_ui()
        self._start_pulse()

    def _pick_font(self):
        for f in ("Segoe UI", "Vazirmatn", "IRANSans", "Tahoma", "Arial"):
            if self._font_exists(f):
                return f
        return "TkDefaultFont"

    def _font_exists(self, name):
        try:
            tk.font.nametofont(name)
            return True
        except tk.TclError:
            return False

    def _build_styles(self):
        s = ttk.Style()
        s.theme_use("clam")

        s.configure(".", background=C["base"], foreground=C["text"], fieldbackground=C["surface0"])
        s.configure("TFrame", background=C["base"])
        s.configure("TLabel", background=C["base"], foreground=C["text"], font=self.F["norm"])

        s.configure("Card.TLabelframe",
                    background=C["surface0"], foreground=C["blue"],
                    borderwidth=0, relief="flat", padding=14)
        s.configure("Card.TLabelframe.Label",
                    background=C["mantle"], foreground=C["blue"],
                    font=self.F["big"], padding=(8, 4))

        s.configure("Accent.TButton",
                    background=C["green"], foreground=C["base"],
                    borderwidth=0, focusthickness=0,
                    font=self.F["bold"], padding=(22, 10))
        s.map("Accent.TButton",
              background=[("active", C["teal"]), ("pressed", C["green"])],
              foreground=[("active", C["base"])])

        s.configure("Danger.TButton",
                    background=C["pink"], foreground=C["base"],
                    borderwidth=0, focusthickness=0,
                    font=self.F["bold"], padding=(22, 10))
        s.map("Danger.TButton",
              background=[("active", C["peach"]), ("pressed", C["pink"])],
              foreground=[("active", C["base"])])

        s.configure("TEntry",
                    fieldbackground=C["surface1"], foreground=C["text"],
                    insertcolor=C["blue"], borderwidth=0, relief="flat", padding=8)
        s.map("TEntry",
              fieldbackground=[("focus", C["surface2"])],
              bordercolor=[("focus", C["blue"])])

        s.configure("TCombobox",
                    fieldbackground=C["surface1"], background=C["surface1"],
                    foreground=C["text"], arrowcolor=C["blue"],
                    borderwidth=0, padding=8)
        s.map("TCombobox",
              fieldbackground=[("readonly", C["surface1"]), ("focus", C["surface2"])],
              foreground=[("readonly", C["text"])],
              selectbackground=[("readonly", C["surface1"])],
              selectforeground=[("readonly", C["text"])])
        self.root.option_add("*TCombobox*Listbox*Background", C["surface1"])
        self.root.option_add("*TCombobox*Listbox*Foreground", C["text"])
        self.root.option_add("*TCombobox*Listbox*selectBackground", C["blue"])
        self.root.option_add("*TCombobox*Listbox*selectForeground", C["base"])
        self.root.option_add("*TCombobox*Listbox*Font", self.F["norm"])

        s.configure("Treeview",
                    background=C["surface0"], fieldbackground=C["surface0"],
                    foreground=C["text"], borderwidth=0, rowheight=28, font=self.F["norm"])
        s.configure("Treeview.Heading",
                    background=C["surface1"], foreground=C["blue"],
                    borderwidth=0, font=self.F["bold"], padding=10)
        s.map("Treeview",
              background=[("selected", C["blue"])],
              foreground=[("selected", C["base"])])
        s.map("Treeview.Heading",
              background=[("active", C["surface2"])])

    def _build_ui(self):
        self._build_header()
        content = tk.Frame(self.parent, bg=C["mantle"])
        content.pack(fill="both", expand=True, padx=18, pady=(12, 6))

        self._build_input_card(content)
        main_row = tk.Frame(content, bg=C["mantle"])
        main_row.pack(fill="both", expand=True, pady=12)
        self._build_canvas_card(main_row)
        self._build_table_card(main_row)
        self._build_result_card(content)
        self._build_status_bar()

        self._on_shape_change()

    def _build_header(self):
        h = tk.Frame(self.parent, bg=C["blue"], height=64)
        h.pack(fill="x", side="top")
        h.pack_propagate(False)
        tk.Label(h, text="◆", bg=C["blue"], fg=C["base"],
                 font=(self.font_family, 22, "bold")).pack(side="left", padx=(22, 6), pady=12)
        tk.Label(h, text="محاسبه‌گر مرکز سطح مرکب", bg=C["blue"], fg=C["base"],
                 font=self.F["title"]).pack(side="left", pady=18)
        tk.Frame(h, bg=C["blue"], width=2).pack(side="left", fill="y", padx=10, pady=14)
        tk.Label(h, text="ساخته شده توسط کیوان حاج احمدی", bg=C["blue"], fg=C["base"],
                 font=(self.font_family, 10, "italic")).pack(side="right", padx=(4, 16))
        tk.Label(h, text="F11 = فول‌اسکرین   |   Esc = خروج", bg=C["blue"], fg=C["base"],
                 font=self.F["norm"]).pack(side="right", padx=22)

    def _build_input_card(self, parent):
        card = ttk.LabelFrame(parent, text="  📐  افزودن جزء  ", style="Card.TLabelframe")
        card.pack(fill="x", pady=(0, 4))

        top = tk.Frame(card, bg=C["surface0"])
        top.pack(fill="x")

        tk.Label(top, text="شکل:", bg=C["surface0"], fg=C["subtext1"],
                 font=self.F["bold"]).grid(row=0, column=0, padx=(0, 6), pady=4, sticky="e")
        self.shape_var = tk.StringVar()
        shape_cb = ttk.Combobox(top, textvariable=self.shape_var,
                                values=[f'{v["icon"]}  {k}' for k, v in self.shapes.items()],
                                state="readonly", width=22, font=self.F["bold"])
        shape_cb.current(0)
        shape_cb.grid(row=0, column=1, padx=4, pady=4)
        shape_cb.bind("<<ComboboxSelected>>", self._on_shape_change)

        tk.Label(top, text="نوع:", bg=C["surface0"], fg=C["subtext1"],
                 font=self.F["bold"]).grid(row=0, column=2, padx=(20, 6), pady=4, sticky="e")
        self.fill_var = tk.StringVar(value="◆  پر")
        ttk.Combobox(top, textvariable=self.fill_var,
                     values=["◆  پر", "○  خالی"], state="readonly",
                     width=10, font=self.F["bold"]).grid(row=0, column=3, padx=4, pady=4)

        self.param_frame = tk.Frame(card, bg=C["surface0"])
        self.param_frame.pack(fill="x", pady=(8, 0))

        ttk.Button(card, text="➕  افزودن جزء", style="Accent.TButton",
                   command=self._add_part).pack(pady=(12, 2))

    def _on_shape_change(self, _=None):
        for w in self.param_frame.winfo_children():
            w.destroy()
        self.entries.clear()
        sel = self.shape_var.get()
        if not sel:
            return
        shape_name = sel.split("  ", 1)[1] if "  " in sel else sel
        cfg = self.shapes[shape_name]
        for i, (key, label) in enumerate(cfg["params"]):
            tk.Label(self.param_frame, text=label + ":", bg=C["surface0"], fg=C["subtext1"],
                     font=self.F["bold"]).grid(row=0, column=i * 2, padx=(8 if i else 0, 6), pady=4, sticky="e")
            e = ttk.Entry(self.param_frame, width=12, justify="center", font=self.F["norm"])
            e.grid(row=0, column=i * 2 + 1, padx=4, pady=4)
            e.bind("<Return>", lambda ev: self._add_part())
            self.entries[key] = e

    def _build_canvas_card(self, parent):
        card = ttk.LabelFrame(parent, text="  🎨  نمایش ترسیمی  ", style="Card.TLabelframe")
        card.pack(side="left", fill="both", expand=True, padx=(0, 6))
        self.canvas = tk.Canvas(card, bg=C["crust"], highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True, padx=6, pady=6)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

    def _build_table_card(self, parent):
        card = ttk.LabelFrame(parent, text="  📊  گزارش عددی  ", style="Card.TLabelframe")
        card.pack(side="right", fill="both", expand=True, padx=(6, 0))
        cols = ("شکل", "پارامترها", "x̄", "ȳ", "مساحت", "نوع")
        widths = (90, 220, 80, 80, 90, 60)
        self.tree = ttk.Treeview(card, columns=cols, show="headings", height=8)
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=6, pady=6)
        self.tree.tag_configure("odd", background=C["surface0"], foreground=C["text"])
        self.tree.tag_configure("even", background=C["surface1"], foreground=C["subtext1"])
        self.tree.tag_configure("hole", foreground=C["peach"])

    def _build_result_card(self, parent):
        card = ttk.LabelFrame(parent, text="  📍  نتیجه نهایی  ", style="Card.TLabelframe")
        card.pack(fill="x", pady=(4, 0))
        inner = tk.Frame(card, bg=C["surface0"])
        inner.pack(fill="x", pady=4)
        self.result_label = tk.Label(inner, text="هنوز جزءای اضافه نشده.",
                                     bg=C["surface0"], fg=C["green"],
                                     font=self.F["result"])
        self.result_label.pack(side="left", padx=10)
        ttk.Button(inner, text="🔄  بازنشانی", style="Danger.TButton",
                   command=self._reset).pack(side="right", padx=10)

    def _build_status_bar(self):
        bar = tk.Frame(self.parent, bg=C["surface0"], height=28)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        self.status_label = tk.Label(bar, text="●  آماده", bg=C["surface0"],
                                     fg=C["subtext0"], font=self.F["norm"])
        self.status_label.pack(side="left", padx=18)
        self.status_right = tk.Label(bar, text="", bg=C["surface0"],
                                     fg=C["subtext0"], font=self.F["norm"])
        self.status_right.pack(side="right", padx=18)

    def _add_part(self):
        sel = self.shape_var.get()
        shape_name = sel.split("  ", 1)[1] if "  " in sel else sel
        if not shape_name:
            messagebox.showwarning("خطا", "یک شکل انتخاب کن.")
            return
        try:
            params = {k: float(e.get()) for k, e in self.entries.items()}
        except ValueError:
            messagebox.showerror("خطا", "مقادیر باید عددی باشن.")
            return

        cfg = self.shapes[shape_name]
        try:
            cx, cy = cfg["func"](params)
        except ImportError as e:
            messagebox.showerror("خطا", str(e))
            return
        except Exception as e:
            messagebox.showerror("خطا در محاسبه", str(e))
            return

        area = cfg["area"](params)
        sign = 1 if "پر" in self.fill_var.get() else -1

        self.x_sum += sign * area * cx
        self.y_sum += sign * area * cy
        self.area_sum += sign * area

        tag = ("even" if self.row_index % 2 else "odd",) + (("hole",) if sign == -1 else ())
        self.tree.insert("", "end", values=(
            f'{cfg["icon"]}  {shape_name}',
            ", ".join(f"{k}={v:g}" for k, v in params.items()),
            f"{cx:.4f}",
            f"{cy:.4f}",
            f"{area:.4f}",
            "خالی" if sign == -1 else "پر",
        ), tags=tag)
        self.row_index += 1

        self.canvas_parts.append({"shape": shape_name, "params": params, "sign": sign, "icon": cfg["icon"]})
        self._redraw_canvas()
        self._update_result()
        self._update_status(f"●  جزء «{shape_name}» اضافه شد")

    def _update_result(self):
        if abs(self.area_sum) < 1e-12:
            self.result_label.config(text="⚠  مساحت خالص صفر است.", fg=C["peach"])
            return
        xc = self.x_sum / self.area_sum
        yc = self.y_sum / self.area_sum
        self.result_label.config(
            text=f"x̄ = {xc:.4f}     ȳ = {yc:.4f}     (مساحت خالص = {self.area_sum:.4f})",
            fg=C["green"],
        )
        self.status_right.config(text=f"ΣA = {self.area_sum:.4f}   |   x̄ = {xc:.4f}   ȳ = {yc:.4f}")

    def _reset(self):
        self.x_sum = self.y_sum = self.area_sum = 0.0
        self.canvas_parts.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.row_index = 0
        self._redraw_canvas()
        self.result_label.config(text="هنوز جزءای اضافه نشده.", fg=C["subtext0"])
        self.status_right.config(text="")
        self._update_status("●  بازنشانی شد")

    def _to_canvas(self, x, y):
        ox, oy = self.origin
        return ox + x * self.scale, oy - y * self.scale

    def _on_canvas_resize(self, event):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        self.origin = (cw // 2, ch - 36)
        self.scale = max(4.0, min(cw, ch) / 50.0)
        self._redraw_canvas()

    def _redraw_canvas(self):
        c = self.canvas
        c.delete("all")
        cw = c.winfo_width()
        ch = c.winfo_height()
        ox, oy = self._to_canvas(0, 0)
        step = max(1, int(self.scale))
        for x in range(0, cw, step):
            c.create_line(x, 0, x, ch, fill=C["mantle"], tags="grid")
        for y in range(0, ch, step):
            c.create_line(0, y, cw, y, fill=C["mantle"], tags="grid")
        c.create_line(0, oy, cw, oy, fill=C["overlay0"], dash=(4, 4), width=1)
        c.create_line(ox, 0, ox, ch, fill=C["overlay0"], dash=(4, 4), width=1)
        c.create_oval(ox - 3, oy - 3, ox + 3, oy + 3, fill=C["overlay0"], outline="")
        c.create_text(ox + 6, oy - 6, text="O", fill=C["overlay0"], anchor="nw", font=self.F["norm"])

        for part in self.canvas_parts:
            self._draw_shape(part)

        if abs(self.area_sum) > 1e-12 and self.canvas_parts:
            xc = self.x_sum / self.area_sum
            yc = self.y_sum / self.area_sum
            px, py = self._to_canvas(xc, yc)
            r = 6 + int(3 * abs(math.sin(self.pulse_phase)))
            c.create_oval(px - r, py - r, px + r, py + r, fill=C["pink"], outline=C["crust"], width=2)
            c.create_oval(px - 2, py - 2, px + 2, py + 2, fill=C["crust"], outline="")
            c.create_text(px + 14, py - 10, text=f"({xc:.2f}, {yc:.2f})",
                          fill=C["yellow"], anchor="w", font=self.F["bold"])

    def _draw_shape(self, part):
        c = self.canvas
        s = part["sign"]
        fill = C["blue"] if s == 1 else C["peach"]
        outline = C["lavender"] if s == 1 else C["yellow"]
        p = part["params"]
        shape = part["shape"]

        if shape == "مستطیل":
            x1, y1 = self._to_canvas(0, 0)
            x2, y2 = self._to_canvas(p["l"], p["h"])
            c.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=2,
                               stipple="" if s == 1 else "gray12")
        elif shape == "مثلث":
            x1, y1 = self._to_canvas(0, 0)
            x2, y2 = self._to_canvas(p["b"], 0)
            x3, y3 = self._to_canvas(0, p["h"])
            c.create_polygon(x1, y1, x2, y2, x3, y3, fill=fill, outline=outline, width=2,
                             stipple="" if s == 1 else "gray12")
        elif shape in ("ربع دایره", "نیم دایره"):
            r = p["r"] * self.scale
            ox, oy = self._to_canvas(0, 0)
            extent = -90 if shape == "ربع دایره" else 180
            c.create_arc(ox - r, oy - r, ox + r, oy + r, start=0, extent=extent,
                         fill=fill, outline=outline, width=2,
                         stipple="" if s == 1 else "gray12")
        elif shape in ("ربع بیضی", "نیم بیضی"):
            rx, ry = p["a"] * self.scale, p["b"] * self.scale
            ox, oy = self._to_canvas(0, 0)
            extent = -90 if shape == "ربع بیضی" else 180
            c.create_arc(ox - rx, oy - ry, ox + rx, oy + ry, start=0, extent=extent,
                         fill=fill, outline=outline, width=2,
                         stipple="" if s == 1 else "gray12")
        elif shape == "سهموی":
            w, h = p["s"] * self.scale, p["b"] * self.scale
            ox, oy = self._to_canvas(0, 0)
            c.create_arc(ox, oy - 2 * h, ox + 2 * w, oy, start=0, extent=-90,
                         fill=fill, outline=outline, width=2,
                         stipple="" if s == 1 else "gray12")
        elif shape == "نیم سهموی":
            w, h = p["a"] * self.scale, p["h"] * self.scale
            ox, oy = self._to_canvas(0, 0)
            c.create_arc(ox - w, oy - 2 * h, ox + w, oy, start=0, extent=180,
                         fill=fill, outline=outline, width=2,
                         stipple="" if s == 1 else "gray12")
        elif shape == "اسپاندرول":
            w, h = p["a"] * self.scale, p["h"] * self.scale
            ox, oy = self._to_canvas(0, 0)
            c.create_rectangle(ox, oy - h, ox + w, oy, fill=fill, outline=outline, width=2,
                               stipple="" if s == 1 else "gray12")
            c.create_line(ox, oy, ox + w, oy - h, fill=outline, width=1, dash=(3, 3))

    def _start_pulse(self):
        self.pulse_phase += 0.15
        if self.canvas_parts and abs(self.area_sum) > 1e-12:
            self._redraw_canvas()
        self.root.after(60, self._start_pulse)

    def _update_status(self, msg):
        self.status_label.config(text=msg, fg=C["green"])

    def _toggle_fullscreen(self, _=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def _exit_fullscreen(self, _=None):
        self.fullscreen = False
        self.root.attributes("-fullscreen", False)


if __name__ == "__main__":
    root = tk.Tk()
    CentroidGUI(root)
    root.mainloop()
