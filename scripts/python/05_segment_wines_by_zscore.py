from pathlib import Path

import duckdb
import pandas as pd


WORKING_DIR = Path("data/output/working")
DUCKDB_PATH = WORKING_DIR / "bottleneck.duckdb"

EXPECTED_PREMIUM_COUNT = 30
ZSCORE_THRESHOLD = 2.0


def compute_zscore(series: pd.Series) -> pd.Series:
    mean_price = series.mean()
    std_price = series.std(ddof=0)

    if std_price == 0:
        raise ValueError("Impossible de calculer le z-score : écart-type nul.")

    return (series - mean_price) / std_price


def main() -> None:
    if not DUCKDB_PATH.exists():
        raise FileNotFoundError(
            f"Base DuckDB introuvable : {DUCKDB_PATH}. "
            "Exécutez d'abord les scripts précédents."
        )

    with duckdb.connect(DUCKDB_PATH) as connection:
        df = connection.execute(
            """
            SELECT
                product_id,
                sku,
                post_title,
                price,
                total_sales,
                stock_quantity,
                stock_status
            FROM products_merged
            """
        ).fetchdf()

        if df.empty:
            raise ValueError("La table products_merged est vide.")

        df["price_zscore"] = compute_zscore(df["price"])
        df["is_premium"] = df["price_zscore"] > ZSCORE_THRESHOLD

        premium_df = df[df["is_premium"]].copy()
        ordinary_df = df[~df["is_premium"]].copy()

        premium_count = len(premium_df)

        if premium_count != EXPECTED_PREMIUM_COUNT:
            raise ValueError(
                f"Contrôle échoué pour les vins premium : "
                f"{premium_count} lignes trouvées, "
                f"{EXPECTED_PREMIUM_COUNT} attendues."
            )

        connection.register("tmp_premium_wines", premium_df)
        connection.register("tmp_ordinary_wines", ordinary_df)

        connection.execute(
            """
            CREATE OR REPLACE TABLE premium_wines AS
            SELECT * FROM tmp_premium_wines
            """
        )

        connection.execute(
            """
            CREATE OR REPLACE TABLE ordinary_wines AS
            SELECT * FROM tmp_ordinary_wines
            """
        )

        connection.unregister("tmp_premium_wines")
        connection.unregister("tmp_ordinary_wines")

        print(f"[OK] premium_wines: {len(premium_df)} lignes")
        print(f"[OK] ordinary_wines: {len(ordinary_df)} lignes")

        preview = connection.execute(
            """
            SELECT
                product_id,
                sku,
                post_title,
                price,
                ROUND(price_zscore, 2) AS price_zscore
            FROM premium_wines
            ORDER BY price DESC
            LIMIT 10
            """
        ).fetchdf()

        print("\nTop 10 des vins premium par prix :")
        print(preview)

    print("\nSegmentation des vins terminée avec succès.")


if __name__ == "__main__":
    main()
