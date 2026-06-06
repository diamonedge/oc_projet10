from pathlib import Path

import duckdb


WORKING_DIR = Path("data/output/working")
DUCKDB_PATH = WORKING_DIR / "bottleneck.duckdb"
SQL_PATH = Path("scripts/sql/02_merge_and_revenue.sql")

EXPECTED_PRODUCTS_MERGED_COUNT = 714
EXPECTED_TOTAL_REVENUE = 70568.60


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


def assert_no_duplicates(
    connection: duckdb.DuckDBPyConnection,
    table_name: str,
    column_name: str,
) -> None:
    total_count, distinct_count = connection.execute(
        f"""
        SELECT
            COUNT(*) AS total_count,
            COUNT(DISTINCT {column_name}) AS distinct_count
        FROM {table_name}
        """
    ).fetchone()

    if total_count != distinct_count:
        raise ValueError(
            f"Contrôle échoué pour {table_name}.{column_name}: "
            f"{total_count - distinct_count} doublon(s) détecté(s)."
        )

    print(f"[OK] {table_name}.{column_name}: aucun doublon")


def assert_total_revenue(
    connection: duckdb.DuckDBPyConnection,
    expected_total: float,
) -> None:
    actual_total = connection.execute(
        "SELECT total_revenue FROM total_revenue"
    ).fetchone()[0]

    actual_total = round(float(actual_total), 2)

    if actual_total != expected_total:
        raise ValueError(
            f"Contrôle échoué pour le chiffre d'affaires total: "
            f"{actual_total} trouvé, {expected_total} attendu."
        )

    print(f"[OK] Chiffre d'affaires total: {actual_total:.2f} €")


def main() -> None:
    if not DUCKDB_PATH.exists():
        raise FileNotFoundError(
            f"Base DuckDB introuvable : {DUCKDB_PATH}. "
            "Exécutez d'abord les scripts précédents."
        )

    if not SQL_PATH.exists():
        raise FileNotFoundError(f"Script SQL introuvable : {SQL_PATH}")

    sql = SQL_PATH.read_text(encoding="utf-8")

    with duckdb.connect(DUCKDB_PATH) as connection:
        connection.execute(sql)

        assert_row_count(
            connection,
            "products_merged",
            EXPECTED_PRODUCTS_MERGED_COUNT,
        )
        assert_row_count(
            connection,
            "revenue_by_product",
            EXPECTED_PRODUCTS_MERGED_COUNT,
        )
        assert_no_duplicates(connection, "products_merged", "product_id")
        assert_no_duplicates(connection, "products_merged", "sku")
        assert_total_revenue(connection, EXPECTED_TOTAL_REVENUE)

        preview = connection.execute(
            """
            SELECT
                product_id,
                sku,
                post_title,
                price,
                total_sales,
                revenue
            FROM revenue_by_product
            ORDER BY revenue DESC
            LIMIT 10
            """
        ).fetchdf()

        print("\nTop 10 des produits par chiffre d'affaires :")
        print(preview)

    print("\nFusion et calcul du chiffre d'affaires terminés avec succès.")


if __name__ == "__main__":
    main()
