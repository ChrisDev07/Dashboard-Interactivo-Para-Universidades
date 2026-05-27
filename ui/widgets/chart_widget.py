"""Embedded HTML chart widget using TkinterWeb when available."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
import tempfile
import tkinter as tk
from tkinter import ttk
import webbrowser

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except Exception:  # pragma: no cover - depends on Pillow ImageTk system package
    FigureCanvasTkAgg = None


try:
    from tkinterweb import HtmlFrame
except Exception:  # pragma: no cover - optional dependency fallback
    HtmlFrame = None


class ChartWidget(ttk.LabelFrame):
    """Render Chart.js or Three.js templates inside Tkinter."""

    def __init__(self, master: tk.Widget, title: str, template_path: Path, on_line_point_click=None) -> None:
        super().__init__(master, text=title, padding=8)
        self.template_path = template_path
        self.on_line_point_click = on_line_point_click
        self.last_html = ""
        self.current_data: dict = {}
        self.browser = None
        self.fallback = None
        self.figure = None
        self.canvas = None
        self.image_label = None
        self.photo_image = None
        self.uses_tkagg = False
        self.drag_handle = None
        if HtmlFrame:
            try:
                self.browser = HtmlFrame(self, messages_enabled=False)
                self.browser.pack(fill="both", expand=True)
            except Exception as exc:  # pragma: no cover - depends on local Tcl/Tk build
                self._build_fallback(f"TkinterWeb no pudo iniciar: {exc}")
        if not self.browser:
            self._build_fallback("Instale una version compatible de TkinterWeb/Tkhtml para ver la grafica embebida.")

    def _build_fallback(self, message: str) -> None:
        if self.fallback:
            return
        toolbar = ttk.Frame(self, style="ChartToolbar.TFrame")
        toolbar.pack(fill="x", pady=(0, 6))
        self.drag_handle = ttk.Label(toolbar, text="Mover panel", style="DragHandle.TLabel", cursor="fleur")
        self.drag_handle.pack(side="left")
        ttk.Button(toolbar, text="HTML", command=self.open_in_browser).pack(side="right")
        self.fallback = ttk.Frame(self)
        self.fallback.pack(fill="both", expand=True)
        self.figure = Figure(figsize=(5.4, 3.2), dpi=100, facecolor="#0B1628")
        if FigureCanvasTkAgg:
            self.canvas = FigureCanvasTkAgg(self.figure, master=self.fallback)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
            self.canvas.mpl_connect("button_press_event", self._on_canvas_click)
            self.uses_tkagg = True
        else:
            self.canvas = FigureCanvasAgg(self.figure)
            self.image_label = ttk.Label(self.fallback)
            self.image_label.pack(fill="both", expand=True)
        self._draw_message(message)

    def render(self, data: dict) -> None:
        self.current_data = data
        template = self.template_path.read_text(encoding="utf-8")
        self.last_html = template.replace("{{DATA_PLACEHOLDER}}", json.dumps(data, ensure_ascii=False))
        if self.browser:
            self.browser.load_html(self.last_html)
        else:
            self._draw_matplotlib(data)

    def _draw_message(self, message: str) -> None:
        self.figure.clear()
        axis = self.figure.add_subplot(111)
        axis.axis("off")
        axis.set_facecolor("#0B1628")
        axis.text(0.5, 0.5, message, ha="center", va="center", wrap=True, color="#AFC1D8")
        self._paint_figure()

    def _draw_matplotlib(self, data: dict) -> None:
        self.figure.clear()
        if "points" in data:
            axis = self.figure.add_subplot(111, projection="3d")
            axis.set_facecolor("#0B1628")
            points = data["points"]
            xs = [point["x"] for point in points]
            ys = [point["y"] for point in points]
            zs = [point["z"] for point in points]
            sizes = [34 + point["z"] * 7 for point in points]
            axis.scatter(xs, ys, zs, s=sizes, c=zs, cmap="viridis", alpha=0.94, edgecolors="#EAF2FF", linewidths=0.6)
            axis.set_xticks(range(len(data.get("semesters", []))))
            axis.set_xticklabels(data.get("semesters", []), rotation=45, ha="right", fontsize=7)
            axis.set_yticks(range(len(data.get("programs", []))))
            axis.set_yticklabels(data.get("programs", []), fontsize=7)
            axis.set_zlabel("Cantidad")
            axis.set_title(data.get("title", ""), fontsize=10, color="#2DD4BF", pad=12)
            axis.tick_params(colors="#EAF2FF")
            axis.xaxis.label.set_color("#EAF2FF")
            axis.yaxis.label.set_color("#EAF2FF")
            axis.zaxis.label.set_color("#EAF2FF")
            for pane in [axis.xaxis.pane, axis.yaxis.pane, axis.zaxis.pane]:
                pane.set_facecolor("#132238")
                pane.set_edgecolor("#243B61")
                pane.set_alpha(0.32)
        elif "datasets" in data:
            axis = self.figure.add_subplot(111)
            self._style_axis(axis)
            labels = data.get("labels", [])
            datasets = data.get("datasets", [])
            width = 0.36
            positions = list(range(len(labels)))
            colors = ["#EF476F", "#FFD166", "#60A5FA"]
            for index, dataset in enumerate(datasets):
                offset = (index - (len(datasets) - 1) / 2) * width
                axis.bar(
                    [position + offset for position in positions],
                    dataset.get("values", []),
                    width=width,
                    label=dataset.get("label", ""),
                    color=colors[index % len(colors)],
                )
            axis.set_xticks(positions)
            axis.set_xticklabels(labels, rotation=20, ha="right", fontsize=8)
            axis.set_title(data.get("title", ""), fontsize=10, color="#2DD4BF")
            axis.legend(fontsize=8, facecolor="#0B1628", edgecolor="#243B61", labelcolor="#EAF2FF")
            axis.grid(axis="y", color="#243B61", alpha=0.55)
        elif data.get("title") == "Distribución por estado":
            axis = self.figure.add_subplot(111)
            axis.set_facecolor("#0B1628")
            values = data.get("values", [])
            labels = data.get("labels", [])
            axis.pie(
                values,
                labels=labels,
                autopct=lambda pct: f"{pct:.0f}%" if pct > 0 else "",
                colors=["#2DD4BF", "#FFD166", "#EF476F", "#60A5FA"],
                startangle=90,
                wedgeprops={"width": 0.45, "edgecolor": "#0B1628", "linewidth": 2},
                textprops={"fontsize": 8, "color": "#EAF2FF"},
            )
            axis.set_title(data.get("title", ""), fontsize=10, color="#2DD4BF")
        else:
            axis = self.figure.add_subplot(111)
            self._style_axis(axis)
            labels = data.get("labels", [])
            values = data.get("values", [])
            positions = list(range(len(labels)))
            axis.plot(positions, values, marker="o", color="#2DD4BF", linewidth=3.0)
            axis.scatter(positions, values, s=72, color="#FFD166", edgecolor="#0B1628", zorder=3, picker=8)
            axis.fill_between(positions, values, color="#60A5FA", alpha=0.18)
            axis.set_xticks(positions)
            axis.set_xticklabels(labels)
            axis.set_title(data.get("title", ""), fontsize=10, color="#2DD4BF")
            axis.tick_params(axis="x", rotation=45, labelsize=8)
            axis.grid(axis="y", color="#243B61", alpha=0.55)
        self.figure.tight_layout()
        self._paint_figure()

    def _style_axis(self, axis) -> None:
        axis.set_facecolor("#0B1628")
        axis.tick_params(colors="#EAF2FF")
        for spine in axis.spines.values():
            spine.set_color("#243B61")

    def _paint_figure(self) -> None:
        if self.uses_tkagg:
            self.canvas.draw_idle()
            return
        buffer = BytesIO()
        self.canvas.draw()
        self.figure.savefig(buffer, format="png", dpi=110, facecolor="#0B1628")
        self.photo_image = tk.PhotoImage(data=buffer.getvalue())
        self.image_label.configure(image=self.photo_image)

    def _on_canvas_click(self, event) -> None:
        if not self.on_line_point_click or not self._is_line_chart() or event.xdata is None:
            return
        labels = self.current_data.get("labels", [])
        if not labels:
            return
        index = min(range(len(labels)), key=lambda item: abs(item - event.xdata))
        if abs(index - event.xdata) <= 0.35:
            self.on_line_point_click(self.current_data, index)

    def _is_line_chart(self) -> bool:
        return (
            bool(self.current_data)
            and "values" in self.current_data
            and "labels" in self.current_data
            and "datasets" not in self.current_data
            and "points" not in self.current_data
            and self.current_data.get("title") != "Distribución por estado"
        )

    def open_in_browser(self) -> None:
        if not self.last_html:
            return
        handle = tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False)
        handle.write(self.last_html)
        handle.close()
        webbrowser.open(handle.name)

    def drag_handles(self) -> list[tk.Widget]:
        return [self.drag_handle] if self.drag_handle else [self]
