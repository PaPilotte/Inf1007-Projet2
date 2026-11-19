
"""Point d'entrée de Marathon Predictor."""

import os
import sys

# Ajouter la racine du projet aux chemins de recherche Python.
racine_projet = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if racine_projet not in sys.path:
    sys.path.insert(0, racine_projet)

from src.interface import main


if __name__ == "__main__":
    main()
