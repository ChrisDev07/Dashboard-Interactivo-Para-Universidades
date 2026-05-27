"""Excel loading, validation and deterministic sample dataset generation."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import random

import pandas as pd


PROGRAMS = [
    "Ingeniería de Sistemas",
    "Ingeniería Civil",
    "Arquitectura",
    "Derecho",
    "MVZ - Medicina Veterinaria y Zootecnia",
    "Ingeniería Industrial",
]
SEMESTERS = [
    "2022-A",
    "2022-B",
    "2023-A",
    "2023-B",
    "2024-A",
    "2024-B",
    "2025-A",
    "2025-B",
]
GENDERS = ["M", "F", "Otro"]
STATES = ["Activo", "Aplazado", "Deserción", "Graduado"]
DEFAULT_DATASET_ROWS = 2000

REQUIRED_COLUMNS = [
    "id_estudiante",
    "nombre",
    "genero",
    "programa",
    "fecha_inscripcion",
    "semestre_ingreso",
    "aplazamiento",
    "semestre_aplazamiento",
    "desercion_voluntaria",
    "fecha_desercion",
    "bajo_rendimiento",
    "semestre_actual",
    "estado",
]


def ensure_dataset(path: Path, rows: int = DEFAULT_DATASET_ROWS) -> None:
    """Create a deterministic Excel dataset if it does not exist."""
    if path.exists() and path.stat().st_size > 0:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    dataframe = generate_sample_students(rows)
    dataframe.to_excel(path, index=False, engine="openpyxl")


def load_students(path: Path) -> pd.DataFrame:
    """Load and validate the student Excel dataset."""
    if not path.exists():
        raise FileNotFoundError(f"No existe el dataset: {path}")
    dataframe = pd.read_excel(path, engine="openpyxl")
    dataframe = dataframe.rename(
        columns={
            "baja_voluntaria": "desercion_voluntaria",
            "fecha_baja": "fecha_desercion",
        }
    )
    missing = [column for column in REQUIRED_COLUMNS if column not in dataframe.columns]
    if missing:
        raise ValueError(f"Columnas faltantes en el dataset: {', '.join(missing)}")

    dataframe = dataframe[REQUIRED_COLUMNS].copy()
    dataframe["fecha_inscripcion"] = pd.to_datetime(dataframe["fecha_inscripcion"], errors="coerce")
    dataframe["fecha_desercion"] = pd.to_datetime(dataframe["fecha_desercion"], errors="coerce")
    for column in ["aplazamiento", "desercion_voluntaria", "bajo_rendimiento"]:
        dataframe[column] = dataframe[column].fillna(False).astype(bool)
    dataframe["semestre_aplazamiento"] = dataframe["semestre_aplazamiento"].fillna("")
    return dataframe


def generate_sample_students(rows: int = 720) -> pd.DataFrame:
    """Generate a mixed synthetic dataset for six programs and eight semesters."""
    random.seed()
    first_names = [
        "Laura", "Carlos", "Valentina", "Andres", "Sofia", "Daniel", "Camila", "Miguel",
        "Paula", "Juan", "Mariana", "Sebastian", "Natalia", "Diego", "Isabella", "Felipe",
        "Alejandra", "Samuel", "Gabriela", "Mateo", "Luciana", "Santiago", "Manuela", "Tomas",
        "Carolina", "Esteban", "Juliana", "Nicolas", "Danna", "Kevin", "Salome", "Jeronimo",
    ]
    last_names = [
        "Martinez", "Gomez", "Ruiz", "Torres", "Rojas", "Diaz", "Moreno", "Castro",
        "Vargas", "Pineda", "Ramirez", "Suarez", "Ortiz", "Navarro", "Cortes", "Mendez",
        "Acosta", "Barrera", "Cabrera", "Duarte", "Escobar", "Fuentes", "Guerrero", "Herrera",
        "Lara", "Medina", "Ospina", "Quintero", "Reyes", "Salazar", "Valencia", "Zamora",
    ]
    semester_weights = [9, 10, 12, 11, 14, 13, 16, 15]
    program_weights = {
        "Ingeniería de Sistemas": 18,
        "Ingeniería Civil": 15,
        "Arquitectura": 13,
        "Derecho": 17,
        "MVZ - Medicina Veterinaria y Zootecnia": 16,
        "Ingeniería Industrial": 21,
    }
    records = []
    for student_id in range(1, rows + 1):
        program = random.choices(PROGRAMS, weights=[program_weights[item] for item in PROGRAMS], k=1)[0]
        semester_in = random.choices(SEMESTERS, weights=semester_weights, k=1)[0]
        semester_index = SEMESTERS.index(semester_in)
        current_semester = random.choice(SEMESTERS[semester_index:])
        gender = random.choices(GENDERS, weights=[46, 50, 4], k=1)[0]
        status_weights = [70, 11, 8, 11] if semester_index < 5 else [82, 9, 7, 2]
        status = random.choices(STATES, weights=status_weights, k=1)[0]
        postponed = status == "Aplazado" or random.random() < random.uniform(0.08, 0.20)
        dropout = status == "Deserción"
        low_performance = random.random() < (random.uniform(0.20, 0.34) if postponed or dropout else random.uniform(0.08, 0.18))
        year, half = semester_in.split("-")
        month = 2 if half == "A" else 7
        signup_date = date(int(year), month, random.randint(1, 24))
        postponement_semester = random.choice(SEMESTERS[semester_index:]) if postponed else ""
        dropout_date = date(int(current_semester[:4]), 11, random.randint(1, 25)) if dropout else pd.NaT
        records.append(
            {
                "id_estudiante": student_id,
                "nombre": f"{random.choice(first_names)} {random.choice(last_names)}",
                "genero": gender,
                "programa": program,
                "fecha_inscripcion": signup_date,
                "semestre_ingreso": semester_in,
                "aplazamiento": postponed,
                "semestre_aplazamiento": postponement_semester,
                "desercion_voluntaria": dropout,
                "fecha_desercion": dropout_date,
                "bajo_rendimiento": low_performance,
                "semestre_actual": current_semester,
                "estado": status,
            }
        )
    return pd.DataFrame.from_records(records)
