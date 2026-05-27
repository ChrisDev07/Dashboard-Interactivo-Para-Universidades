"""Entry point for the university student dashboard."""

import os
from pathlib import Path

from core.data_loader import ensure_dataset, load_students


BASE_DIR = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(BASE_DIR / "reports" / ".matplotlib"))


def main() -> None:
    """Create the sample dataset when needed and launch the Tkinter app."""
    from ui.main_window import DashboardApp

    dataset_path = BASE_DIR / "data" / "estudiantes_universitarios.xlsx"
    ensure_dataset(dataset_path)
    dataframe = load_students(dataset_path)
    app = DashboardApp(dataframe=dataframe, base_dir=BASE_DIR)
    app.mainloop()


if __name__ == "__main__":
    main()
