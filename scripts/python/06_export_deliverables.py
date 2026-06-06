from pathlib import Path

import duckdb
import pandas as pd
import csv

WORKING_DIR = Path("data/output/working")
LATEST_DIR = Path("data/output/latest")
DUCKDB_PATH = WORKING_DIR / "bottleneck.duckdb"

REVENUE_REPORT_PATH = LATEST_DIR / "bottleneck_revenue_report.xlsx"
PREMIUM_WINES_PATH = LATEST_DIR / "premium_wines.csv"
ORDINARY_WINES_PATH = LATEST_DIR / "ordinary_wines.csv"

EXPECTED_TOTAL_REVENUE = 70568.60
EXPECTED_PREMIUM_COUNT = 30
EXPECTED_ORDINARY_COUNT = 684


def assert_table_exists(connection: duckdb.DuckDBPyConnection, table_name: str) -> None:
    tables = connection.execute("SHOW TABLES").fetchdf()["name"].tolist()

    if table_name not in tables:
        raise ValueError(
            f"Table manquante dans DuckDB : {table_name}. "
            "Exécutez d'abord les scripts précédents."
        )


def assert_count(dataframe: pd.DataFrame, expected_count: int, label: str) -> None:
    actual_count = len(dataframe)

    if actual_count != expected_count:
        raise ValueError(
            f"Contrôle échoué pour {label}: "
            f"{actual_count} lignes trouvées, {expected_count} attendues."
        )

    print(f"[OK] {label}: {actual_count} lignes")


def assert_total_revenue(total_revenue: float) -> None:
    total_revenue = round(float(total_revenue), 2)

    if total_revenue != EXPECTED_TOTAL_REVENUE:
        raise ValueError(
            f"Contrôle échoué pour le chiffre d'affaires total: "
            f"{total_revenue} trouvé, {EXPECTED_TOTAL_REVENUE} attendu."
        )

    print(f"[OK] Chiffre d'affaires total: {total_revenue:.2f} €")


def main() -> None:
    if not DUCKDB_PATH.exists():
        raise FileNotFoundError(
            f"Base DuckDB introuvable : {DUCKDB_PATH}. "
            "Exécutez d'abord les scripts précédents."
        )

    LATEST_DIR.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(DUCKDB_PATH) as connection:
        for table_name in [
            "revenue_by_product",
            "total_revenue",
            "premium_wines",
            "ordinary_wines",
        ]:
            assert_table_exists(connection, table_name)

        revenue_df = connection.execute(
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
            """
        ).fetchdf()

        total_revenue = connection.execute(
            """
            SELECT total_revenue
            FROM total_revenue
            """
        ).fetchone()[0]

        premium_df = connection.execute(
            """
            SELECT
                product_id,
                sku,
                post_title,
                price,
                total_sales,
                stock_quantity,
                stock_status,
                price_zscore,
                is_premium
            FROM premium_wines
            ORDER BY price DESC
            """
        ).fetchdf()

        ordinary_df = connection.execute(
            """
            SELECT
                product_id,
                sku,
                post_title,
                price,
                total_sales,
                stock_quantity,
                stock_status,
                price_zscore,
                is_premium
            FROM ordinary_wines
            ORDER BY price DESC
            """
        ).fetchdf()

    assert_count(revenue_df, 714, "revenue_by_product")
    assert_count(premium_df, EXPECTED_PREMIUM_COUNT, "premium_wines")
    assert_count(ordinary_df, EXPECTED_ORDINARY_COUNT, "ordinary_wines")
    assert_total_revenue(total_revenue)

    summary_df = pd.DataFrame(
        [
            {
                "indicator": "total_revenue",
                "value": round(float(total_revenue), 2),
            },
            {
                "indicator": "products_count",
                "value": len(revenue_df),
            },
            {
                "indicator": "premium_wines_count",
                "value": len(premium_df),
            },
            {
                "indicator": "ordinary_wines_count",
                "value": len(ordinary_df),
            },
        ]
    )

    with pd.ExcelWriter(REVENUE_REPORT_PATH, engine="xlsxwriter") as writer:
        summary_df.to_excel(writer, sheet_name="summary", index=False)
        revenue_df.to_excel(writer, sheet_name="revenue_by_product", index=False)

    premium_df.to_csv(PREMIUM_WINES_PATH, index=False, encoding="utf-8",sep=";",quoting=csv.QUOTE_NONNUMERIC)
    ordinary_df.to_csv(ORDINARY_WINES_PATH, index=False, encoding="utf-8",sep=";",quoting=csv.QUOTE_NONNUMERIC)

    print(f"[OK] Rapport CA exporté : {REVENUE_REPORT_PATH}")
    print(f"[OK] Vins premium exportés : {PREMIUM_WINES_PATH}")
    print(f"[OK] Vins ordinaires exportés : {ORDINARY_WINES_PATH}")

    print("\nExports terminés avec succès.")


if __name__ == "__main__":
    main()
