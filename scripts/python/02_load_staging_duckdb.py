from pathlib import Path
import warnings

import duckdb
import pandas as pd


warnings.filterwarnings(
    "ignore",
    message="Unknown extension is not supported and will be removed",
)

INPUT_DIR = Path("data/input")
WORKING_DIR = Path("data/output/working")
DUCKDB_PATH = WORKING_DIR / "bottleneck.duckdb"

FILES = {
    "erp": INPUT_DIR / "Fichier_erp.xlsx",
    "web": INPUT_DIR / "Fichier_web.xlsx",
    "liaison": INPUT_DIR / "fichier_liaison.xlsx",
}

EXPECTED_RAW_COUNTS = {
    "raw_erp": 825,
    "raw_web": 1513,
    "raw_liaison": 825,
}


def read_excel_file(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Fichier manquant : {path}")

    return pd.read_excel(path)


def load_dataframe_to_duckdb(
    connection: duckdb.DuckDBPyConnection,
    table_name: str,
    dataframe: pd.DataFrame,
) -> None:
    temp_view_name = f"tmp_{table_name}"

    connection.register(temp_view_name, dataframe)
    connection.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM {temp_view_name}")
    connection.unregister(temp_view_name)


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
    WORKING_DIR.mkdir(parents=True, exist_ok=True)

    df_erp = read_excel_file(FILES["erp"])
    df_web = read_excel_file(FILES["web"])
    df_liaison = read_excel_file(FILES["liaison"])

    with duckdb.connect(DUCKDB_PATH) as connection:
        load_dataframe_to_duckdb(connection, "raw_erp", df_erp)
        load_dataframe_to_duckdb(connection, "raw_web", df_web)
        load_dataframe_to_duckdb(connection, "raw_liaison", df_liaison)

        for table_name, expected_count in EXPECTED_RAW_COUNTS.items():
            assert_row_count(connection, table_name, expected_count)

        tables = connection.execute("SHOW TABLES").fetchdf()
        print("\nTables créées dans DuckDB :")
        print(tables)

    print(f"\nBase DuckDB créée : {DUCKDB_PATH}")


if __name__ == "__main__":
    main()
