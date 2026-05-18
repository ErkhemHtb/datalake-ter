import os
import unittest

from src.client_atlas import get_config_atlas


class ClientAtlasTest(unittest.TestCase):
    def test_default_config(self) -> None:
        old_values = {
            "ATLAS_URL": os.environ.pop("ATLAS_URL", None),
            "ATLAS_USERNAME": os.environ.pop("ATLAS_USERNAME", None),
            "ATLAS_PASSWORD": os.environ.pop("ATLAS_PASSWORD", None),
        }

        try:
            config = get_config_atlas()
            self.assertEqual(config["api_url"], "http://localhost:21000/api/atlas/v2")
            self.assertEqual(config["server_url"], "http://localhost:21000")
            self.assertEqual(config["username"], "admin")
            self.assertEqual(config["password"], "admin")
        finally:
            for key, value in old_values.items():
                if value is not None:
                    os.environ[key] = value


if __name__ == "__main__":
    unittest.main()
