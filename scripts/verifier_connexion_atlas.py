from __future__ import annotations

import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from src.client_atlas import verifier_connexion  # noqa: E402


def main() -> None:
    try:
        version = verifier_connexion()
        nom = version.get("Name", "apache-atlas") if isinstance(version, dict) else "apache-atlas"
        numero = version.get("Version", "version inconnue") if isinstance(version, dict) else "version inconnue"
        print(f"Connexion a Atlas reussie: {nom} {numero}")
    except RuntimeError as error:
        print(f"Erreur de connexion Atlas: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
