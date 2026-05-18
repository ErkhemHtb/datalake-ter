from pathlib import Path
import unittest

import pandas as pd
import yaml


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
STRUCTURED_DIR = BASE_DIR / "data" / "structured"
METADATA_DIR = BASE_DIR / "metadata"

EXPECTED_ROWS = {
    "clients": 1000,
    "produits": 200,
    "commandes": 3000,
    "paiements": 3000,
    "avis_clients": 1200,
    "tickets_support": 500,
}


class DatasetConsistencyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tables = {
            name: pd.read_csv(RAW_DIR / f"{name}.csv")
            for name in EXPECTED_ROWS
        }
        cls.table_metadata = yaml.safe_load((METADATA_DIR / "metadonnees_tables.yaml").read_text(encoding="utf-8"))
        cls.column_metadata = yaml.safe_load((METADATA_DIR / "classifications_colonnes.yaml").read_text(encoding="utf-8"))

    def test_expected_files_and_rows(self) -> None:
        for table_name, expected_rows in EXPECTED_ROWS.items():
            csv_path = RAW_DIR / f"{table_name}.csv"
            self.assertTrue(csv_path.exists(), f"csv manquant: {csv_path}")
            self.assertEqual(len(self.tables[table_name]), expected_rows)
            self.assertEqual(self.table_metadata[table_name]["expected_number_of_rows"], expected_rows)

    def test_columns_match_metadata(self) -> None:
        for table_name, dataframe in self.tables.items():
            csv_columns = list(dataframe.columns)
            metadata_columns = list(self.column_metadata[table_name].keys())
            self.assertEqual(csv_columns, metadata_columns, table_name)

    def test_relationships_are_consistent(self) -> None:
        clients = self.tables["clients"]
        produits = self.tables["produits"]
        commandes = self.tables["commandes"]
        paiements = self.tables["paiements"]
        avis = self.tables["avis_clients"]
        tickets = self.tables["tickets_support"]

        self.assertTrue(set(commandes["id_client"]).issubset(set(clients["id_client"])))
        self.assertTrue(set(paiements["id_commande"]).issubset(set(commandes["id_commande"])))
        self.assertTrue(set(avis["id_client"]).issubset(set(clients["id_client"])))
        self.assertTrue(set(avis["id_produit"]).issubset(set(produits["id_produit"])))
        self.assertTrue(set(tickets["id_client"]).issubset(set(clients["id_client"])))

    def test_payments_match_orders(self) -> None:
        commandes = self.tables["commandes"][["id_commande", "montant_total"]]
        paiements = self.tables["paiements"]
        merged = paiements.merge(commandes, on="id_commande", how="left")
        self.assertTrue((merged["montant"] == merged["montant_total"]).all())

    def test_parquet_matches_csv(self) -> None:
        for table_name, csv_dataframe in self.tables.items():
            parquet_path = STRUCTURED_DIR / f"{table_name}.parquet"
            self.assertTrue(parquet_path.exists(), f"parquet manquant: {parquet_path}")

            parquet_dataframe = pd.read_parquet(parquet_path)
            self.assertEqual(list(csv_dataframe.columns), list(parquet_dataframe.columns), table_name)
            self.assertEqual(len(csv_dataframe), len(parquet_dataframe), table_name)


if __name__ == "__main__":
    unittest.main()
