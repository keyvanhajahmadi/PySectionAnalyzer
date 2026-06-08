import tkinter as tk
from tkinter import ttk, messagebox
import math
import truss


C = {
    "base": "#1e1e2e", "mantle": "#181825", "crust": "#11111b",
    "surface0": "#313244", "surface1": "#45475a", "surface2": "#585b70",
    "overlay0": "#6c7086", "text": "#cdd6f4", "subtext1": "#bac2de", "subtext0": "#a6adc8",
    "blue": "#aad16e", "lavender": "#c5df8a", "sapphire": "#e8c87a",
    "teal": "#edd494", "green": "#8bb84e", "yellow": "#f9e2af",
    "peach": "#fab387", "pink": "#f38ba8",
}


TOOLS = {
    "node":    {"label": "🟢 Node",     "desc": "Click to place a new node"},
    "member":  {"label": "🔵 Member",     "desc": "Click two nodes to connect a member"},
    "support": {"label": "🟡 Support","desc": "Click a node to place a support"},
    "load":    {"label": "🔴 Load",     "desc": "Click a node to apply a load"},
    "dim":     {"label": "📐 Measure",  "desc": "Click a member to see its dimensions"},
    "delete":  {"label": "❌ Delete","desc": "Click a node or member to delete"},
    "select":  {"label": "🖱️ Select",  "desc": "Drag a node to move it"},
}


