"""Top toolbar with search and export controls."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class Toolbar(ttk.Frame):
    """Search field and export actions."""

    def __init__(self, master: tk.Widget, on_search, on_export_png, on_export_pdf) -> None:
        super().__init__(master, padding=(16, 12), style="Toolbar.TFrame")
        self.search_var = tk.StringVar()
        ttk.Label(self, text="Dashboard Estudiantil Universitario", style="Title.TLabel").pack(side="left")
        search = ttk.Entry(self, textvariable=self.search_var, width=32)
        search.pack(side="left", padx=(24, 8))
        search.insert(0, "")
        ttk.Label(self, text="Buscar nombre", style="Hint.TLabel").pack(side="left", padx=(0, 14))
        ttk.Button(self, text="Exportar PNG", command=on_export_png).pack(side="right", padx=(6, 0))
        ttk.Button(self, text="Exportar PDF", command=on_export_pdf).pack(side="right")
        self.search_var.trace_add("write", lambda *_: on_search())
