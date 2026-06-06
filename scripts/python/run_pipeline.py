import subprocess
from pathlib import Path


SCRIPTS = [
    "scripts/python/01_inspect_sources.py",
    "scripts/python/02_load_staging_duckdb.py",
    "scripts/python/03_clean_sources_duckdb.py",
    "scripts/python/04_merge_and_compute_revenue.py",
    "scripts/python/05_segment_wines_by_zscore.py",
    "scripts/python/06_export_deliverables.py",
]


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
    for script in SCRIPTS:
        run_script(script)

    print("\nPipeline local exécuté avec succès.")


if __name__ == "__main__":
    main()
