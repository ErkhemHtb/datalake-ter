import importlib.util
from pathlib import Path
import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
SCRIPT_PATH = BASE_DIR / "scripts" / "04_creer_types_atlas.py"


def charger_module():
    spec = importlib.util.spec_from_file_location("creer_types_atlas", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ModeleAtlasTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = charger_module()

    def test_types_principaux(self) -> None:
        table = self.module.definition_table()
        colonne = self.module.definition_colonne()

        self.assertEqual(table["name"], "datalake_table")
        self.assertEqual(colonne["name"], "datalake_column")

    def test_classifications_attendues(self) -> None:
        self.assertIn("DONNEE_PERSONNELLE", self.module.CLASSIFICATIONS)
        self.assertIn("DONNEE_FINANCIERE", self.module.CLASSIFICATIONS)
        self.assertIn("CLE_PRIMAIRE", self.module.CLASSIFICATIONS)
        self.assertIn("NON_SENSIBLE", self.module.CLASSIFICATIONS)


if __name__ == "__main__":
    unittest.main()
