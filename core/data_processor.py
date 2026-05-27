"""Filtering, aggregations and chart-ready statistics."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from core.data_loader import GENDERS, PROGRAMS, SEMESTERS, STATES


@dataclass
class DashboardFilters:
    """Current user-selected filters."""

    program: str = "Todos"
    semester: str = "Todos"
    name: str = ""
    conditions: set[str] = field(default_factory=set)
    gender: str = "Todos"
    state: str = "Todos"


class DataProcessor:
    """Provide filtered data and computed dashboard summaries."""

    def __init__(self, dataframe: pd.DataFrame) -> None:
        self.dataframe = dataframe.copy()

    def filter(self, filters: DashboardFilters) -> pd.DataFrame:
        """Return a dataframe filtered by the controls in the dashboard."""
        df = self.dataframe.copy()
        if filters.program != "Todos":
            df = df[df["programa"] == filters.program]
        if filters.semester != "Todos":
            df = df[
                (df["semestre_ingreso"] == filters.semester)
                | (df["semestre_actual"] == filters.semester)
            ]
        if filters.name.strip():
            query = filters.name.strip().lower()
            df = df[df["nombre"].str.lower().str.contains(query, na=False)]
        if filters.gender != "Todos":
            df = df[df["genero"] == filters.gender]
        if filters.state != "Todos":
            df = df[df["estado"] == filters.state]
        condition_columns = {
            "Aplazamiento": "aplazamiento",
            "Deserción voluntaria": "desercion_voluntaria",
            "Bajo rendimiento": "bajo_rendimiento",
        }
        for condition in filters.conditions:
            column = condition_columns.get(condition)
            if column:
                df = df[df[column]]
        return df

    def kpis(self, df: pd.DataFrame) -> dict[str, str]:
        """Build KPI values for the top cards."""
        total = len(df)
        ratio = lambda column: f"{(df[column].mean() * 100):.1f}%" if total else "0.0%"
        gender_counts = df["genero"].value_counts().to_dict() if total else {}
        gender_text = " / ".join(f"{gender}: {gender_counts.get(gender, 0)}" for gender in GENDERS)
        return {
            "Total estudiantes": str(total),
            "Aplazamientos": ratio("aplazamiento"),
            "Deserciones voluntarias": ratio("desercion_voluntaria"),
            "Bajo rendimiento": ratio("bajo_rendimiento"),
            "Género": gender_text,
        }

    def charts(self, df: pd.DataFrame, focus_semester: str = "Todos") -> dict[str, dict]:
        """Return chart-ready data dictionaries for all visualizations."""
        line_semesters = [focus_semester] if focus_semester != "Todos" else SEMESTERS
        return {
            "line": {
                "title": "Evolución de inscripciones",
                "labels": line_semesters,
                "values": [int((df["semestre_ingreso"] == semester).sum()) for semester in line_semesters],
                "by_program": {
                    semester: {
                        program: int(((df["semestre_ingreso"] == semester) & (df["programa"] == program)).sum())
                        for program in PROGRAMS
                    }
                    for semester in line_semesters
                },
            },
            "pie": {
                "title": "Distribución por estado",
                "labels": STATES,
                "values": [int((df["estado"] == state).sum()) for state in STATES],
            },
            "bar": {
                "title": "Deserción y bajo rendimiento por programa",
                "labels": PROGRAMS,
                "datasets": [
                    {
                        "label": "Deserciones",
                        "values": [int(((df["programa"] == program) & df["desercion_voluntaria"]).sum()) for program in PROGRAMS],
                    },
                    {
                        "label": "Bajo rendimiento",
                        "values": [int(((df["programa"] == program) & df["bajo_rendimiento"]).sum()) for program in PROGRAMS],
                    },
                ],
            },
            "gender": {
                "title": "Género por carrera",
                "labels": PROGRAMS,
                "datasets": [
                    {
                        "label": gender,
                        "values": [int(((df["programa"] == program) & (df["genero"] == gender)).sum()) for program in PROGRAMS],
                    }
                    for gender in GENDERS
                ],
            },
            "three_d": self.entry_points(df),
        }

    def entry_points(self, df: pd.DataFrame) -> dict:
        """Return points for semester-program-count 3D scatter."""
        points = []
        for semester_index, semester in enumerate(SEMESTERS):
            for program_index, program in enumerate(PROGRAMS):
                count = int(((df["semestre_ingreso"] == semester) & (df["programa"] == program)).sum())
                points.append(
                    {
                        "semester": semester,
                        "program": program,
                        "x": semester_index,
                        "y": program_index,
                        "z": count,
                    }
                )
        return {"title": "Análisis 3D de ingresos", "points": points, "semesters": SEMESTERS, "programs": PROGRAMS}
