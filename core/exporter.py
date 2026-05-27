"""PNG and PDF report export utilities."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class Exporter:
    """Generate static reports from the filtered dashboard data."""

    def __init__(self, reports_dir: Path) -> None:
        self.reports_dir = reports_dir
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def export_png(self, charts: dict[str, dict]) -> Path:
        """Export a compact PNG summary using matplotlib."""
        path = self.reports_dir / f"reporte_{datetime.now():%Y%m%d_%H%M%S}.png"
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        line = charts["line"]
        axes[0].plot(line["labels"], line["values"], marker="o", color="#2E6DA4")
        axes[0].set_title(line["title"])
        axes[0].tick_params(axis="x", rotation=45)
        pie = charts["pie"]
        axes[1].pie(pie["values"], labels=pie["labels"], autopct="%1.0f%%")
        axes[1].set_title(pie["title"])
        bar = charts["bar"]
        axes[2].bar(bar["labels"], bar["datasets"][0]["values"], label="Deserciones", color="#D9480F")
        axes[2].bar(bar["labels"], bar["datasets"][1]["values"], bottom=bar["datasets"][0]["values"], label="Bajo rendimiento", color="#F4A261")
        axes[2].set_title(bar["title"])
        axes[2].tick_params(axis="x", rotation=30)
        axes[2].legend()
        fig.tight_layout()
        fig.savefig(path, dpi=160)
        plt.close(fig)
        return path

    def export_pdf(self, df: pd.DataFrame, kpis: dict[str, str]) -> Path:
        """Export a PDF report with KPIs and a preview table."""
        path = self.reports_dir / f"reporte_{datetime.now():%Y%m%d_%H%M%S}.pdf"
        doc = SimpleDocTemplate(str(path), pagesize=landscape(letter), leftMargin=24, rightMargin=24, topMargin=24, bottomMargin=24)
        styles = getSampleStyleSheet()
        story = [Paragraph("Dashboard Estudiantil Universitario", styles["Title"]), Spacer(1, 12)]
        kpi_rows = [["Indicador", "Valor"], *[[key, value] for key, value in kpis.items()]]
        story.append(_styled_table(kpi_rows))
        story.append(Spacer(1, 16))
        columns = ["id_estudiante", "nombre", "genero", "programa", "semestre_ingreso", "estado"]
        preview = df[columns].head(35).fillna("").astype(str).values.tolist()
        story.append(Paragraph("Tabla de estudiantes filtrados", styles["Heading2"]))
        story.append(_styled_table([columns, *preview], font_size=7))
        doc.build(story)
        return path


def _styled_table(rows: list[list[str]], font_size: int = 9) -> Table:
    table = Table(rows, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E6DA4")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E2E8F0")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), font_size),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F7FA")]),
            ]
        )
    )
    return table
