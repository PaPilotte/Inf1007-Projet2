import pytest

from src.chronos import (
    convertir_temps,
    calculer_allure,
    lire_chrono,
    valider_chronos
)
from src.exceptions import DonneeInvalideError


class FauxChamp:
    """Simule un champ Tkinter sans ouvrir de fenêtre."""

    def __init__(self, valeur):
        self.valeur = valeur

    def get(self):
        return self.valeur


def creer_champs(heures, minutes, secondes):
    """Crée de faux champs pour tester lire_chrono."""
    return {
        "5K": {
            "heures": FauxChamp(heures),
            "minutes": FauxChamp(minutes),
            "secondes": FauxChamp(secondes)
        }
    }


def creer_chronos():
    """Retourne des temps de passage cohérents."""
    return {
        "5K": 1500,
        "10K": 3000,
        "15K": 4500,
        "HALF": 6300
    }


# --------------------------------------------------
# Tests de convertir_temps()
# --------------------------------------------------

def test_convertir_temps_normal():
    assert convertir_temps(3661) == "01:01:01"


def test_convertir_temps_zero():
    assert convertir_temps(0) == "00:00:00"


def test_convertir_temps_marathon():
    assert convertir_temps(12600) == "03:30:00"


def test_convertir_temps_arrondi():
    assert convertir_temps(3661.6) == "01:01:02"


# --------------------------------------------------
# Tests de calculer_allure()
# --------------------------------------------------

def test_calculer_allure_marathon():
    assert calculer_allure(12600) == "4:59/km"


def test_calculer_allure_six_minutes():
    assert calculer_allure(42.195 * 360) == "6:00/km"


def test_calculer_allure_zero():
    assert calculer_allure(0) == "0:00/km"


# --------------------------------------------------
# Tests de lire_chrono()
# --------------------------------------------------

def test_lire_chrono_normal():
    champs = creer_champs("01", "30", "45")

    assert lire_chrono("5K", champs) == 5445


def test_lire_chrono_zero():
    champs = creer_champs("00", "00", "00")

    assert lire_chrono("5K", champs) == 0


def test_lire_chrono_maximum():
    champs = creer_champs("09", "59", "59")

    assert lire_chrono("5K", champs) == 35999


def test_lire_chrono_texte():
    champs = creer_champs("abc", "30", "00")

    with pytest.raises(DonneeInvalideError):
        lire_chrono("5K", champs)


def test_lire_chrono_heures_invalides():
    champs = creer_champs("10", "30", "00")

    with pytest.raises(DonneeInvalideError):
        lire_chrono("5K", champs)


def test_lire_chrono_heures_negatives():
    champs = creer_champs("-1", "30", "00")

    with pytest.raises(DonneeInvalideError):
        lire_chrono("5K", champs)


def test_lire_chrono_minutes_invalides():
    champs = creer_champs("01", "60", "00")

    with pytest.raises(DonneeInvalideError):
        lire_chrono("5K", champs)


def test_lire_chrono_secondes_invalides():
    champs = creer_champs("01", "30", "60")

    with pytest.raises(DonneeInvalideError):
        lire_chrono("5K", champs)


def test_lire_chrono_secondes_negatives():
    champs = creer_champs("01", "30", "-1")

    with pytest.raises(DonneeInvalideError):
        lire_chrono("5K", champs)


# --------------------------------------------------
# Tests de valider_chronos()
# --------------------------------------------------

def test_valider_chronos_normaux():
    chronos = creer_chronos()

    assert valider_chronos(chronos) is None


def test_valider_chronos_5km_zero():
    chronos = creer_chronos()
    chronos["5K"] = 0

    with pytest.raises(DonneeInvalideError):
        valider_chronos(chronos)


def test_valider_chronos_5km_negatif():
    chronos = creer_chronos()
    chronos["5K"] = -100

    with pytest.raises(DonneeInvalideError):
        valider_chronos(chronos)


def test_valider_chronos_10km_inferieur():
    chronos = creer_chronos()
    chronos["10K"] = 1200

    with pytest.raises(DonneeInvalideError):
        valider_chronos(chronos)


def test_valider_chronos_15km_inferieur():
    chronos = creer_chronos()
    chronos["15K"] = 2500

    with pytest.raises(DonneeInvalideError):
        valider_chronos(chronos)


def test_valider_chronos_demi_inferieur():
    chronos = creer_chronos()
    chronos["HALF"] = 4000

    with pytest.raises(DonneeInvalideError):
        valider_chronos(chronos)


def test_valider_chronos_temps_identiques():
    chronos = creer_chronos()
    chronos["10K"] = chronos["5K"]

    with pytest.raises(DonneeInvalideError):
        valider_chronos(chronos)
