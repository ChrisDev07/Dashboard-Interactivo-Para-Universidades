"""Treeview table for detailed student records."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import pandas as pd


class TableWidget(ttk.Frame):
    """Sortable table backed by a pandas dataframe."""

    COLUMNS = [
        "id_estudiante",
        "nombre",
        "genero",
        "programa",
        "semestre_ingreso",
        "semestre_actual",
        "aplazamiento",
        "desercion_voluntaria",
        "bajo_rendimiento",
        "estado",
    ]

    def __init__(self, master: tk.Widget, columns: list[str] | None = None) -> None:
        super().__init__(master, padding=(0, 8, 0, 0))
        self.dataframe = pd.DataFrame()
        self.sort_descending = False
        self.columns = columns or self.COLUMNS
        self.tree = ttk.Treeview(self, columns=self.columns, show="headings", height=13)
        yscroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        xscroll = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        for column in self.columns:
            self.tree.heading(column, text=column, command=lambda col=column: self.sort_by(col))
            self.tree.column(column, minwidth=90, width=130, anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def update_data(self, dataframe: pd.DataFrame) -> None:
        self.dataframe = dataframe.copy()
        self._refresh()

    def sort_by(self, column: str) -> None:
        if self.dataframe.empty:
            return
        self.sort_descending = not self.sort_descending
        self.dataframe = self.dataframe.sort_values(column, ascending=not self.sort_descending)
        self._refresh()

    def _refresh(self) -> None:
        self.tree.delete(*self.tree.get_children())
        if self.dataframe.empty:
            return
        display_df = self.dataframe[self.columns].fillna("").copy()
        for _, row in display_df.iterrows():
            values = [str(row[column]) for column in self.columns]
            self.tree.insert("", "end", values=values)
