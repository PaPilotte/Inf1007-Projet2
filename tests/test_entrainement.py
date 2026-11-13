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