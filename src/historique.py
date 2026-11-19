import csv
import os
from datetime import datetime


class HistoriquePredictions:
    """Enregistre et consulte les prédictions dans un fichier CSV."""

    COLONNES = [
        "Date",
        "Age",
        "Sexe",
        "5K",
        "10K",
        "15K",
        "HALF",
        "Prediction"
    ]

    def __init__(self, chemin: str = "historique.csv") -> None:
        """Initialise le chemin du fichier d'historique.

        Args:
            chemin: Chemin vers le fichier CSV d'historique.
        """
        self._chemin = chemin

    def ajouter(
        self, caracteristiques: dict, prediction: float
    ) -> None:
        """Ajoute une prédiction au fichier CSV.

        Args:
            caracteristiques: Informations du coureur et temps
                de passage, exprimés en secondes.
            prediction: Temps final prédit au marathon en secondes.

        Returns:
            None. La prédiction est ajoutée au fichier CSV.

        Raises:
            KeyError: Si une caractéristique obligatoire est absente.
            OSError: Si le fichier ne peut pas être écrit.
            csv.Error: Si une erreur survient pendant l'écriture CSV.
        """
        dossier = os.path.dirname(self._chemin)

        if dossier:
            os.makedirs(dossier, exist_ok=True)

        fichier_existe = (
            os.path.exists(self._chemin)
            and os.path.getsize(self._chemin) > 0
        )

        ligne = {
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Age": caracteristiques["Age"],
            "Sexe": caracteristiques["M/F"],
            "5K": caracteristiques["5K"],
            "10K": caracteristiques["10K"],
            "15K": caracteristiques["15K"],
            "HALF": caracteristiques["HALF"],
            "Prediction": prediction
        }

        with open(
            self._chemin,
            "a",
            newline="",
            encoding="utf-8"
        ) as fichier:
            writer = csv.DictWriter(
                fichier,
                fieldnames=self.COLONNES
            )

            if not fichier_existe:
                writer.writeheader()

            writer.writerow(ligne)

    def consulter(self) -> list[dict]:
        """Retourne les prédictions enregistrées.

        Returns:
            Liste de dictionnaires représentant les prédictions.
            Retourne une liste vide si le fichier n'existe pas.

        Raises:
            OSError: Si le fichier ne peut pas être lu.
            csv.Error: Si une erreur survient pendant la lecture CSV.
            UnicodeError: Si le contenu ne peut pas être décodé.
        """
        if not os.path.exists(self._chemin):
            return []

        with open(
            self._chemin,
            "r",
            newline="",
            encoding="utf-8"
        ) as fichier:
            reader = csv.DictReader(fichier)
            return list(reader)
