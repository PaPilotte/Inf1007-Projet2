
"""Tests de l'historique des prédictions."""

import csv

from src.historique import HistoriquePredictions


def test_historique_vide(tmp_path):
    historique = HistoriquePredictions(
        str(tmp_path / "historique.csv")
    )

    assert historique.consulter() == []


def test_ajouter_prediction(tmp_path):
    historique = HistoriquePredictions(
        str(tmp_path / "historique.csv")
    )

    caracteristiques = {
        "Age": 20,
        "M/F": "M",
        "5K": 1320,
        "10K": 2700,
        "15K": 4080,
        "HALF": 5760
    }

    historique.ajouter(caracteristiques, 12300)

    predictions = historique.consulter()

    assert len(predictions) == 1
    assert predictions[0]["Age"] == "20"
    assert predictions[0]["Sexe"] == "M"
    assert float(predictions[0]["Prediction"]) == 12300


def test_plusieurs_predictions(tmp_path):
    historique = HistoriquePredictions(
        str(tmp_path / "historique.csv")
    )

    caracteristiques = {
        "Age": 20,
        "M/F": "M",
        "5K": 1320,
        "10K": 2700,
        "15K": 4080,
        "HALF": 5760
    }

    historique.ajouter(caracteristiques, 12300)
    historique.ajouter(caracteristiques, 12500)

    predictions = historique.consulter()

    assert len(predictions) == 2
    assert float(predictions[0]["Prediction"]) == 12300
    assert float(predictions[1]["Prediction"]) == 12500


def test_entete_csv_unique(tmp_path):
    chemin = tmp_path / "historique.csv"
    historique = HistoriquePredictions(str(chemin))

    caracteristiques = {
        "Age": 20,
        "M/F": "M",
        "5K": 1320,
        "10K": 2700,
        "15K": 4080,
        "HALF": 5760
    }

    historique.ajouter(caracteristiques, 12300)
    historique.ajouter(caracteristiques, 12500)

    with open(chemin, newline="", encoding="utf-8") as fichier:
        lignes = list(csv.reader(fichier))

    assert len(lignes) == 3
    assert lignes[0] == HistoriquePredictions.COLONNES
