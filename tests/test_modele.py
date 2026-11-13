
import json

import numpy as np
import pytest

from src.exceptions import DonneeInvalideError, ModeleNonEntraineError
from src.modele import Modele, calculer_mae, calculer_r2, chronometrer


# ---------- Métriques ----------

def test_mae_valeur_connue():
    """MAE de [10, 20] contre [12, 18] : (2 + 2) / 2 = 2."""
    assert calculer_mae([10, 20], [12, 18]) == pytest.approx(2.0)


def test_mae_prediction_parfaite():
    """Des prédictions identiques donnent une MAE de 0."""
    assert calculer_mae([5, 6, 7], [5, 6, 7]) == pytest.approx(0.0)


def test_mae_tailles_differentes():
    """Deux tableaux de tailles différentes sont refusés."""
    with pytest.raises(DonneeInvalideError):
        calculer_mae([1, 2, 3], [1, 2])


def test_mae_tableaux_vides():
    """Des tableaux vides sont refusés."""
    with pytest.raises(DonneeInvalideError):
        calculer_mae([], [])


def test_r2_prediction_parfaite():
    """Prédictions parfaites : R² = 1."""
    assert calculer_r2([1, 2, 3, 4], [1, 2, 3, 4]) == pytest.approx(1.0)


def test_r2_prediction_moyenne():
    """Prédire toujours la moyenne donne un R² de 0."""
    reel = [1, 2, 3]
    predit = [2, 2, 2]  # la moyenne de reel est 2
    assert calculer_r2(reel, predit) == pytest.approx(0.0)


def test_r2_cible_constante():
    """Une cible constante rend le R² indéfini."""
    with pytest.raises(DonneeInvalideError):
        calculer_r2([5, 5, 5], [4, 5, 6])


# ---------- Décorateur ----------

def test_chronometrer_conserve_le_resultat(capsys):
    """Le décorateur ne change pas la valeur retournée et affiche la durée."""
    @chronometrer
    def additionner(a, b):
        return a + b

    assert additionner(2, 3) == 5
    assert "additionner" in capsys.readouterr().out


def test_chronometrer_conserve_le_nom():
    """@wraps conserve le nom de la fonction d'origine."""
    @chronometrer
    def ma_fonction():
        pass

    assert ma_fonction.__name__ == "ma_fonction"


# ---------- Classe Modele : état ----------

def test_modele_initial_non_entraine():
    """Un nouveau modèle n'est pas entraîné."""
    modele = Modele()

    assert modele.est_entraine is False
    assert modele.resultats == {}


def test_repr_change_avec_l_etat(donnees_marathon):
    """Le texte affiché reflète l'état du modèle."""
    modele = Modele()
    assert "non entraîné" in repr(modele)

    modele.entrainer(donnees_marathon)
    assert "non entraîné" not in repr(modele)


# ---------- Classe Modele : entraînement ----------

def test_entrainer_retourne_les_metriques(donnees_marathon):
    """entrainer() retourne toutes les clés attendues."""
    resultats = Modele().entrainer(donnees_marathon)

    cles_attendues = {
        "mae_modele", "r2_modele",
        "mae_reference_moyenne", "mae_reference_naive",
        "taille_entrainement", "taille_test",
    }
    assert cles_attendues <= set(resultats)


def test_entrainer_separation_80_20(donnees_marathon):
    """200 lignes : 160 pour l'entraînement, 40 pour le test."""
    resultats = Modele().entrainer(donnees_marathon)

    assert resultats["taille_entrainement"] == 160
    assert resultats["taille_test"] == 40


def test_entrainer_marque_comme_entraine(donnees_marathon):
    """Après entrainer(), est_entraine passe à True."""
    modele = Modele()
    modele.entrainer(donnees_marathon)

    assert modele.est_entraine is True


def test_modele_bat_la_reference_moyenne(donnees_marathon):
    """Sur des données très structurées, le modèle bat la moyenne simple."""
    resultats = Modele().entrainer(donnees_marathon)

    assert resultats["mae_modele"] < resultats["mae_reference_moyenne"]


def test_bon_r2_sur_donnees_structurees(donnees_marathon):
    """Les temps sont presque linéaires : R² proche de 1."""
    resultats = Modele().entrainer(donnees_marathon)

    assert resultats["r2_modele"] > 0.95


def test_entrainement_reproductible(donnees_marathon):
    """Même graine, mêmes résultats."""
    premier = Modele(graine=7).entrainer(donnees_marathon)
    deuxieme = Modele(graine=7).entrainer(donnees_marathon)

    assert premier["mae_modele"] == pytest.approx(deuxieme["mae_modele"])


def test_entrainer_colonne_manquante(donnees_marathon):
    """Une colonne absente déclenche DonneeInvalideError."""
    incomplet = donnees_marathon.drop(columns=["HALF"])

    with pytest.raises(DonneeInvalideError):
        Modele().entrainer(incomplet)


def test_resultats_est_une_copie(donnees_marathon):
    """Modifier le dictionnaire reçu ne change pas l'état interne."""
    modele = Modele()
    modele.entrainer(donnees_marathon)

    copie = modele.resultats
    copie["mae_modele"] = -1

    assert modele.resultats["mae_modele"] != -1


# ---------- Classe Modele : donnees_test ----------

