from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
STRUCTURED_DIR = BASE_DIR / "data" / "structured"


def find_csv_files() -> list[Path]:
    if not RAW_DIR.exists():
        raise FileNotFoundError(f"dossier introuvable: {RAW_DIR}")

    csv_files = sorted(RAW_DIR.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"aucun fichier csv trouve dans: {RAW_DIR}")

    return csv_files


def convert_csv_to_parquet(csv_path: Path) -> Path:
    dataframe = pd.read_csv(csv_path)
    parquet_path = STRUCTURED_DIR / f"{csv_path.stem}.parquet"
    dataframe.to_parquet(parquet_path, index=False)

    print(f"{csv_path.name} -> {parquet_path}")
    print(f"  lignes: {len(dataframe)}")
    print(f"  colonnes: {len(dataframe.columns)}")

    return parquet_path


def main() -> None:
    STRUCTURED_DIR.mkdir(parents=True, exist_ok=True)

    csv_files = find_csv_files()
    for csv_path in csv_files:
        convert_csv_to_parquet(csv_path)

    print("\nConversion terminee")


if __name__ == "__main__":
    main()