class TrussGUI:
    def __init__(self, parent):
        self.parent = parent
        self.parent.configure(bg=C["mantle"])
        self.font_family = "Segoe UI"
        self.F = {"norm": (self.font_family, 10), "bold": (self.font_family, 10, "bold"),
                   "big": (self.font_family, 12, "bold"), "title": (self.font_family, 15, "bold"),
                   "result": (self.font_family, 11, "bold")}

        self.nodes = []
        self.members = []
        self.ref_lines = []
        self.supports = []
        self.loads = []
        self.forces = []
        self.reactions = []
        self.solved = False
        self.current_tool = "node"
        self.selected_node = None
        self.hover_node = None
        self.hover_member = None
        self.drag_node = None
        self.drag_offsets = (0, 0)
        self.snap_grid = 0.5

        self.scale = 30.0
        self.ox = 100.0
        self.oy = 400.0
        self.x_min, self.x_max = -5.0, 15.0
        self.y_min, self.y_max = -2.0, 12.0
        self._REF_COLORS = {"Green": C["green"], "Red": C["pink"], "Blue": C["blue"],
                            "Yellow": C["yellow"], "Orange": C["peach"], "Purple": C["lavender"]}

        self.build_styles()
        self.build_ui()
        self._update_transform()
        self.draw()

    def build_styles(self):
        s = ttk.Style()
        s.configure(".", background=C["base"], foreground=C["text"])
        s.configure("TLabel", background=C["base"], foreground=C["text"], font=self.F["norm"])
        s.configure("TEntry", fieldbackground=C["mantle"], foreground=C["text"],
                     insertcolor=C["text"], borderwidth=0, padding=4)
        s.map("TEntry", fieldbackground=[("focus", C["crust"])])
        s.configure("Treeview", background=C["mantle"], foreground=C["text"],
                    fieldbackground=C["mantle"], borderwidth=0, font=self.F["norm"])
        s.map("Treeview", background=[("selected", C["surface2"])],
              foreground=[("selected", C["text"])])
        s.configure("TSeparator", background=C["surface2"])
        s.configure("TCombobox", background=C["mantle"], foreground=C["text"],
                    fieldbackground=C["mantle"], selectbackground=C["surface2"],
                    selectforeground=C["text"], borderwidth=0, padding=4)
        s.map("TCombobox", fieldbackground=[("focus", C["crust"])],
              background=[("active", C["surface1"])])

    def _make_btn(self, parent, text, color, hover_color, cmd, **kw):
        btn = tk.Button(parent, text=text, bg=color, fg=C["base"],
                        font=self.F["bold"], bd=0, padx=14, pady=6, cursor="hand2",
                        activebackground=hover_color, activeforeground=C["base"],
                        command=cmd, relief="flat", highlightthickness=0, **kw)
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_color))
        btn.bind("<Leave>", lambda e: btn.config(bg=color))
        return btn

    def build_ui(self):
        # ── minimal header ──
        hdr = tk.Frame(self.parent, bg=C["mantle"])
        hdr.pack(fill="x", side="top")
        tk.Frame(hdr, bg=C["blue"], height=3).pack(fill="x")
        hdr_row = tk.Frame(hdr, bg=C["mantle"])
        hdr_row.pack(fill="x", padx=14, pady=(8, 6))
        tk.Label(hdr_row, text="🏗️", bg=C["mantle"], font=(self.font_family, 16)).pack(side="left")
        tk.Label(hdr_row, text="Truss Structure Analyzer", bg=C["mantle"], fg=C["text"],
                 font=self.F["title"]).pack(side="left", padx=(10, 0))
        tk.Label(hdr_row, text="Truss Analyzer v2", bg=C["mantle"], fg=C["overlay0"],
                 font=(self.font_family, 9)).pack(side="right")

        # ── body: left toolbar | canvas | right panel ──
        body = tk.Frame(self.parent, bg=C["base"])
        body.pack(fill="both", expand=True)

        # ── left toolbar ──
        tb = tk.Frame(body, bg=C["surface0"], width=72)
        tb.pack(side="left", fill="y")
        tb.pack_propagate(False)

        # tool buttons (top section)
        tool_ids = ("node", "member", "support", "load", "dim", "delete", "select")
        self.tool_btns = {}
        for i, tid in enumerate(tool_ids):
            emoji = TOOLS[tid]["label"][:2]
            label = TOOLS[tid]["label"][2:]
            b = tk.Button(tb, text=f"{emoji}\n{label}", bg=C["surface1"], fg=C["subtext1"],
                          font=(self.font_family, 8, "bold"), bd=0, padx=4, pady=6,
                          cursor="hand2", relief="flat", highlightthickness=0,
                          activebackground=C["surface2"], activeforeground=C["text"],
                          command=lambda tid=tid: self.set_tool(tid))
            b.pack(fill="x", padx=4, pady=(4 if i == 0 else 0, 0))
            self.tool_btns[tid] = b

        # spacer
        tk.Frame(tb, bg=C["surface0"]).pack(fill="both", expand=True)

        # solve / reset at bottom
        tk.Frame(tb, bg=C["surface2"], height=1).pack(fill="x", padx=6)
        solve_btn = tk.Button(tb, text="🧮\nSolve", bg=C["green"], fg=C["base"],
                              font=(self.font_family, 9, "bold"), bd=0, padx=4, pady=8,
                              cursor="hand2", relief="flat", highlightthickness=0,
                              activebackground=C["teal"], activeforeground=C["base"],
                              command=self.solve)
        solve_btn.pack(fill="x", padx=6, pady=(6, 2))
        reset_btn = tk.Button(tb, text="🗑\nReset", bg=C["surface1"], fg=C["pink"],
                              font=(self.font_family, 9, "bold"), bd=0, padx=4, pady=8,
                              cursor="hand2", relief="flat", highlightthickness=0,
                              activebackground=C["pink"], activeforeground=C["base"],
                              command=self.reset_all)
        reset_btn.pack(fill="x", padx=6, pady=(0, 6))

        # ── canvas ──
        canvas_frame = tk.Frame(body, bg=C["crust"])
        canvas_frame.pack(side="left", fill="both", expand=True, padx=(1, 0))
        border = tk.Frame(canvas_frame, bg=C["surface2"])
        border.pack(fill="both", expand=True, padx=1, pady=1)
        self.canvas = tk.Canvas(border, bg=C["crust"], highlightthickness=0, bd=0,
                                cursor="crosshair")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self.draw())
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_motion)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.parent.bind("<Key>", self.on_key)
        for k in ("<Up>", "<Down>", "<Left>", "<Right>"):
            self.parent.bind(k, self.on_arrow)

        # ── right panel ──
        rp = tk.Frame(body, bg=C["base"], width=280)
        rp.pack(side="right", fill="y", padx=(1, 0))
        rp.pack_propagate(False)

        # props card
        self.prop_card = tk.Frame(rp, bg=C["surface0"])
        self.prop_card.pack(fill="x")
        tk.Frame(self.prop_card, bg=C["blue"], height=2).pack(fill="x")
        hdr_f = tk.Frame(self.prop_card, bg=C["surface0"])
        hdr_f.pack(fill="x", padx=10, pady=(8, 2))
        tk.Label(hdr_f, text="⚙️  Settings", bg=C["surface0"], fg=C["blue"],
                 font=self.F["big"]).pack(side="left")
        self.tool_desc = tk.Label(hdr_f, text="", bg=C["surface0"], fg=C["overlay0"],
                                  font=(self.font_family, 8))
        self.tool_desc.pack(side="right")
        self.prop_content = tk.Frame(self.prop_card, bg=C["surface0"])
        self.prop_content.pack(fill="x", padx=10, pady=(2, 8))
        self.prop_entries = []
        self.prop_ok_btn = None

        # results card
        res_card = tk.Frame(rp, bg=C["surface0"])
        res_card.pack(fill="both", expand=True, pady=(6, 0))
        tk.Frame(res_card, bg=C["blue"], height=2).pack(fill="x")
        tk.Label(res_card, text="📊  Member Results", bg=C["surface0"], fg=C["blue"],
                 font=self.F["big"]).pack(anchor="w", padx=10, pady=(8, 2))
        cols = ("Member", "Force", "Type")
        self.tree = ttk.Treeview(res_card, columns=cols, show="headings", height=6)
        for c, w in zip(cols, (60, 90, 70)):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=8, pady=6)
        self.tree.tag_configure("tension", foreground=C["green"])
        self.tree.tag_configure("compression", foreground=C["pink"])

        # reactions card
        rx_card = tk.Frame(rp, bg=C["surface0"])
        rx_card.pack(fill="x", pady=(6, 0))
        tk.Frame(rx_card, bg=C["blue"], height=2).pack(fill="x")
        tk.Label(rx_card, text="📍  Reactions", bg=C["surface0"], fg=C["blue"],
                 font=self.F["big"]).pack(anchor="w", padx=10, pady=(8, 2))
        self.react_label = tk.Label(rx_card, text="Not solved yet.", bg=C["surface0"],
                                    fg=C["subtext0"], font=self.F["result"])
        self.react_label.pack(anchor="w", padx=10, pady=(4, 8))

        # ── status bar ──
        sb = tk.Frame(self.parent, bg=C["surface0"], height=24)
        sb.pack(fill="x", side="bottom")
        tk.Frame(sb, bg=C["surface2"], height=1).pack(fill="x")
        self.status_label = tk.Label(sb, text="Ready", bg=C["surface0"], fg=C["overlay0"],
                                     font=(self.font_family, 9))
        self.status_label.pack(side="left", padx=10, pady=2)

        self.set_tool("node")

    def _clear_prop(self):
        for w in self.prop_content.winfo_children():
            w.destroy()
        self.prop_entries = []
        self.prop_ok_btn = None

    def _build_prop_node(self):
        self._clear_prop()
        frow = tk.Frame(self.prop_content, bg=C["surface0"])
        frow.pack(pady=4)
        tk.Label(frow, text="X:", bg=C["surface0"], fg=C["subtext1"], font=self.F["bold"]).pack(side="left")
        self.entry_nx = ttk.Entry(frow, width=8, justify="center")
        self.entry_nx.pack(side="left", padx=3)
        self.entry_nx.insert(0, "0")
        self.entry_nx.bind("<Return>", lambda e: self._add_node_keyboard())
        tk.Label(frow, text="Y:", bg=C["surface0"], fg=C["subtext1"], font=self.F["bold"]).pack(side="left", padx=(8, 0))
        self.entry_ny = ttk.Entry(frow, width=8, justify="center")
        self.entry_ny.pack(side="left", padx=3)
        self.entry_ny.insert(0, "0")
        self.entry_ny.bind("<Return>", lambda e: self._add_node_keyboard())
        btn = self._make_btn(self.prop_content, "➕ Add Node", C["blue"], C["lavender"],
                             self._add_node_keyboard)
        btn.pack(pady=4)
        tk.Label(self.prop_content, text="Or click on canvas", bg=C["surface0"],
                 fg=C["subtext0"], font=self.F["norm"]).pack(pady=(0, 2))
        self.status("Type coordinates + Enter, or click on canvas.")

    def _add_node_keyboard(self):
        try:
            x = float(self.entry_nx.get())
            y = float(self.entry_ny.get())
        except ValueError:
            messagebox.showerror("Error", "X and Y must be numbers.")
            return
        self.nodes.append((x, y))
        self.solved = False
        self.status(f"Node {len(self.nodes)-1}: ({x:.2f}, {y:.2f})")
        self.entry_nx.delete(0, "end")
        self.entry_ny.delete(0, "end")
        self.entry_nx.insert(0, "0")
        self.entry_ny.insert(0, "0")
        self.draw()

    def _build_prop_member(self):
        self._clear_prop()
        tk.Label(self.prop_content, text="Select first node...", bg=C["surface0"],
                 fg=C["subtext0"], font=self.F["norm"]).pack()
        if self.selected_node is not None:
            self.status(f"Node {self.selected_node} selected. Click second node.")

    def _build_prop_support(self):
        self._clear_prop()
        tk.Label(self.prop_content, text="Support Type:", bg=C["surface0"],
                 fg=C["text"], font=self.F["bold"]).pack(anchor="w")
        self.sup_var = tk.StringVar(value="Pinned")
        ttk.Combobox(self.prop_content, textvariable=self.sup_var,
                      values=["Pinned (Rx,Ry)", "Fixed (Rx,Ry,M)", "Roller V (Ry)", "Roller H (Rx)", "Cable (Rx,Ry)"],
                      state="readonly", width=22, font=self.F["norm"]).pack(pady=4)
        tk.Label(self.prop_content, text="Click on a node.", bg=C["surface0"],
                 fg=C["subtext0"], font=self.F["norm"]).pack()
        self.status("Click a node to place a support.")

    def _build_prop_load(self):
        self._clear_prop()
        tk.Label(self.prop_content, text="Load Value:", bg=C["surface0"],
                 fg=C["text"], font=self.F["bold"]).pack(anchor="w")
        frow = tk.Frame(self.prop_content, bg=C["surface0"])
        frow.pack(pady=2)
        tk.Label(frow, text="Fx:", bg=C["surface0"], fg=C["subtext1"], font=self.F["norm"]).pack(side="left")
        self.entry_fx = ttk.Entry(frow, width=8, justify="center")
        self.entry_fx.pack(side="left", padx=2)
        self.entry_fx.insert(0, "0")
        tk.Label(frow, text="Fy:", bg=C["surface0"], fg=C["subtext1"], font=self.F["norm"]).pack(side="left", padx=(6, 0))
        self.entry_fy = ttk.Entry(frow, width=8, justify="center")
        self.entry_fy.pack(side="left", padx=2)
        self.entry_fy.insert(0, "0")
        tk.Label(self.prop_content, text="Click on a node.", bg=C["surface0"],
                 fg=C["subtext0"], font=self.F["norm"]).pack()
        self.status("Click a node to apply a load.")

    def set_tool(self, tool_id):
        self.current_tool = tool_id
        self.selected_node = None
        self.canvas.config(cursor="crosshair" if tool_id != "select" else "hand2")
        for tid, btn in self.tool_btns.items():
            if tid == tool_id:
                btn.config(bg=C["blue"], fg=C["base"])
            else:
                btn.config(bg=C["surface1"], fg=C["subtext1"])
        self.tool_desc.config(text=TOOLS[tool_id]["desc"])
        if tool_id == "node":
            self._build_prop_node()
        elif tool_id == "member":
            self._build_prop_member()
        elif tool_id == "support":
            self._build_prop_support()
        elif tool_id == "load":
            self._build_prop_load()
        elif tool_id == "dim":
            self._clear_prop()
            tk.Label(self.prop_content, text="Click a Member\nto see its dimensions.", bg=C["surface0"],
                     fg=C["subtext0"], font=self.F["norm"]).pack()
            self.status("Click a Member to see dx, dy, L.")
        elif tool_id == "delete":
            self._clear_prop()
            tk.Label(self.prop_content, text="Click a Node or Member.", bg=C["surface0"],
                     fg=C["subtext0"], font=self.F["norm"]).pack()
            self.status("Click a Node or Member to delete.")
        elif tool_id == "select":
            self._build_prop_select()

    def status(self, msg):
        self.status_label.config(text=msg, fg=C["green"])

    def _get_canvas_size(self):
        self.canvas.update_idletasks()
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        return (cw, ch) if cw > 10 and ch > 10 else (800, 500)

    def _update_transform(self):
        cw, ch = self._get_canvas_size()
        sx = cw / (self.x_max - self.x_min) * 0.85
        sy = ch / (self.y_max - self.y_min) * 0.85
        self.scale = max(5, min(sx, sy, 200))
        self.ox = cw / 2 - self.scale * (self.x_min + self.x_max) / 2
        self.oy = ch / 2 + self.scale * (self.y_min + self.y_max) / 2

    def _recalc_limits(self):
        cw, ch = self._get_canvas_size()
        self.x_min = (-self.ox) / self.scale
        self.x_max = (cw - self.ox) / self.scale
        self.y_min = (self.oy - ch) / self.scale
        self.y_max = self.oy / self.scale

    def _build_prop_select(self):
        self._recalc_limits()
        self._clear_prop()
        tk.Label(self.prop_content, text="Settings Axes (m):", bg=C["surface0"],
                 fg=C["subtext1"], font=self.F["bold"]).pack(pady=(0, 4))
        fr = tk.Frame(self.prop_content, bg=C["surface0"])
        fr.pack()
        tk.Label(fr, text="X from:", bg=C["surface0"], fg=C["subtext1"], font=self.F["norm"]).pack(side="left")
        self.entry_xmin = ttk.Entry(fr, width=7, justify="center")
        self.entry_xmin.pack(side="left", padx=1)
        self.entry_xmin.insert(0, f"{self.x_min:.1f}")
        tk.Label(fr, text=" to:", bg=C["surface0"], fg=C["subtext1"], font=self.F["norm"]).pack(side="left")
        self.entry_xmax = ttk.Entry(fr, width=7, justify="center")
        self.entry_xmax.pack(side="left", padx=1)
        self.entry_xmax.insert(0, f"{self.x_max:.1f}")
        fr2 = tk.Frame(self.prop_content, bg=C["surface0"])
        fr2.pack()
        tk.Label(fr2, text="Y from:", bg=C["surface0"], fg=C["subtext1"], font=self.F["norm"]).pack(side="left")
        self.entry_ymin = ttk.Entry(fr2, width=7, justify="center")
        self.entry_ymin.pack(side="left", padx=1)
        self.entry_ymin.insert(0, f"{self.y_min:.1f}")
        tk.Label(fr2, text=" to:", bg=C["surface0"], fg=C["subtext1"], font=self.F["norm"]).pack(side="left")
        self.entry_ymax = ttk.Entry(fr2, width=7, justify="center")
        self.entry_ymax.pack(side="left", padx=1)
        self.entry_ymax.insert(0, f"{self.y_max:.1f}")
        fr3 = tk.Frame(self.prop_content, bg=C["surface0"])
        fr3.pack(pady=2)
        tk.Label(fr3, text="Grid:", bg=C["surface0"], fg=C["subtext1"], font=self.F["norm"]).pack(side="left")
        self.entry_grid = ttk.Entry(fr3, width=7, justify="center")
        self.entry_grid.pack(side="left", padx=1)
        self.entry_grid.insert(0, f"{self.snap_grid:.2f}")
        tk.Label(fr3, text="m", bg=C["surface0"], fg=C["subtext1"], font=self.F["norm"]).pack(side="left", padx=2)
        self._make_btn(self.prop_content, "✓ Apply", C["green"], C["teal"],
                       self._apply_view).pack(pady=4)
        for e in (self.entry_xmin, self.entry_xmax, self.entry_ymin, self.entry_ymax, self.entry_grid):
            e.bind("<Return>", lambda ev: self._apply_view())
        self.status("Set axis limits and grid step via keyboard.")

        ttk.Separator(self.prop_content, orient="horizontal").pack(fill="x", pady=6)
        tk.Label(self.prop_content, text="Member Weight:", bg=C["surface0"], fg=C["subtext1"],
                 font=self.F["bold"]).pack()
        fw = tk.Frame(self.prop_content, bg=C["surface0"])
        fw.pack(pady=2)
        tk.Label(fw, text="Unit Weight (kN/m):", bg=C["surface0"], fg=C["subtext1"],
                 font=self.F["norm"]).pack(side="left")
        self.entry_selfw = ttk.Entry(fw, width=7, justify="center")
        self.entry_selfw.pack(side="left", padx=2)
        self.entry_selfw.insert(0, "0.0")
        self._make_btn(self.prop_content, "⚖️ Distribute Weight", C["sapphire"], C["teal"],
                       self._apply_self_weight).pack(pady=2)

        ttk.Separator(self.prop_content, orient="horizontal").pack(fill="x", pady=6)
        tk.Label(self.prop_content, text="Reference Levels:", bg=C["surface0"], fg=C["subtext1"],
                 font=self.F["bold"]).pack()
        frl = tk.Frame(self.prop_content, bg=C["surface0"])
        frl.pack(pady=2)
        tk.Label(frl, text="Y:", bg=C["surface0"], fg=C["subtext1"], font=self.F["norm"]).pack(side="left")
        self.entry_ref_y = ttk.Entry(frl, width=7, justify="center")
        self.entry_ref_y.pack(side="left", padx=1)
        self.entry_ref_y.insert(0, "0")
        tk.Label(frl, text="Label:", bg=C["surface0"], fg=C["subtext1"],
                 font=self.F["norm"]).pack(side="left", padx=(6, 0))
        self.entry_ref_label = ttk.Entry(frl, width=12, justify="center")
        self.entry_ref_label.pack(side="left", padx=1)
        self.entry_ref_label.insert(0, "Ground")
        tk.Label(frl, text="Color:", bg=C["surface0"], fg=C["subtext1"],
                 font=self.F["norm"]).pack(side="left", padx=(6, 0))
        self.ref_color_var = tk.StringVar(value="Green")
        ttk.Combobox(frl, textvariable=self.ref_color_var,
                      values=["Green", "Red", "Blue", "Yellow", "Orange", "Purple"],
                      state="readonly", width=7, font=self.F["norm"]).pack(side="left", padx=1)
        self._make_btn(self.prop_content, "➕ Add Ref Line", C["teal"], C["green"],
                       self._add_ref_line).pack(pady=2)
        self.ref_list_frame = tk.Frame(self.prop_content, bg=C["surface0"])
        self.ref_list_frame.pack(fill="x", pady=2)
        self._rebuild_ref_list()

    def _apply_view(self):
        try:
            xmin = float(self.entry_xmin.get())
            xmax = float(self.entry_xmax.get())
            ymin = float(self.entry_ymin.get())
            ymax = float(self.entry_ymax.get())
            grid = float(self.entry_grid.get())
        except ValueError:
            messagebox.showerror("Error", "All values must be numbers.")
            return
        if xmin >= xmax or ymin >= ymax:
            messagebox.showerror("Error", "min must be less than max.")
            return
        if grid <= 0:
            messagebox.showerror("Error", "Grid step must be positive.")
            return
        self.x_min, self.x_max = xmin, xmax
        self.y_min, self.y_max = ymin, ymax
        self.snap_grid = grid
        self._update_transform()
        self.draw()
        self.status(f"Axes: X[{xmin}, {xmax}]  Y[{ymin}, {ymax}]  Grid={grid}")

    def _add_ref_line(self):
        try:
            y = float(self.entry_ref_y.get())
        except ValueError:
            messagebox.showerror("Error", "Y must be a number.")
            return
        label = self.entry_ref_label.get().strip() or f"Y={y:.2f}"
        color_name = self.ref_color_var.get()
        color = self._REF_COLORS.get(color_name, C["green"])
        self.ref_lines.append((y, label, color_name))
        self._rebuild_ref_list()
        self.draw()
        self.status(f"Ref line '{label}' at Y={y:.2f} added.")

    def _remove_ref_line(self, idx):
        if 0 <= idx < len(self.ref_lines):
            self.ref_lines.pop(idx)
            self._rebuild_ref_list()
            self.draw()

    def _rebuild_ref_list(self):
        for w in self.ref_list_frame.winfo_children():
            w.destroy()
        if not self.ref_lines:
            tk.Label(self.ref_list_frame, text="(None)", bg=C["surface0"],
                     fg=C["subtext0"], font=self.F["norm"]).pack()
            return
        for i, (y, lbl, cname) in enumerate(self.ref_lines):
            f = tk.Frame(self.ref_list_frame, bg=C["surface0"])
            f.pack(fill="x", pady=1)
            color_hex = self._REF_COLORS.get(cname, C["green"])
            tk.Canvas(f, width=12, height=12, bg=color_hex, highlightthickness=0,
                      bd=0).pack(side="left", padx=2)
            tk.Label(f, text=f"{lbl} (Y={y:.2f})", bg=C["surface0"], fg=C["text"],
                     font=self.F["norm"], anchor="w").pack(side="left", fill="x", expand=True)
            tk.Button(f, text="✕", bg=C["surface0"], fg=C["pink"], bd=0, cursor="hand2",
                       font=self.F["bold"], command=lambda i=i: self._remove_ref_line(i)).pack(side="right")

    def _apply_self_weight(self):
        if not self.members:
            self.status("No Members defined.")
            return
        try:
            w = float(self.entry_selfw.get())
        except ValueError:
            messagebox.showerror("Error", "Unit weight must be a number.")
            return
        if w <= 0:
            self.status("Zero weight — no loads added.")
            return
        node_loads = {}
        for i, j in self.members:
            x1, y1 = self.nodes[i]
            x2, y2 = self.nodes[j]
            L = math.hypot(x2 - x1, y2 - y1)
            total_w = w * L
            half = total_w / 2
            node_loads[i] = node_loads.get(i, (0, 0))
            node_loads[i] = (node_loads[i][0], node_loads[i][1] - half)
            node_loads[j] = node_loads.get(j, (0, 0))
            node_loads[j] = (node_loads[j][0], node_loads[j][1] - half)
        for ni, (fx, fy) in node_loads.items():
            found = False
            for k, (n, efx, efy) in enumerate(self.loads):
                if n == ni:
                    self.loads[k] = (ni, efx + fx, efy + fy)
                    found = True
                    break
            if not found:
                self.loads.append((ni, fx, fy))
        self.solved = False
        total = sum(abs(fy) for _, _, fy in self.loads if fy < 0)
        self.status(f"Self-weight distributed. Total vertical load added: {total:.2f} kN")
        self.draw()

    def to_canvas(self, x, y):
        return self.ox + x * self.scale, self.oy - y * self.scale

    def from_canvas(self, px, py):
        return (px - self.ox) / self.scale, (self.oy - py) / self.scale

    def snap(self, val):
        return round(val / self.snap_grid) * self.snap_grid

    def _frange(self, start, stop, step):
        r = []
        v = start
        while v <= stop:
            r.append(v)
            v += step
        return r

    def find_node(self, cx, cy, tol=12.0):
        for i, (nx, ny) in enumerate(self.nodes):
            px, py = self.to_canvas(nx, ny)
            if (px - cx) ** 2 + (py - cy) ** 2 < tol ** 2:
                return i
        return None

    def find_member(self, cx, cy, tol=10.0):
        for k, (i, j) in enumerate(self.members):
            x1, y1 = self.to_canvas(*self.nodes[i])
            x2, y2 = self.to_canvas(*self.nodes[j])
            d = self._dist_to_seg(cx, cy, x1, y1, x2, y2)
            if d < tol:
                return k
        return None

    def _dist_to_seg(self, px, py, x1, y1, x2, y2):
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(px - x1, py - y1)
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))

    def on_zoom(self, e):
        scale_factor = 1.1
        if e.delta > 0:
            self.scale *= scale_factor
        else:
            self.scale /= scale_factor
        self.scale = max(5, min(self.scale, 200))
        self.draw()

    def on_motion(self, e):
        self.hover_node = self.find_node(e.x, e.y, 10)
        self.hover_member = None if self.hover_node is not None else self.find_member(e.x, e.y, 8)
        self.draw()

    def _apply_dim(self, mk, i, j):
        try:
            new_L = float(self.entry_dim_L.get())
            new_ang = float(self.entry_dim_ang.get())
        except ValueError:
            messagebox.showerror("Error", "L and angle must be numbers.")
            return
        if new_L <= 0:
            messagebox.showerror("Error", "Length must be positive.")
            return
        rad = math.radians(new_ang)
        new_dx = new_L * math.cos(rad)
        new_dy = new_L * math.sin(rad)
        x1, y1 = self.nodes[i]
        self.nodes[j] = (round(x1 + new_dx, 4), round(y1 + new_dy, 4))
        self.solved = False
        self.status(f"Member {mk} updated: L={new_L:.3f}, angle={new_ang:.1f}°")
        self.draw()

    def on_click(self, e):
        if self.current_tool == "node":
            x, y = self.from_canvas(e.x, e.y)
            x, y = self.snap(x), self.snap(y)
            self.nodes.append((x, y))
            self.solved = False
            self.status(f"Node {len(self.nodes)-1}: ({x:.2f}, {y:.2f})")
            self.entry_nx.delete(0, "end"); self.entry_nx.insert(0, f"{x:.2f}")
            self.entry_ny.delete(0, "end"); self.entry_ny.insert(0, f"{y:.2f}")
            self.draw()

        elif self.current_tool == "member":
            ni = self.find_node(e.x, e.y)
            if ni is None:
                return
            if self.selected_node is None:
                self.selected_node = ni
                self.status(f"First node {ni} selected. Click second node.")
                self.draw()
            else:
                if ni != self.selected_node:
                    self.members.append((self.selected_node, ni))
                    self.solved = False
                    self.status(f"Member {self.selected_node}-{ni} added.")
                self.selected_node = None
                self.draw()

        elif self.current_tool == "support":
            ni = self.find_node(e.x, e.y)
            if ni is None:
                return
            sup_map = {"Pinned (Rx,Ry)": "pinned", "Fixed (Rx,Ry,M)": "fixed",
                       "Roller V (Ry)": "roller", "Roller H (Rx)": "roller_x",
                       "Cable (Rx,Ry)": "cable"}
            rtype = sup_map.get(self.sup_var.get(), "pinned")
            idx = None
            for i, (n, _) in enumerate(self.supports):
                if n == ni:
                    idx = i
                    break
            if idx is not None:
                self.supports[idx] = (ni, rtype)
                self.status(f"Support at node {ni} changed to {rtype}.")
            else:
                self.supports.append((ni, rtype))
                self.status(f"Support {rtype} added to node {ni}.")
            self.solved = False
            self.draw()

        elif self.current_tool == "load":
            ni = self.find_node(e.x, e.y)
            if ni is None:
                return
            try:
                fx = float(self.entry_fx.get())
                fy = float(self.entry_fy.get())
            except ValueError:
                messagebox.showerror("Error", "Fx and Fy must be numbers.")
                return
            if abs(fx) < 1e-12 and abs(fy) < 1e-12:
                self.status("Zero load ignored.")
                return
            idx = None
            for i, (n, _, _) in enumerate(self.loads):
                if n == ni:
                    idx = i
                    break
            if idx is not None:
                self.loads[idx] = (ni, fx, fy)
                self.status(f"Load at node {ni} changed to ({fx}, {fy}).")
            else:
                self.loads.append((ni, fx, fy))
                self.status(f"Load ({fx}, {fy}) added to node {ni}.")
            self.solved = False
            self.draw()

        elif self.current_tool == "dim":
            mk = self.find_member(e.x, e.y, 10)
            if mk is not None:
                i, j = self.members[mk]
                x1, y1 = self.nodes[i]
                x2, y2 = self.nodes[j]
                dx = x2 - x1
                dy = y2 - y1
                L = math.hypot(dx, dy)
                self._dim_member_idx = mk
                self._clear_prop()
                hdr = tk.Label(self.prop_content, text=f"Edit Member {mk}  ({i}→{j})",
                               bg=C["surface0"], fg=C["peach"], font=self.F["bold"])
                hdr.pack(pady=(0, 4))
                fr_l = tk.Frame(self.prop_content, bg=C["surface0"])
                fr_l.pack()
                tk.Label(fr_l, text="L (m):", bg=C["surface0"], fg=C["subtext1"],
                         font=self.F["norm"]).pack(side="left")
                self.entry_dim_L = ttk.Entry(fr_l, width=9, justify="center")
                self.entry_dim_L.pack(side="left", padx=2)
                self.entry_dim_L.insert(0, f"{L:.3f}")
                tk.Label(fr_l, text="Angle°:", bg=C["surface0"], fg=C["subtext1"],
                         font=self.F["norm"]).pack(side="left", padx=(6, 0))
                self.entry_dim_ang = ttk.Entry(fr_l, width=7, justify="center")
                self.entry_dim_ang.pack(side="left", padx=2)
                self.entry_dim_ang.insert(0, f"{math.degrees(math.atan2(dy, dx)):.1f}")
                fr_d = tk.Frame(self.prop_content, bg=C["surface0"])
                fr_d.pack(pady=2)
                tk.Label(fr_d, text="Δx:", bg=C["surface0"], fg=C["subtext1"],
                         font=self.F["norm"]).pack(side="left")
                self.entry_dim_dx = ttk.Entry(fr_d, width=9, justify="center")
                self.entry_dim_dx.pack(side="left", padx=2)
                self.entry_dim_dx.insert(0, f"{dx:.3f}")
                tk.Label(fr_d, text="Δy:", bg=C["surface0"], fg=C["subtext1"],
                         font=self.F["norm"]).pack(side="left", padx=(6, 0))
                self.entry_dim_dy = ttk.Entry(fr_d, width=9, justify="center")
                self.entry_dim_dy.pack(side="left", padx=2)
                self.entry_dim_dy.insert(0, f"{dy:.3f}")
                self._make_btn(self.prop_content, "✓ Apply Changes", C["green"], C["teal"],
                               lambda mki=mk, ii=i, ji=j: self._apply_dim(mki, ii, ji)).pack(pady=4)
                for e in (self.entry_dim_L, self.entry_dim_ang, self.entry_dim_dx, self.entry_dim_dy):
                    e.bind("<Return>", lambda ev: self._apply_dim(mk, i, j))
                self.canvas.delete("dim_overlay")
                px1, py1 = self.to_canvas(x1, y1)
                px2, py2 = self.to_canvas(x2, y2)
                self.canvas.create_line(px1, py1 + 4, px1, py2 - 4, fill=C["peach"], dash=(3, 3), tags="dim_overlay")
                self.canvas.create_line(px1 + 4, py1, px2 - 4, py1, fill=C["peach"], dash=(3, 3), tags="dim_overlay")
            else:
                self.status("No Member there.")

        elif self.current_tool == "delete":
            ni = self.find_node(e.x, e.y, 12)
            if ni is not None:
                self._delete_node(ni)
                self.status(f"Node {ni} deleted.")
                self.draw()
                return
            mk = self.find_member(e.x, e.y, 10)
            if mk is not None:
                self.members.pop(mk)
                self.solved = False
                self.status(f"Member {mk} deleted.")
                self.draw()

        elif self.current_tool == "select":
            ni = self.find_node(e.x, e.y, 12)
            if ni is not None:
                self.drag_node = ni
                px, py = self.to_canvas(*self.nodes[ni])
                self.drag_offsets = (e.x - px, e.y - py)

    def on_drag(self, e):
        if self.current_tool == "select" and self.drag_node is not None:
            nx = (e.x - self.drag_offsets[0] - self.ox) / self.scale
            ny = (self.oy - (e.y - self.drag_offsets[1])) / self.scale
            nx, ny = self.snap(nx), self.snap(ny)
            self.nodes[self.drag_node] = (nx, ny)
            self.solved = False
            self.draw()

    def on_release(self, e):
        if self.drag_node is not None:
            self.status(f"Node {self.drag_node} moved.")
        self.drag_node = None

    def on_key(self, e):
        key = e.char
        tools = {"1": "node", "2": "member", "3": "support", "4": "load", "5": "dim", "6": "delete", "7": "select"}
        if key in tools:
            self.set_tool(tools[key])

    def on_arrow(self, e):
        if not self.nodes or self.current_tool != "node":
            return
        i = len(self.nodes) - 1
        x, y = self.nodes[i]
        step = self.snap_grid
        if e.keysym == "Up":
            y += step
        elif e.keysym == "Down":
            y -= step
        elif e.keysym == "Left":
            x -= step
        elif e.keysym == "Right":
            x += step
        x, y = self.snap(x), self.snap(y)
        self.nodes[i] = (x, y)
        self.solved = False
        self.entry_nx.delete(0, "end"); self.entry_nx.insert(0, f"{x:.2f}")
        self.entry_ny.delete(0, "end"); self.entry_ny.insert(0, f"{y:.2f}")
        self.status(f"Node {i}: ({x:.2f}, {y:.2f})")
        self.draw()

    def _delete_node(self, ni):
        self.members = [(i, j) for (i, j) in self.members if i != ni and j != ni]
        self.members = [(i if i < ni else i - 1, j if j < ni else j - 1) for (i, j) in self.members]
        self.supports = [(i, t) for (i, t) in self.supports if i != ni]
        self.supports = [(i if i < ni else i - 1, t) for (i, t) in self.supports]
        self.loads = [(i, fx, fy) for (i, fx, fy) in self.loads if i != ni]
        self.loads = [(i if i < ni else i - 1, fx, fy) for (i, fx, fy) in self.loads]
        self.nodes.pop(ni)
        self.solved = False

    def solve(self):
        if len(self.nodes) < 2:
            messagebox.showwarning("Warning", "At least 2 nodes needed.")
            return
        if not self.members:
            messagebox.showwarning("Warning", "No Members defined.")
            return
        if not self.supports:
            messagebox.showwarning("Warning", "Place at least one support.")
            return
        try:
            forces, reactions = truss.solve_truss(self.nodes, self.members, self.supports, self.loads)
        except Exception as e:
            messagebox.showerror("Error", f"Truss cannot be solved:\n{str(e)}")
            return
        self.forces = list(forces)
        self.reactions = list(reactions)
        self.solved = True
        for item in self.tree.get_children():
            self.tree.delete(item)
        for k, (i, j) in enumerate(self.members):
            f = forces[k]
            if abs(f) < 1e-6:
                typ, tag = "Zero", "zero"
            elif f > 0:
                typ, tag = "Tension ✓", "tension"
            else:
                typ, tag = "Compression ✗", "compression"
            self.tree.insert("", "end", values=(f"{i}-{j}", f"{f:.3f}", typ), tags=(tag,))
        rlist = []
        rk = 0
        for idx, rtype in self.supports:
            if rtype in ("pinned", "fixed"):
                rlist.append(f"R{idx}x={reactions[rk]:.2f}"); rk += 1
                rlist.append(f"R{idx}y={reactions[rk]:.2f}"); rk += 1
            elif rtype == "roller":
                rlist.append(f"R{idx}y={reactions[rk]:.2f}"); rk += 1
            elif rtype == "roller_x":
                rlist.append(f"R{idx}x={reactions[rk]:.2f}"); rk += 1
        self.react_label.config(text=", ".join(rlist), fg=C["green"])
        self.status(f"Solved. {len(forces)} members")
        self.draw()

    def reset_all(self):
        self.nodes.clear()
        self.members.clear()
        self.ref_lines.clear()
        self.supports.clear()
        self.loads.clear()
        self.forces.clear()
        self.reactions.clear()
        self.solved = False
        self.selected_node = None
        self.drag_node = None
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.react_label.config(text="Cleared.", fg=C["subtext0"])
        self.canvas.delete("all")
        self.status("All cleared.")

    def draw(self, event=None):
        c = self.canvas
        c.delete("all")
        cw = c.winfo_width()
        ch = c.winfo_height()
        if cw < 20 or ch < 20:
            return

        # grid
        step = self.snap_grid * self.scale
        start_x = self.ox % step
        start_y = self.oy % step
        for gx in range(int(start_x), cw, int(step)):
            c.create_line(gx, 0, gx, ch, fill=C["mantle"], width=1)
        for gy in range(int(start_y), ch, int(step)):
            c.create_line(0, gy, cw, gy, fill=C["mantle"], width=1)

        # reference lines (ground/ceiling)
        for y, label, cname in self.ref_lines:
            py = self.oy - y * self.scale
            if 10 <= py <= ch - 10:
                color = self._REF_COLORS.get(cname, C["green"])
                c.create_line(10, py, cw - 10, py, fill=color, width=3, dash=(8, 4))
                c.create_text(15, py - 8, text=label, fill=color, anchor="w",
                              font=(self.font_family, 9, "bold"))

        # axes
        ox, oy = self.to_canvas(0, 0)
        if 0 <= ox <= cw:
            c.create_line(ox, 0, ox, ch, fill=C["overlay0"], dash=(4, 4))
        if 0 <= oy <= ch:
            c.create_line(0, oy, cw, oy, fill=C["overlay0"], dash=(4, 4))
        # axis labels and tick marks
        step_px = self.snap_grid * self.scale
        if step_px > 20:
            x_start = int(math.ceil(self.x_min / self.snap_grid)) * self.snap_grid
            x_end = int(math.floor(self.x_max / self.snap_grid)) * self.snap_grid
            x_vals = [round(v, 4) for v in self._frange(x_start, x_end + self.snap_grid * 0.5, self.snap_grid)]
            for x_val in x_vals:
                px = self.ox + x_val * self.scale
                if 10 <= px <= cw - 10:
                    c.create_line(px, oy - 4, px, oy + 4, fill=C["overlay0"], width=1)
                    if abs(x_val) > 1e-9 and abs(px - ox) > 10:
                        c.create_text(px, oy + 12, text=f"{x_val:.1f}".rstrip("0").rstrip("."), fill=C["overlay0"],
                                      font=(self.font_family, 8))
            y_start = int(math.ceil(self.y_min / self.snap_grid)) * self.snap_grid
            y_end = int(math.floor(self.y_max / self.snap_grid)) * self.snap_grid
            y_vals = [round(v, 4) for v in self._frange(y_start, y_end + self.snap_grid * 0.5, self.snap_grid)]
            for y_val in y_vals:
                py = self.oy - y_val * self.scale
                if 10 <= py <= ch - 10:
                    c.create_line(ox - 4, py, ox + 4, py, fill=C["overlay0"], width=1)
                    if abs(y_val) > 1e-9 and abs(py - oy) > 10:
                        c.create_text(ox - 10, py, text=f"{y_val:.1f}".rstrip("0").rstrip("."), fill=C["overlay0"],
                                      font=(self.font_family, 8), anchor="e")

        # members
        for k, (i, j) in enumerate(self.members):
            x1, y1 = self.to_canvas(*self.nodes[i])
            x2, y2 = self.to_canvas(*self.nodes[j])
            color = C["overlay0"]
            width = 2
            label = ""
            if self.solved and k < len(self.forces):
                f = self.forces[k]
                label = f"{f:.1f}"
                if f > 1e-6:
                    color = C["green"]; width = 3
                elif f < -1e-6:
                    color = C["pink"]; width = 3
                else:
                    color = C["overlay0"]
            if self.hover_member == k and not self.solved:
                color = C["yellow"]; width = 3
            c.create_line(x1, y1, x2, y2, fill=color, width=width)
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            if label:
                c.create_text(mx, my - 12, text=label, fill=C["yellow"], font=self.F["bold"])

        # nodes
        for i, (x, y) in enumerate(self.nodes):
            px, py = self.to_canvas(x, y)
            r = 7
            fill = C["blue"]
            if i == self.hover_node:
                fill = C["lavender"]; r = 9
            if i == self.selected_node:
                fill = C["pink"]; r = 9
            c.create_oval(px - r, py - r, px + r, py + r, fill=fill, outline=C["crust"], width=2)
            c.create_text(px, py - 16, text=str(i), fill=C["text"], font=self.F["bold"])

        # supports
        for idx, rtype in self.supports:
            x, y = self.nodes[idx]
            px, py = self.to_canvas(x, y)
            if rtype == "pinned":
                c.create_polygon(px - 10, py + 5, px + 10, py + 5, px, py + 18,
                                 fill=C["yellow"], outline=C["crust"])
                c.create_line(px - 7, py + 5, px + 7, py + 5, fill=C["crust"], width=2)
            elif rtype == "fixed":
                c.create_rectangle(px - 12, py + 5, px + 12, py + 22,
                                   fill=C["yellow"], outline=C["crust"], width=2)
                for yy in range(8, 21, 4):
                    c.create_line(px - 10, py + yy, px + 10, py + yy, fill=C["crust"], width=1)
            elif rtype == "cable":
                anchor_x, anchor_y = px, py + 50
                c.create_line(px, py, anchor_x, anchor_y, fill=C["teal"], width=2, dash=(4, 3))
                c.create_polygon(anchor_x - 8, anchor_y + 2, anchor_x + 8, anchor_y + 2,
                                 anchor_x, anchor_y + 12, fill=C["teal"], outline=C["crust"])
            elif rtype == "roller":
                c.create_polygon(px - 10, py + 5, px + 10, py + 5, px, py + 18,
                                 fill=C["yellow"], outline=C["crust"])
                c.create_oval(px - 5, py + 18, px + 5, py + 26, fill=C["yellow"], outline=C["crust"])
                c.create_line(px - 7, py + 5, px + 7, py + 5, fill=C["crust"], width=2)
            elif rtype == "roller_x":
                c.create_polygon(px + 5, py - 10, px + 5, py + 10, px + 18, py,
                                 fill=C["yellow"], outline=C["crust"])
                c.create_oval(px + 18, py - 5, px + 26, py + 5, fill=C["yellow"], outline=C["crust"])
                c.create_line(px + 5, py - 7, px + 5, py + 7, fill=C["crust"], width=2)

        # loads
        for idx, fx, fy in self.loads:
            x, y = self.nodes[idx]
            px, py = self.to_canvas(x, y)
            mag = math.hypot(fx, fy)
            if mag < 1e-12:
                continue
            s = self.scale * 0.3
            ex, ey = px + fx * s / mag, py - fy * s / mag
            c.create_line(px, py, ex, ey, fill=C["pink"], width=3, arrow="last", arrowshape=(10, 12, 6))
            mid_x, mid_y = (px + ex) / 2, (py + ey) / 2
            lbl = []
            if abs(fx) > 1e-6:
                lbl.append(f"Fx={fx:.1f}")
            if abs(fy) > 1e-6:
                lbl.append(f"Fy={fy:.1f}")
            c.create_text(mid_x + 14, mid_y - 6, text=", ".join(lbl),
                          fill=C["pink"], font=self.F["bold"], anchor="w")

        # coordinate origin label
        if 0 <= ox <= cw and 0 <= oy <= ch:
            c.create_text(ox + 6, oy - 6, text="O", fill=C["overlay0"], anchor="nw", font=self.F["bold"])
            c.create_text(cw - 10, oy - 10, text="X", fill=C["overlay0"], font=self.F["bold"])
            c.create_text(ox + 10, 10, text="Y", fill=C["overlay0"], font=self.F["bold"])

        self._recalc_limits()