def test_donnees_test_avant_entrainement():
    """Sans entraînement, donnees_test() lève une erreur."""
    with pytest.raises(ModeleNonEntraineError):
        Modele().donnees_test()


def test_donnees_test_apres_entrainement(donnees_marathon):
    """Après entraînement, on reçoit deux tableaux de 40 valeurs."""
    modele = Modele()
    modele.entrainer(donnees_marathon)

    reel, predit = modele.donnees_test()

    assert len(reel) == 40
    assert len(predit) == 40


# ---------- Classe Modele : prédiction ----------

def test_predire_avant_entrainement(coureur_exemple):
    """Prédire sans entraîner lève ModeleNonEntraineError."""
    with pytest.raises(ModeleNonEntraineError):
        Modele().predire(coureur_exemple)


def test_predire_retourne_un_float_plausible(donnees_marathon, coureur_exemple):
    """La prédiction est un float proche de 8.9 x 5K."""
    modele = Modele()
    modele.entrainer(donnees_marathon)

    prediction = modele.predire(coureur_exemple)

    assert isinstance(prediction, float)
    # 8.9 x 1500 = 13350 secondes, on tolère 5 %
    assert prediction == pytest.approx(13350, rel=0.05)


def test_predire_caracteristique_manquante(donnees_marathon, coureur_exemple):
    """Une caractéristique absente est refusée."""
    modele = Modele()
    modele.entrainer(donnees_marathon)
    del coureur_exemple["Age"]

    with pytest.raises(DonneeInvalideError):
        modele.predire(coureur_exemple)


def test_predire_genre_invalide(donnees_marathon, coureur_exemple):
    """Un genre autre que M ou F est refusé."""
    modele = Modele()
    modele.entrainer(donnees_marathon)
    coureur_exemple["M/F"] = "X"

    with pytest.raises(DonneeInvalideError):
        modele.predire(coureur_exemple)


def test_predire_valeur_non_numerique(donnees_marathon, coureur_exemple):
    """Un texte à la place d'un nombre est refusé."""
    modele = Modele()
    modele.entrainer(donnees_marathon)
    coureur_exemple["5K"] = "rapide"

    with pytest.raises(DonneeInvalideError):
        modele.predire(coureur_exemple)


def test_predire_accepte_du_texte_numerique(donnees_marathon, coureur_exemple):
    """Un nombre écrit en texte ("1500") est converti en float."""
    modele = Modele()
    modele.entrainer(donnees_marathon)
    coureur_exemple["5K"] = "1500"

    assert isinstance(modele.predire(coureur_exemple), float)


# ---------- Classe Modele : sauvegarde et chargement ----------

def test_sauvegarder_avant_entrainement(tmp_path, donnees_marathon):
    """Sauvegarder un modèle non entraîné est refusé."""
    with pytest.raises(ModeleNonEntraineError):
        Modele().sauvegarder(
            str(tmp_path / "m.joblib"),
            str(tmp_path / "m.json"),
            donnees_marathon,
        )


def test_sauvegarder_cree_les_fichiers(tmp_path, donnees_marathon):
    """Les fichiers .joblib et .json sont créés, même dans un sous-dossier neuf."""
    modele = Modele()
    modele.entrainer(donnees_marathon)
    chemin_modele = tmp_path / "nouveau_dossier" / "m.joblib"
    chemin_meta = tmp_path / "nouveau_dossier" / "m.json"

    modele.sauvegarder(str(chemin_modele), str(chemin_meta), donnees_marathon)

    assert chemin_modele.exists()
    assert chemin_meta.exists()


def test_metadonnees_contenu(tmp_path, donnees_marathon):
    """Le JSON contient les colonnes, les intervalles et les métriques."""
    modele = Modele()
    modele.entrainer(donnees_marathon)
    chemin_meta = tmp_path / "m.json"

    modele.sauvegarder(str(tmp_path / "m.joblib"), str(chemin_meta), donnees_marathon)

    with open(chemin_meta, encoding="utf-8") as fichier:
        meta = json.load(fichier)

    assert meta["cible"] == "Finish Net"
    assert meta["categories"] == {"M/F": ["M", "F"]}
    assert set(meta["intervalles"]) == {"Age", "5K", "10K", "15K", "HALF"}
    assert "mae_modele" in meta["metriques"]


def test_charger_fichier_inexistant(tmp_path):
    """Charger un fichier absent lève FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        Modele.charger(str(tmp_path / "absent.joblib"))


def test_charger_donne_un_modele_entraine(tmp_path, donnees_marathon):
    """Un modèle chargé est considéré comme entraîné."""
    modele = Modele()
    modele.entrainer(donnees_marathon)
    chemin = tmp_path / "m.joblib"
    modele.sauvegarder(str(chemin), str(tmp_path / "m.json"), donnees_marathon)

    recharge = Modele.charger(str(chemin))

    assert recharge.est_entraine is True


def test_aller_retour_meme_prediction(tmp_path, donnees_marathon, coureur_exemple):
    """Le modèle rechargé prédit exactement comme l'original."""
    original = Modele()
    original.entrainer(donnees_marathon)
    chemin = tmp_path / "m.joblib"
    original.sauvegarder(str(chemin), str(tmp_path / "m.json"), donnees_marathon)

    recharge = Modele.charger(str(chemin))

    assert recharge.predire(coureur_exemple) == pytest.approx(
        original.predire(coureur_exemple)
    )