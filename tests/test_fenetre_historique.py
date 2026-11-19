from unittest.mock import Mock

import pytest

import src.fenetre_historique as module_historique


@pytest.fixture
def fenetre_simulee(monkeypatch):
    """Remplace les widgets Tkinter par des objets simulés."""
    fausse_fenetre = Mock()
    faux_tableau = Mock()
    faux_label = Mock()

    monkeypatch.setattr(
        module_historique.tk,
        "Toplevel",
        Mock(return_value=fausse_fenetre)
    )

    monkeypatch.setattr(
        module_historique.ttk,
        "Frame",
        Mock(return_value=Mock())
    )

    monkeypatch.setattr(
        module_historique.ttk,
        "Label",
        faux_label
    )

    monkeypatch.setattr(
        module_historique.ttk,
        "Treeview",
        Mock(return_value=faux_tableau)
    )

    monkeypatch.setattr(
        module_historique.ttk,
        "Scrollbar",
        Mock(return_value=Mock())
    )

    return {
        "fenetre": fausse_fenetre,
        "tableau": faux_tableau,
        "label": faux_label
    }


@pytest.fixture
def predictions_exemples():
    """Retourne deux prédictions fictives."""
    return [
        {
            "Date": "2026-11-18 10:00:00",
            "Age": "25",
            "Sexe": "M",
            "5K": "1500",
            "10K": "3000",
            "15K": "4500",
            "HALF": "6300",
            "Prediction": "13000"
        },
        {
            "Date": "2026-11-19 11:00:00",
            "Age": "30",
            "Sexe": "F",
            "5K": "1400",
            "10K": "2900",
            "15K": "4400",
            "HALF": "6200",
            "Prediction": "12500"
        }
    ]


def test_fenetre_creee(fenetre_simulee):
    """Vérifie la création de la fenêtre."""
    parent = Mock()

    module_historique.afficher_historique(parent, [])

    module_historique.tk.Toplevel.assert_called_once_with(parent)

    fenetre_simulee["fenetre"].title.assert_called_once_with(
        "Historique des prédictions"
    )


def test_nombre_predictions_affiche(
    fenetre_simulee, predictions_exemples
):
    """Vérifie l'affichage du nombre de prédictions."""
    module_historique.afficher_historique(
        Mock(), predictions_exemples
    )

    textes = [
        appel.kwargs.get("text")
        for appel in fenetre_simulee["label"].call_args_list
    ]

    assert "Nombre de prédictions : 2" in textes


def test_predictions_plus_recentes_en_premier(
    fenetre_simulee, predictions_exemples
):
    """La dernière prédiction enregistrée apparaît en premier."""
    module_historique.afficher_historique(
        Mock(), predictions_exemples
    )

    appels = fenetre_simulee["tableau"].insert.call_args_list

    assert len(appels) == 2

    premiere_ligne = appels[0].kwargs["values"]
    deuxieme_ligne = appels[1].kwargs["values"]

    assert premiere_ligne[0] == "2026-11-19 11:00:00"
    assert deuxieme_ligne[0] == "2026-11-18 10:00:00"


def test_chronos_correctement_formates(
    fenetre_simulee, predictions_exemples
):
    """Les temps en secondes sont affichés en HH:MM:SS."""
    module_historique.afficher_historique(
        Mock(), predictions_exemples
    )

    appels = fenetre_simulee["tableau"].insert.call_args_list
    valeurs = appels[1].kwargs["values"]

    assert valeurs[3] == "00:25:00"
    assert valeurs[4] == "00:50:00"
    assert valeurs[5] == "01:15:00"
    assert valeurs[6] == "01:45:00"
    assert valeurs[7] == "03:36:40"


def test_historique_vide(fenetre_simulee):
    """Un historique vide affiche un message explicatif."""
    module_historique.afficher_historique(Mock(), [])

    fenetre_simulee["tableau"].insert.assert_not_called()

    textes = [
        appel.kwargs.get("text")
        for appel in fenetre_simulee["label"].call_args_list
    ]

    assert "Aucune prédiction enregistrée pour le moment." in textes


def test_ligne_incomplete_ignoree(
    fenetre_simulee, predictions_exemples
):
    """Une ligne contenant une colonne manquante est ignorée."""
    ligne_invalide = {
        "Date": "2026-11-20",
        "Age": "25"
    }

    predictions = predictions_exemples + [ligne_invalide]

    module_historique.afficher_historique(
        Mock(), predictions
    )

    assert fenetre_simulee["tableau"].insert.call_count == 2


def test_chrono_invalide_ignore(
    fenetre_simulee, predictions_exemples
):
    """Une ligne contenant un chrono non numérique est ignorée."""
    ligne_invalide = predictions_exemples[0].copy()
    ligne_invalide["5K"] = "invalide"

    predictions = predictions_exemples + [ligne_invalide]

    module_historique.afficher_historique(
        Mock(), predictions
    )

    assert fenetre_simulee["tableau"].insert.call_count == 2


def test_colonnes_du_tableau(fenetre_simulee):
    """Vérifie la configuration des huit colonnes."""
    module_historique.afficher_historique(Mock(), [])

    tableau = fenetre_simulee["tableau"]

    assert tableau.heading.call_count == 8
    assert tableau.column.call_count == 8

    noms = [
        appel.args[0]
        for appel in tableau.heading.call_args_list
    ]

    assert noms == list(module_historique.COLONNES)
