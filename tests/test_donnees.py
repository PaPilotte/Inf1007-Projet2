import pandas as pd
import pytest

from src.donnees import (
    Variable,
    VariableNumerique,
    VariableCategorielle,
    charger_donnees,
    nettoyer_donnees,
    verifier_temps,
    echantillonner_donnees,
    sauvegarder_donnees
)

from src.exceptions import DonneeInvalideError


# --------------------------------------------------
# Données fictives pour les tests
# --------------------------------------------------

@pytest.fixture
def donnees_exemple():
    """Crée un petit jeu de données fictif."""
    return pd.DataFrame({
        "Name": ["Alex", "Sam", "Max", "Charlie"],
        "Age": [25, 35, 45, 30],
        "M/F": ["M", "F", "X", "M"],
        "5K": [1200, 1500, 1400, 1300],
        "10K": [2450, 3050, 2850, 2650],
        "15K": [3700, 4600, 4300, 4000],
        "HALF": [5300, 6600, 6100, 5700],
        "Finish Net": [10800, 13800, 12500, 12000]
    })


# --------------------------------------------------
# Tests du chargement et du nettoyage des données
# --------------------------------------------------

def test_charger_donnees(tmp_path):
    """Vérifie le chargement d'un CSV valide."""
    chemin = tmp_path / "test.csv"

    pd.DataFrame({"Age": [25, 30]}).to_csv(
        chemin, index=False
    )

    resultat = charger_donnees(str(chemin))

    assert len(resultat) == 2
    assert list(resultat.columns) == ["Age"]


def test_charger_fichier_inexistant(tmp_path):
    """Vérifie l'erreur si le fichier n'existe pas."""
    chemin = tmp_path / "inexistant.csv"

    with pytest.raises(FileNotFoundError):
        charger_donnees(str(chemin))


def test_nettoyer_colonnes(donnees_exemple):
    """Vérifie la sélection des 7 colonnes."""
    resultat = nettoyer_donnees(donnees_exemple)

    assert list(resultat.columns) == [
        "Age", "M/F", "5K", "10K",
        "15K", "HALF", "Finish Net"
    ]


def test_filtrer_categories(donnees_exemple):
    """Vérifie que la catégorie X est exclue."""
    resultat = nettoyer_donnees(donnees_exemple)

    assert len(resultat) == 3
    assert set(resultat["M/F"]) == {"M", "F"}


def test_colonne_manquante(donnees_exemple):
    """Vérifie l'erreur lorsqu'une colonne manque."""
    donnees = donnees_exemple.drop(columns=["HALF"])

    with pytest.raises(ValueError):
        nettoyer_donnees(donnees)


def test_temps_valides(donnees_exemple):
    """Vérifie que les temps valides sont acceptés."""
    donnees = nettoyer_donnees(donnees_exemple)

    invalides = verifier_temps(donnees)

    assert invalides.empty


def test_temps_incoherents(donnees_exemple):
    """Vérifie la détection d'un temps incohérent."""
    donnees = nettoyer_donnees(donnees_exemple)
    donnees.loc[0, "10K"] = 1000

    invalides = verifier_temps(donnees)

    assert len(invalides) == 1


def test_nombre_observations(donnees_exemple):
    """Vérifie la taille de l'échantillon."""
    donnees = nettoyer_donnees(donnees_exemple)

    resultat = echantillonner_donnees(
        donnees, nombre=2
    )

    assert len(resultat) == 2


def test_echantillonnage_reproductible(donnees_exemple):
    """Vérifie qu'une même graine donne le même résultat."""
    donnees = nettoyer_donnees(donnees_exemple)

    premier = echantillonner_donnees(donnees, 2, 42)
    deuxieme = echantillonner_donnees(donnees, 2, 42)

    pd.testing.assert_frame_equal(premier, deuxieme)


def test_echantillonnage_invalide(donnees_exemple):
    """Vérifie le refus d'un échantillon trop grand."""
    donnees = nettoyer_donnees(donnees_exemple)

    with pytest.raises(ValueError):
        echantillonner_donnees(donnees, nombre=100)


def test_sauvegarder_donnees(tmp_path, donnees_exemple):
    """Vérifie la sauvegarde d'un CSV."""
    chemin = tmp_path / "sauvegarde.csv"

    sauvegarder_donnees(donnees_exemple, str(chemin))

    assert chemin.exists()

    resultat = pd.read_csv(chemin)

    pd.testing.assert_frame_equal(
        resultat, donnees_exemple
    )


# --------------------------------------------------
# Tests des classes de variables (POO)
# --------------------------------------------------

def test_variable_abstraite():
    """Vérifie qu'on ne peut pas instancier la classe abstraite."""
    with pytest.raises(TypeError):
        Variable("Age")


def test_variable_numerique_valide():
    """Vérifie l'acceptation des nombres dans l'intervalle."""
    variable = VariableNumerique("Age", 18, 80)

    assert variable.valider(25) == 25.0
    assert variable.valider("35") == 35.0


def test_variable_numerique_hors_intervalle():
    """Vérifie le refus d'une valeur hors intervalle."""
    variable = VariableNumerique("Age", 18, 80)

    with pytest.raises(DonneeInvalideError):
        variable.valider(120)


def test_variable_numerique_non_numerique():
    """Vérifie le refus d'un texte non numérique."""
    variable = VariableNumerique("Age", 18, 80)

    with pytest.raises(DonneeInvalideError):
        variable.valider("bonjour")


def test_variable_numerique_non_finie():
    """Vérifie le refus des valeurs NaN et infinies."""
    variable = VariableNumerique("Age", 18, 80)

    with pytest.raises(DonneeInvalideError):
        variable.valider(float("nan"))

    with pytest.raises(DonneeInvalideError):
        variable.valider(float("inf"))


def test_variable_categorielle_valide():
    """Vérifie l'acceptation des catégories M et F."""
    variable = VariableCategorielle("M/F", ["M", "F"])

    assert variable.valider("M") == "M"
    assert variable.valider("F") == "F"


def test_variable_categorielle_invalide():
    """Vérifie le refus d'une catégorie inconnue."""
    variable = VariableCategorielle("M/F", ["M", "F"])

    with pytest.raises(DonneeInvalideError):
        variable.valider("X")


def test_variable_polymorphisme():
    """Vérifie la validation polymorphe de deux variables."""
    variables = [
        VariableNumerique("Age", 18, 80),
        VariableCategorielle("M/F", ["M", "F"])
    ]

    valeurs = [25, "M"]

    resultats = [
        variable.valider(valeur)
        for variable, valeur in zip(variables, valeurs)
    ]

    assert resultats == [25.0, "M"]


def test_variable_repr():
    """Vérifie la représentation des objets."""
    variable = VariableNumerique("Age", 18, 80)

    assert repr(variable) == "VariableNumerique('Age')"
