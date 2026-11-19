import numpy as np

from src.entrainement import (
    afficher_resultats,
    tracer_exploration,
    tracer_predit_vs_reel,
)


def test_tracer_exploration_cree_l_image(tmp_path, donnees_marathon):
    """Le nuage de points est enregistré en PNG."""
    chemin = tmp_path / "exploration.png"

    tracer_exploration(donnees_marathon, str(chemin))

    assert chemin.exists()
    assert chemin.stat().st_size > 0


def test_tracer_predit_vs_reel_cree_l_image(tmp_path):
    """Le graphique prédit contre réel est enregistré en PNG."""
    chemin = tmp_path / "predit.png"
    reel = np.array([10000.0, 12000.0, 14000.0])
    predit = np.array([10100.0, 11900.0, 14200.0])

    tracer_predit_vs_reel(reel, predit, str(chemin))

    assert chemin.exists()
    assert chemin.stat().st_size > 0


def test_afficher_resultats_en_minutes(capsys):
    """Les métriques sont affichées converties en minutes."""
    resultats = {
        "mae_modele": 600,               # 10 minutes
        "mae_reference_moyenne": 1200,   # 20 minutes
        "mae_reference_naive": 900,      # 15 minutes
        "r2_modele": 0.9876,
    }

    afficher_resultats(resultats)
    sortie = capsys.readouterr().out

    assert "10.00 min" in sortie
    assert "20.00 min" in sortie
    assert "15.00 min" in sortie
    assert "0.9876" in sortie


# --------------------------------------------------
# Tests du pipeline complet d'entraînement
# --------------------------------------------------

from unittest.mock import Mock, call

import pytest

import src.entrainement as module_entrainement


@pytest.fixture
def pipeline_simule(monkeypatch, tmp_path, donnees_marathon):
    """Simule les opérations du pipeline sans entraîner le vrai modèle."""
    modele = Mock()

    resultats = {
        "mae_modele": 420,
        "mae_reference_moyenne": 1200,
        "mae_reference_naive": 800,
        "r2_modele": 0.95,
    }

    modele.entrainer.return_value = resultats

    y_reel = np.array([10000, 12000, 14000])
    y_predit = np.array([10100, 11900, 13900])
    modele.donnees_test.return_value = (y_reel, y_predit)

    charger = Mock(return_value=donnees_marathon)
    tracer_exploration = Mock()
    tracer_predictions = Mock()
    afficher = Mock()

    monkeypatch.setattr(
        module_entrainement, "charger_donnees", charger
    )
    monkeypatch.setattr(
        module_entrainement, "Modele", Mock(return_value=modele)
    )
    monkeypatch.setattr(
        module_entrainement,
        "tracer_exploration",
        tracer_exploration
    )
    monkeypatch.setattr(
        module_entrainement,
        "tracer_predit_vs_reel",
        tracer_predictions
    )
    monkeypatch.setattr(
        module_entrainement,
        "afficher_resultats",
        afficher
    )

    monkeypatch.setattr(
        module_entrainement,
        "DOSSIER_GRAPHIQUES",
        str(tmp_path / "graphiques")
    )
    monkeypatch.setattr(
        module_entrainement,
        "CHEMIN_MODELE",
        str(tmp_path / "modele.joblib")
    )
    monkeypatch.setattr(
        module_entrainement,
        "CHEMIN_METADONNEES",
        str(tmp_path / "metadonnees.json")
    )

    return {
        "modele": modele,
        "donnees": donnees_marathon,
        "resultats": resultats,
        "charger": charger,
        "tracer_exploration": tracer_exploration,
        "tracer_predictions": tracer_predictions,
        "afficher": afficher,
        "dossier": tmp_path / "graphiques",
        "y_reel": y_reel,
        "y_predit": y_predit,
        "tmp_path": tmp_path,
    }


def test_pipeline_entraine_et_sauvegarde(pipeline_simule):
    """Le pipeline charge les données, entraîne et sauvegarde."""
    simulation = pipeline_simule

    module_entrainement.main()

    simulation["charger"].assert_called_once_with(
        module_entrainement.CHEMIN_NETTOYE
    )

    simulation["modele"].entrainer.assert_called_once_with(
        simulation["donnees"]
    )

    simulation["afficher"].assert_called_once_with(
        simulation["resultats"]
    )

    simulation["modele"].donnees_test.assert_called_once()

    simulation["modele"].sauvegarder.assert_called_once_with(
        module_entrainement.CHEMIN_MODELE,
        module_entrainement.CHEMIN_METADONNEES,
        simulation["donnees"],
    )


def test_pipeline_prepare_les_graphiques(pipeline_simule):
    """Les deux graphiques reçoivent les données appropriées."""
    simulation = pipeline_simule

    module_entrainement.main()

    assert simulation["dossier"].is_dir()

    simulation["tracer_exploration"].assert_called_once_with(
        simulation["donnees"],
        str(simulation["dossier"] / "exploration.png"),
    )

    simulation["tracer_predictions"].assert_called_once()

    arguments = simulation["tracer_predictions"].call_args.args

    np.testing.assert_array_equal(
        arguments[0], simulation["y_reel"]
    )
    np.testing.assert_array_equal(
        arguments[1], simulation["y_predit"]
    )

    assert arguments[2] == str(
        simulation["dossier"] / "predit_vs_reel.png"
    )


def test_pipeline_erreur_chargement(pipeline_simule, monkeypatch):
    """Une erreur de chargement empêche l'entraînement."""
    simulation = pipeline_simule

    monkeypatch.setattr(
        module_entrainement,
        "charger_donnees",
        Mock(side_effect=FileNotFoundError("CSV absent")),
    )

    with pytest.raises(FileNotFoundError, match="CSV absent"):
        module_entrainement.main()

    simulation["modele"].entrainer.assert_not_called()
    simulation["modele"].sauvegarder.assert_not_called()
