"""KPI card widget."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class CardWidget(ttk.Frame):
    """Small KPI card with a title and value."""

    def __init__(self, master: tk.Widget, title: str) -> None:
        super().__init__(master, style="Card.TFrame", padding=(14, 12))
        self.title = title
        self.value = "0"
        self.progress = 0.0
        self.header = ttk.Frame(self, style="Card.TFrame")
        self.header.pack(fill="x")
        self.title_label = ttk.Label(self.header, text=title, style="CardTitle.TLabel")
        self.title_label.pack(side="left")
        self.drag_handle = ttk.Label(self.header, text="Mover", style="DragHandle.TLabel", cursor="fleur")
        self.drag_handle.pack(side="right")
        self.value_label = ttk.Label(self, text="0", style="CardValue.TLabel")
        self.value_label.pack(anchor="w", pady=(10, 0))
        self.caption_label = ttk.Label(self, text="Indicador filtrado", style="CardCaption.TLabel")
        self.caption_label.pack(anchor="w", pady=(2, 0))
        self.canvas = tk.Canvas(
            self,
            height=42,
            bd=0,
            highlightthickness=0,
            background="#132238",
        )
        self.canvas.pack(fill="x", pady=(12, 0))
        self.canvas.bind("<Configure>", lambda _event: self._draw_canvas())

    def set_value(self, value: str) -> None:
        self.value = value
        self.progress = self._progress_from_value(value)
        self.value_label.configure(text=value)
        self.caption_label.configure(text=self._caption())
        self._draw_canvas()

    def _progress_from_value(self, value: str) -> float:
        if value.endswith("%"):
            try:
                return max(0.0, min(float(value[:-1]) / 100, 1.0))
            except ValueError:
                return 0.0
        if self.title == "Género":
            numbers = []
            for part in value.replace("/", " ").split():
                if part.isdigit():
                    numbers.append(int(part))
            total = sum(numbers)
            return 0.5 if total else 0.0
        try:
            numeric = float(value.replace(",", "."))
        except ValueError:
            return 0.0
        return max(0.05, min(numeric / 500, 1.0))

    def _caption(self) -> str:
        captions = {
            "Total estudiantes": "Registros visibles en la vista",
            "Aplazamientos": "Porcentaje de estudiantes con pausa",
            "Deserciones voluntarias": "Retiro declarado por el estudiante",
            "Bajo rendimiento": "Alertas académicas activas",
            "Género": "Distribución por población filtrada",
        }
        return captions.get(self.title, "Indicador filtrado")

    def _draw_canvas(self) -> None:
        width = max(self.canvas.winfo_width(), 160)
        height = max(self.canvas.winfo_height(), 42)
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, width, height, fill="#132238", outline="")
        self.canvas.create_rectangle(0, height - 9, width, height, fill="#0B1628", outline="")
        bar_width = max(18, int(width * self.progress))
        self.canvas.create_rectangle(0, height - 9, bar_width, height, fill="#2DD4BF", outline="")

        points = self._sparkline_points(width, height)
        if len(points) > 2:
            self.canvas.create_line(points, fill="#8BE9DD", width=2, smooth=True)
            last_x, last_y = points[-2], points[-1]
            self.canvas.create_oval(last_x - 4, last_y - 4, last_x + 4, last_y + 4, fill="#FFD166", outline="")

        self.canvas.create_text(
            width - 10,
            11,
            text=f"{int(self.progress * 100)}%",
            anchor="e",
            fill="#B7C8DD",
            font=("Segoe UI", 8, "bold"),
        )

    def _sparkline_points(self, width: int, height: int) -> list[int]:
        base = max(0.08, self.progress)
        values = [
            0.18,
            min(0.95, base * 0.52 + 0.12),
            min(0.95, base * 0.74 + 0.08),
            min(0.95, base * 0.62 + 0.24),
            min(0.95, base * 0.9 + 0.06),
            min(0.95, base),
        ]
        points: list[int] = []
        usable_width = width - 24
        for index, value in enumerate(values):
            x = 12 + int((usable_width / (len(values) - 1)) * index)
            y = 30 - int(value * 20)
            points.extend([x, max(7, min(height - 14, y))])
        return points

    def drag_handles(self) -> list[tk.Widget]:
        return [self.drag_handle, self.header]
