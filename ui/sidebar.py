"""Sidebar filters for program, semester, condition, gender and status."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core.data_loader import GENDERS, PROGRAMS, SEMESTERS, STATES


class Sidebar(ttk.Frame):
    """Left-side filter panel."""

    def __init__(self, master: tk.Widget, on_change, on_open_dataset) -> None:
        super().__init__(master, padding=14, style="Sidebar.TFrame")
        self.on_change = on_change
        self.on_open_dataset = on_open_dataset
        self.program_var = tk.StringVar(value="Todos")
        self.semester_var = tk.StringVar(value="Todos")
        self.gender_var = tk.StringVar(value="Todos")
        self.state_var = tk.StringVar(value="Todos")
        self.condition_vars = {
            "Aplazamiento": tk.BooleanVar(value=False),
            "Deserción voluntaria": tk.BooleanVar(value=False),
            "Bajo rendimiento": tk.BooleanVar(value=False),
        }
        self._build()

    def _build(self) -> None:
        ttk.Label(self, text="UNIVERSIDAD NOVA ANDINA", style="Brand.TLabel").pack(anchor="w", pady=(0, 2))
        ttk.Label(self, text="Cohortes 2022-2025", style="Muted.TLabel").pack(anchor="w", pady=(0, 16))

        ttk.Button(self, text="Ver dataset", command=self.on_open_dataset).pack(fill="x", pady=(0, 14))
        ttk.Separator(self).pack(fill="x", pady=(0, 12))

        ttk.Label(self, text="Carrera", style="Section.TLabel").pack(anchor="w")
        for program in ["Todos", *PROGRAMS]:
            ttk.Radiobutton(self, text=program, variable=self.program_var, value=program, command=self.on_change).pack(anchor="w", pady=2)

        ttk.Separator(self).pack(fill="x", pady=12)
        ttk.Label(self, text="Semestre", style="Section.TLabel").pack(anchor="w")
        ttk.Combobox(self, textvariable=self.semester_var, values=["Todos", *SEMESTERS], state="readonly").pack(fill="x", pady=(4, 8))
        self.semester_var.trace_add("write", lambda *_: self.on_change())

        ttk.Label(self, text="Condición", style="Section.TLabel").pack(anchor="w", pady=(8, 0))
        for label, var in self.condition_vars.items():
            ttk.Checkbutton(self, text=label, variable=var, command=self.on_change).pack(anchor="w", pady=2)

        ttk.Label(self, text="Género", style="Section.TLabel").pack(anchor="w", pady=(12, 0))
        for gender in ["Todos", *GENDERS]:
            ttk.Radiobutton(self, text=gender, variable=self.gender_var, value=gender, command=self.on_change).pack(anchor="w", pady=2)

        ttk.Label(self, text="Estado", style="Section.TLabel").pack(anchor="w", pady=(12, 0))
        ttk.Combobox(self, textvariable=self.state_var, values=["Todos", *STATES], state="readonly").pack(fill="x", pady=(4, 0))
        self.state_var.trace_add("write", lambda *_: self.on_change())

    def selected_conditions(self) -> set[str]:
        return {label for label, var in self.condition_vars.items() if var.get()}
