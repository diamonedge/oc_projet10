from pathlib import Path
import pandas as pd

INPUT_DIR = Path("data/input")

files = {
    "erp": INPUT_DIR / "Fichier_erp.xlsx",
    "web": INPUT_DIR / "Fichier_web.xlsx",
    "liaison": INPUT_DIR / "fichier_liaison.xlsx",
}

for name, path in files.items():
    print(f"\n=== {name.upper()} ===")
    print(f"Fichier : {path}")

    if not path.exists():
        raise FileNotFoundError(f"Fichier manquant : {path}")

    df = pd.read_excel(path)
    print(f"Lignes : {len(df)}")
    print(f"Colonnes : {list(df.columns)}")
    print("Valeurs manquantes par colonne :")
    print(df.isna().sum())
