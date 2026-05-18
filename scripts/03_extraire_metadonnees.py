from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
STRUCTURED_DIR = BASE_DIR / "data" / "structured"
METADATA_DIR = BASE_DIR / "metadata"
OUTPUT_PATH = METADATA_DIR / "metadonnees_extraites.json"


def find_parquet_files() -> list[Path]:
    if not STRUCTURED_DIR.exists():
        raise FileNotFoundError(f"dossier introuvable: {STRUCTURED_DIR}")

    parquet_files = sorted(STRUCTURED_DIR.glob("*.parquet"))
    if not parquet_files:
        raise FileNotFoundError(f"aucun fichier parquet trouve dans: {STRUCTURED_DIR}")

    return parquet_files


def extract_file_metadata(parquet_path: Path, extraction_date: str) -> dict:
    dataframe = pd.read_parquet(parquet_path)
    chemin_relatif = parquet_path.relative_to(BASE_DIR)
    columns = [
        {"nom": column_name, "type": str(dataframe[column_name].dtype)}
        for column_name in dataframe.columns
    ]

    return {
        "nom_table": parquet_path.stem,
        "chemin_fichier": chemin_relatif.as_posix(),
        "format": "parquet",
        "nombre_lignes": len(dataframe),
        "nombre_colonnes": len(dataframe.columns),
        "colonnes": columns,
        "taille_fichier_octets": parquet_path.stat().st_size,
        "date_extraction": extraction_date,
    }


def write_metadata(metadata: list[dict]) -> None:
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> None:
    extraction_date = datetime.now(timezone.utc).isoformat()
    parquet_files = find_parquet_files()
    metadata = [extract_file_metadata(path, extraction_date) for path in parquet_files]
    write_metadata(metadata)

    print("Metadonnees extraites")
    for table in metadata:
        print(
            f"- {table['nom_table']}: "
            f"{table['nombre_lignes']} lignes, "
            f"{table['nombre_colonnes']} colonnes"
        )
    print(f"Fichier cree: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
