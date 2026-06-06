import subprocess
from pathlib import Path


DUCKDB_PATH = Path("data/output/working/bottleneck.duckdb")

GENERATED_FILES = [
    DUCKDB_PATH,
    Path("data/output/latest/bottleneck_revenue_report.xlsx"),
    Path("data/output/latest/premium_wines.csv"),
    Path("data/output/latest/ordinary_wines.csv"),
]

SCRIPTS = [
    "scripts/python/01_inspect_sources.py",
    "scripts/python/02_load_staging_duckdb.py",
    "scripts/python/03_clean_sources_duckdb.py",
    "scripts/python/04_merge_and_compute_revenue.py",
    "scripts/python/05_segment_wines_by_zscore.py",
    "scripts/python/06_export_deliverables.py",
]


def clean_generated_files() -> None:
    print("=== Nettoyage des fichiers générés ===")

    for path in GENERATED_FILES:
        if path.exists():
            path.unlink()
            print(f"[OK] Supprimé : {path}")
        else:
            print(f"[INFO] Absent : {path}")


def run_script(script_path: str) -> None:
    path = Path(script_path)

    if not path.exists():
        raise FileNotFoundError(f"Script introuvable : {script_path}")

    print(f"\n=== Exécution : {script_path} ===")

    subprocess.run(
        ["uv", "run", "python", script_path],
        check=True,
    )


def main() -> None:
    clean_generated_files()

    for script in SCRIPTS:
        run_script(script)

    print("\nPipeline local exécuté avec succès depuis un état propre.")


if __name__ == "__main__":
    main()
