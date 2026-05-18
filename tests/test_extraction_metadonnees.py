import json
from pathlib import Path
import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = BASE_DIR / "metadata" / "metadonnees_extraites.json"

EXPECTED_TABLES = {
    "avis_clients",
    "clients",
    "commandes",
    "paiements",
    "produits",
    "tickets_support",
}


class ExtractionMetadonneesTest(unittest.TestCase):
    def test_metadata_file_exists(self) -> None:
        self.assertTrue(OUTPUT_PATH.exists())

    def test_metadata_content(self) -> None:
        metadata = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        tables = {item["nom_table"] for item in metadata}

        self.assertEqual(tables, EXPECTED_TABLES)
        for item in metadata:
            self.assertEqual(item["format"], "parquet")
            self.assertGreater(item["nombre_lignes"], 0)
            self.assertGreater(item["nombre_colonnes"], 0)
            self.assertEqual(len(item["colonnes"]), item["nombre_colonnes"])
            self.assertGreater(item["taille_fichier_octets"], 0)
            self.assertIn("date_extraction", item)


if __name__ == "__main__":
    unittest.main()
