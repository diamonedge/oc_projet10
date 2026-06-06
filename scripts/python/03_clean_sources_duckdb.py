from pathlib import Path

import duckdb


WORKING_DIR = Path("data/output/working")
DUCKDB_PATH = WORKING_DIR / "bottleneck.duckdb"
SQL_PATH = Path("scripts/sql/01_clean_sources.sql")


EXPECTED_COUNTS = {
    "erp_clean": 825,
    "liaison_clean": 825,
    "web_without_missing_sku": 1428,
    "web_clean": 714,
}


def assert_row_count(
    connection: duckdb.DuckDBPyConnection,
    table_name: str,
    expected_count: int,
) -> None:
    actual_count = connection.execute(
        f"SELECT COUNT(*) FROM {table_name}"
    ).fetchone()[0]

    if actual_count != expected_count:
        raise ValueError(
            f"Contrôle échoué pour {table_name}: "
            f"{actual_count} lignes trouvées, {expected_count} attendues."
        )

    print(f"[OK] {table_name}: {actual_count} lignes")


def main() -> None:
    if not DUCKDB_PATH.exists():
        raise FileNotFoundError(
            f"Base DuckDB introuvable : {DUCKDB_PATH}. "
            "Exécutez d'abord scripts/python/02_load_staging_duckdb.py."
        )

    if not SQL_PATH.exists():
        raise FileNotFoundError(f"Script SQL introuvable : {SQL_PATH}")

    sql = SQL_PATH.read_text(encoding="utf-8")

    with duckdb.connect(DUCKDB_PATH) as connection:
        connection.execute(sql)

        for table_name, expected_count in EXPECTED_COUNTS.items():
            assert_row_count(connection, table_name, expected_count)

        tables = connection.execute("SHOW TABLES").fetchdf()
        print("\nTables disponibles dans DuckDB :")
        print(tables)

    print("\nNettoyage terminé avec succès.")


if __name__ == "__main__":
    main()
