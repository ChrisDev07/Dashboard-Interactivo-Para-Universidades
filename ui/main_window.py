"""Main Tkinter window, layout, filtering and widget coordination."""

from __future__ import annotations

import json
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

import pandas as pd

from core.data_processor import DashboardFilters, DataProcessor
from core.exporter import Exporter
from ui.sidebar import Sidebar
from ui.toolbar import Toolbar
from ui.widgets.card_widget import CardWidget
from ui.widgets.chart_widget import ChartWidget
from ui.widgets.table_widget import TableWidget


class DashboardApp(tk.Tk):
    """Tkinter dashboard application."""

    def __init__(self, dataframe: pd.DataFrame, base_dir: Path) -> None:
        super().__init__()
        self.title("Dashboard Estudiantil Universitario - Universidad Nova Andina")
        self.geometry("1380x860")
        self.minsize(1100, 720)
        self.base_dir = base_dir
        self.layout_path = base_dir / "config" / "layout.json"
        self.processor = DataProcessor(dataframe)
        self.exporter = Exporter(base_dir / "reports")
        self.dataframe = dataframe
        self.filtered_df = dataframe
        self.card_widgets: dict[str, CardWidget] = {}
        self.chart_widgets: list[ChartWidget] = []
        self.drag_source = None
        self.drag_source_index = 0
        self.drag_preview = None
        self.drag_preview_label = None
        self.drop_indicator = None
        self.drag_source_style = ""
        self.hero_canvas = None
        self.hero_total_text = "0"
        self.hero_context_text = "Todos"
        self._configure_style()
        self._build_layout()
        self.refresh()

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        self.configure(background="#0B1020")
        style.configure(".", font=("Segoe UI", 10), background="#0B1020", foreground="#EAF2FF")
        style.configure("TFrame", background="#0B1020")
        style.configure("Toolbar.TFrame", background="#111A2E")
        style.configure("Title.TLabel", background="#111A2E", foreground="#F8FAFC", font=("Segoe UI", 18, "bold"))
        style.configure("Hint.TLabel", background="#111A2E", foreground="#9DB0C9")
        style.configure("Brand.TLabel", background="#111A2E", foreground="#FFD166", font=("Segoe UI", 13, "bold"))
        style.configure("Muted.TLabel", background="#111A2E", foreground="#94A3B8", font=("Segoe UI", 9))
        style.configure("Section.TLabel", background="#111A2E", foreground="#5EEAD4", font=("Segoe UI", 10, "bold"))
        style.configure("Sidebar.TFrame", background="#111A2E")
        style.configure("Card.TFrame", background="#132238", relief="solid", borderwidth=1)
        style.configure("DraggingCard.TFrame", background="#1D3557", relief="solid", borderwidth=2)
        style.configure("CardTitle.TLabel", background="#132238", foreground="#AFC1D8", font=("Segoe UI", 9, "bold"))
        style.configure("CardValue.TLabel", background="#132238", foreground="#F8FAFC", font=("Segoe UI", 20, "bold"))
        style.configure("CardCaption.TLabel", background="#132238", foreground="#7F95B2", font=("Segoe UI", 8))
        style.configure("DragHandle.TLabel", background="#243B61", foreground="#EAF2FF", font=("Segoe UI", 8, "bold"), padding=(8, 3))
        style.configure("ChartToolbar.TFrame", background="#111A2E")
        style.configure("TLabelframe", background="#0B1020", foreground="#EAF2FF", bordercolor="#243B61", relief="solid")
        style.configure("Dragging.TLabelframe", background="#0B1020", bordercolor="#5EEAD4", relief="solid", borderwidth=2)
        style.configure("TLabelframe.Label", background="#0B1020", foreground="#FFD166", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", background="#2563EB", foreground="#F8FAFC", bordercolor="#60A5FA", focusthickness=0, padding=(11, 7))
        style.map("TButton", background=[("active", "#2DD4BF")], foreground=[("active", "#06121F")])
        style.configure("TEntry", fieldbackground="#132238", foreground="#F8FAFC", bordercolor="#243B61", insertcolor="#5EEAD4")
        style.configure("TCombobox", fieldbackground="#132238", background="#243B61", foreground="#F8FAFC", bordercolor="#243B61", arrowcolor="#5EEAD4")
        style.map("TCombobox", fieldbackground=[("readonly", "#132238")], foreground=[("readonly", "#F8FAFC")])
        style.configure("TRadiobutton", background="#111A2E", foreground="#EAF2FF")
        style.map("TRadiobutton", foreground=[("active", "#FFD166")], background=[("active", "#111A2E")])
        style.configure("TCheckbutton", background="#111A2E", foreground="#EAF2FF")
        style.map("TCheckbutton", foreground=[("active", "#5EEAD4")], background=[("active", "#111A2E")])
        style.configure("Treeview", background="#111A2E", fieldbackground="#111A2E", foreground="#EAF2FF", bordercolor="#243B61", rowheight=27)
        style.configure("Treeview.Heading", background="#1D3557", foreground="#FFD166", font=("Segoe UI", 9, "bold"))
        style.map("Treeview", background=[("selected", "#2563EB")], foreground=[("selected", "#F8FAFC")])

    def _build_layout(self) -> None:
        self.toolbar = Toolbar(self, self.refresh, self.export_png, self.export_pdf)
        self.toolbar.pack(side="top", fill="x")
        body = ttk.Frame(self)
        body.pack(side="top", fill="both", expand=True)
        self.sidebar = Sidebar(body, self.refresh, self.open_dataset_window)
        self.sidebar.pack(side="left", fill="y")
        self.main = ttk.Frame(body, padding=14)
        self.main.pack(side="left", fill="both", expand=True)

        self._build_hero()

        self.cards_frame = ttk.Frame(self.main)
        self.cards_frame.pack(fill="x", pady=(12, 0))
        for title in ["Total estudiantes", "Aplazamientos", "Deserciones voluntarias", "Bajo rendimiento", "Género"]:
            card = CardWidget(self.cards_frame, title)
            self.card_widgets[title] = card
            self._make_draggable(card)

        self.charts_frame = ttk.Frame(self.main)
        self.charts_frame.pack(fill="both", expand=True, pady=(12, 8))
        templates = self.base_dir / "templates"
        self.chart_widgets = [
            ChartWidget(self.charts_frame, "Evolución de inscripciones", templates / "chart_line.html", self.show_enrollment_breakdown),
            ChartWidget(self.charts_frame, "Distribución por estado", templates / "chart_pie.html"),
            ChartWidget(self.charts_frame, "Comparativa entre carreras", templates / "chart_bar.html"),
            ChartWidget(self.charts_frame, "Análisis 3D de ingresos", templates / "chart_3d.html"),
        ]
        for widget in self.chart_widgets:
            self._make_draggable(widget)

        self.table = TableWidget(self.main)
        self.table.pack(fill="both", expand=False)
        self._apply_saved_layout()

    def _build_hero(self) -> None:
        self.hero_canvas = tk.Canvas(
            self.main,
            height=158,
            bd=0,
            highlightthickness=0,
            background="#101A2E",
        )
        self.hero_canvas.pack(fill="x")
        self.hero_canvas.bind("<Configure>", lambda _event: self._draw_hero())

    def _draw_hero(self) -> None:
        if not self.hero_canvas:
            return
        canvas = self.hero_canvas
        width = max(canvas.winfo_width(), 760)
        height = max(canvas.winfo_height(), 158)
        canvas.delete("all")
        canvas.create_rectangle(0, 0, width, height, fill="#101A2E", outline="#243B61")
        canvas.create_polygon(0, 0, width * 0.58, 0, width * 0.42, height, 0, height, fill="#132238", outline="")
        canvas.create_polygon(width * 0.62, 0, width, 0, width, height, width * 0.82, height, fill="#10293B", outline="")
        for offset, color in [(0, "#2DD4BF"), (34, "#FFD166"), (68, "#60A5FA")]:
            canvas.create_line(width - 320 + offset, 18, width - 80 + offset, height - 22, fill=color, width=2)
        canvas.create_text(
            26,
            30,
            text="Centro de Control Académico",
            anchor="nw",
            fill="#F8FAFC",
            font=("Segoe UI", 25, "bold"),
        )
        canvas.create_text(
            28,
            70,
            text="Admisiones, permanencia, alertas e ingresos en una sola vista operativa",
            anchor="nw",
            fill="#AFC1D8",
            font=("Segoe UI", 10),
        )
        chip_x = 28
        for chip, color in [
            ("ADMITIDOS", "#2563EB"),
            ("RIESGO", "#EF476F"),
            ("INGRESOS", "#2DD4BF"),
            ("EXPORTACION", "#FFD166"),
        ]:
            chip_width = 90 if chip != "EXPORTACION" else 112
            canvas.create_rectangle(chip_x, 108, chip_x + chip_width, 132, fill=color, outline="")
            canvas.create_text(
                chip_x + chip_width / 2,
                120,
                text=chip,
                fill="#06121F" if color in {"#2DD4BF", "#FFD166"} else "#F8FAFC",
                font=("Segoe UI", 8, "bold"),
            )
            chip_x += chip_width + 8
        self._draw_hero_metric(width - 292, 36, "Registros", self.hero_total_text)
        self._draw_hero_metric(width - 146, 36, "Vista actual", self.hero_context_text)

    def _draw_hero_metric(self, x: int, y: int, label: str, value: str) -> None:
        canvas = self.hero_canvas
        if not canvas:
            return
        canvas.create_rectangle(x, y, x + 126, y + 84, fill="#0B1628", outline="#243B61")
        canvas.create_text(x + 12, y + 13, text=label, anchor="nw", fill="#5EEAD4", font=("Segoe UI", 8, "bold"))
        display_value = value if len(value) <= 13 else f"{value[:12]}..."
        canvas.create_text(x + 12, y + 37, text=display_value, anchor="nw", fill="#FFD166", font=("Segoe UI", 17, "bold"))
        canvas.create_line(x + 12, y + 70, x + 112, y + 70, fill="#2563EB", width=3)

    def _make_draggable(self, widget: tk.Widget) -> None:
        handles = widget.drag_handles() if hasattr(widget, "drag_handles") else [widget]
        for child in handles:
            try:
                child.bind("<ButtonPress-1>", self._drag_start, add="+")
                child.bind("<B1-Motion>", self._drag_motion, add="+")
                child.bind("<ButtonRelease-1>", self._drag_release, add="+")
            except Exception:
                continue

    def _walk_widgets(self, widget: tk.Widget) -> list[tk.Widget]:
        widgets = [widget]
        for child in widget.winfo_children():
            widgets.extend(self._walk_widgets(child))
        return widgets

    def _drag_start(self, event) -> None:
        if self._is_interactive_widget(event.widget):
            return
        container = self._drag_container(event.widget)
        if not container:
            return
        self.drag_source = container
        siblings = list(self.drag_source.master.winfo_children())
        self.drag_source_index = siblings.index(self.drag_source)
        self._mark_drag_source(True)
        self._show_drag_preview(event.x_root, event.y_root)
        self.configure(cursor="fleur")

    def _drag_motion(self, event) -> None:
        if not self.drag_source:
            return
        self.configure(cursor="fleur")
        self._move_drag_preview(event.x_root, event.y_root)
        self._show_drop_indicator(event.x_root, event.y_root)

    def _drag_release(self, event) -> None:
        if not self.drag_source:
            return
        parent = self.drag_source.master
        siblings = list(parent.winfo_children())
        new_index = self._drop_index(parent, siblings, event.x_root, event.y_root)
        old_index = siblings.index(self.drag_source)
        if new_index != old_index:
            siblings.insert(new_index, siblings.pop(old_index))
            self._pack_order(parent, siblings)
        self._save_layout()
        self._mark_drag_source(False)
        self._hide_drag_preview()
        self._hide_drop_indicator()
        self.drag_source = None
        self.configure(cursor="")

    def _show_drag_preview(self, x_root: int, y_root: int) -> None:
        title = self._drag_title(self.drag_source)
        width = max(170, min(self.drag_source.winfo_width(), 320))
        height = 54 if self.drag_source.master is self.cards_frame else 72
        self.drag_preview = tk.Toplevel(self)
        self.drag_preview.overrideredirect(True)
        self.drag_preview.attributes("-topmost", True)
        try:
            self.drag_preview.attributes("-alpha", 0.82)
        except tk.TclError:
            pass
        self.drag_preview.configure(background="#5EEAD4")
        frame = tk.Frame(self.drag_preview, background="#132238", highlightbackground="#5EEAD4", highlightthickness=2)
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text="MOVIENDO", background="#2563EB", foreground="#F8FAFC", font=("Segoe UI", 8, "bold")).pack(fill="x")
        self.drag_preview_label = tk.Label(
            frame,
            text=title,
            background="#132238",
            foreground="#F8FAFC",
            font=("Segoe UI", 11, "bold"),
            padx=12,
            pady=10,
        )
        self.drag_preview_label.pack(fill="both", expand=True)
        self.drag_preview.geometry(f"{width}x{height}+{x_root + 18}+{y_root + 18}")

    def _move_drag_preview(self, x_root: int, y_root: int) -> None:
        if self.drag_preview:
            self.drag_preview.geometry(f"+{x_root + 18}+{y_root + 18}")

    def _hide_drag_preview(self) -> None:
        if self.drag_preview:
            self.drag_preview.destroy()
        self.drag_preview = None
        self.drag_preview_label = None

    def _show_drop_indicator(self, x_root: int, y_root: int) -> None:
        parent = self.drag_source.master
        siblings = list(parent.winfo_children())
        index = self._drop_index(parent, siblings, x_root, y_root)
        x, y, width, height = self._indicator_geometry(parent, siblings, index)
        if not self.drop_indicator:
            self.drop_indicator = tk.Toplevel(self)
            self.drop_indicator.overrideredirect(True)
            self.drop_indicator.attributes("-topmost", True)
            try:
                self.drop_indicator.attributes("-alpha", 0.9)
            except tk.TclError:
                pass
            self.drop_indicator.configure(background="#2DD4BF")
        self.drop_indicator.geometry(f"{width}x{height}+{x}+{y}")

    def _hide_drop_indicator(self) -> None:
        if self.drop_indicator:
            self.drop_indicator.destroy()
        self.drop_indicator = None

    def _indicator_geometry(self, parent: tk.Widget, siblings: list[tk.Widget], index: int) -> tuple[int, int, int, int]:
        candidates = [widget for widget in siblings if widget is not self.drag_source]
        if parent is self.cards_frame:
            if not candidates:
                return parent.winfo_rootx(), parent.winfo_rooty(), 6, max(parent.winfo_height(), 80)
            if index >= len(candidates):
                ref = candidates[-1]
                return ref.winfo_rootx() + ref.winfo_width() + 4, ref.winfo_rooty(), 6, ref.winfo_height()
            ref = candidates[index]
            return ref.winfo_rootx() - 8, ref.winfo_rooty(), 6, ref.winfo_height()
        if not candidates:
            return parent.winfo_rootx(), parent.winfo_rooty(), max(parent.winfo_width(), 180), 6
        if index >= len(candidates):
            ref = candidates[-1]
            return ref.winfo_rootx(), ref.winfo_rooty() + ref.winfo_height() + 4, ref.winfo_width(), 6
        ref = candidates[index]
        return ref.winfo_rootx(), ref.winfo_rooty() - 8, ref.winfo_width(), 6

    def _drag_title(self, widget: tk.Widget) -> str:
        if hasattr(widget, "title_label"):
            return widget.title_label.cget("text")
        try:
            return widget.cget("text")
        except tk.TclError:
            return "Panel"

    def _mark_drag_source(self, active: bool) -> None:
        if isinstance(self.drag_source, CardWidget):
            self.drag_source.configure(style="DraggingCard.TFrame" if active else "Card.TFrame")
        elif isinstance(self.drag_source, ChartWidget):
            self.drag_source.configure(style="Dragging.TLabelframe" if active else "TLabelframe")

    def _drop_index(self, parent: tk.Widget, siblings: list[tk.Widget], x_root: int, y_root: int) -> int:
        candidates = [widget for widget in siblings if widget is not self.drag_source]
        if not candidates:
            return 0
        if parent is self.cards_frame:
            centers = [widget.winfo_rootx() + widget.winfo_width() / 2 for widget in candidates]
            for index, center in enumerate(centers):
                if x_root < center:
                    return index
            return len(candidates)
        parent.update_idletasks()
        relative_x = max(0, min(x_root - parent.winfo_rootx(), parent.winfo_width()))
        relative_y = max(0, min(y_root - parent.winfo_rooty(), parent.winfo_height()))
        column = 0 if relative_x < parent.winfo_width() / 2 else 1
        row = 0 if relative_y < parent.winfo_height() / 2 else 1
        destination = row * 2 + column
        return max(0, min(destination, len(candidates)))

    def _drag_container(self, widget: tk.Widget) -> tk.Widget | None:
        current = widget
        while current:
            if current.master in {self.cards_frame, self.charts_frame}:
                return current
            current = current.master
        return None

    def _is_interactive_widget(self, widget: tk.Widget) -> bool:
        return widget.winfo_class() in {"TButton", "TEntry", "TCombobox", "Treeview"}

    def _pack_order(self, parent: tk.Widget, widgets: list[tk.Widget]) -> None:
        for widget in widgets:
            widget.pack_forget()
            widget.grid_forget()
        if parent is self.cards_frame:
            for widget in widgets:
                widget.pack(side="left", fill="x", expand=True, padx=6)
        else:
            for index, widget in enumerate(widgets):
                widget.grid(row=index // 2, column=index % 2, sticky="nsew", padx=7, pady=7)
            parent.columnconfigure(0, weight=1)
            parent.columnconfigure(1, weight=1)
            parent.rowconfigure(0, weight=1)
            parent.rowconfigure(1, weight=1)

    def _apply_saved_layout(self) -> None:
        card_order = list(self.card_widgets.values())
        chart_order = self.chart_widgets
        if self.layout_path.exists():
            try:
                layout = json.loads(self.layout_path.read_text(encoding="utf-8"))
                card_lookup = {card.title_label.cget("text"): card for card in card_order}
                chart_lookup = {chart.cget("text"): chart for chart in chart_order}
                saved_cards = [card_lookup[name] for name in layout.get("cards", []) if name in card_lookup]
                saved_charts = [chart_lookup[name] for name in layout.get("charts", []) if name in chart_lookup]
                card_order = saved_cards + [card for card in card_order if card not in saved_cards]
                chart_order = saved_charts + [chart for chart in chart_order if chart not in saved_charts]
            except (OSError, json.JSONDecodeError):
                pass
        self._pack_order(self.cards_frame, card_order)
        self._pack_order(self.charts_frame, chart_order)

    def _save_layout(self) -> None:
        self.layout_path.parent.mkdir(parents=True, exist_ok=True)
        layout = {
            "cards": [card.title_label.cget("text") for card in self.cards_frame.winfo_children()],
            "charts": [chart.cget("text") for chart in self.charts_frame.winfo_children()],
        }
        self.layout_path.write_text(json.dumps(layout, indent=2), encoding="utf-8")

    def current_filters(self) -> DashboardFilters:
        return DashboardFilters(
            program=self.sidebar.program_var.get(),
            semester=self.sidebar.semester_var.get(),
            name=self.toolbar.search_var.get(),
            conditions=self.sidebar.selected_conditions(),
            gender=self.sidebar.gender_var.get(),
            state=self.sidebar.state_var.get(),
        )

    def refresh(self) -> None:
        filters = self.current_filters()
        self.filtered_df = self.processor.filter(filters)
        kpis = self.processor.kpis(self.filtered_df)
        charts = self.processor.charts(self.filtered_df, focus_semester=filters.semester)
        self.hero_total_text = str(len(self.filtered_df))
        context = self.sidebar.program_var.get()
        semester = self.sidebar.semester_var.get()
        self.hero_context_text = context if semester == "Todos" else semester
        self._draw_hero()
        for title, value in kpis.items():
            self.card_widgets[title].set_value(value)
        self.chart_widgets[0].render(charts["line"])
        self.chart_widgets[1].render(charts["pie"])
        self.chart_widgets[2].render(charts["bar"])
        self.chart_widgets[3].render(charts["three_d"])
        self.table.update_data(self.filtered_df)

    def export_png(self) -> None:
        path = self.exporter.export_png(self.processor.charts(self.filtered_df, focus_semester=self.sidebar.semester_var.get()))
        messagebox.showinfo("Exportación completa", f"PNG generado:\n{path}")

    def export_pdf(self) -> None:
        path = self.exporter.export_pdf(self.filtered_df, self.processor.kpis(self.filtered_df))
        messagebox.showinfo("Exportación completa", f"PDF generado:\n{path}")

    def show_enrollment_breakdown(self, chart_data: dict, index: int) -> None:
        semester = chart_data["labels"][index]
        counts = chart_data.get("by_program", {}).get(semester, {})
        total = chart_data["values"][index]
        detail = "\n".join(f"{program}: {counts.get(program, 0)}" for program in counts)
        messagebox.showinfo(
            f"Inscripciones en {semester}",
            f"Total inscripciones: {total}\n\n{detail}",
        )

    def open_dataset_window(self) -> None:
        window = tk.Toplevel(self)
        window.title("Dataset estudiantes universitarios")
        window.geometry("1180x560")
        window.configure(background="#08111F")
        header = ttk.Frame(window, padding=(14, 12), style="Toolbar.TFrame")
        header.pack(fill="x")
        ttk.Label(header, text="Dataset estudiantes universitarios", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text=f"{len(self.dataframe)} registros", style="Hint.TLabel").pack(side="right")
        table = TableWidget(window, columns=list(self.dataframe.columns))
        table.pack(fill="both", expand=True, padx=14, pady=14)
        table.update_data(self.dataframe)
