
"""Fonctions de gestion des chronos de Marathon Predictor."""

from src.exceptions import DonneeInvalideError


DISTANCES = ("5K", "10K", "15K", "HALF")

NOMS_DISTANCES = {
    "5K": "5 km",
    "10K": "10 km",
    "15K": "15 km",
    "HALF": "demi-marathon"
}


def convertir_temps(secondes: float) -> str:
    """Convertit un temps en secondes au format HH:MM:SS."""
    secondes = round(secondes)

    heures = secondes // 3600
    minutes = (secondes % 3600) // 60
    secondes_restantes = secondes % 60

    return f"{heures:02d}:{minutes:02d}:{secondes_restantes:02d}"


def calculer_allure(secondes: float) -> str:
    """Calcule l'allure moyenne sur 42,195 km."""
    secondes_par_km = round(secondes / 42.195)

    minutes = secondes_par_km // 60
    secondes_restantes = secondes_par_km % 60

    return f"{minutes}:{secondes_restantes:02d}/km"


def lire_chrono(distance: str, champs_temps: dict) -> int:
    """Lit les champs d'un chrono et retourne les secondes."""
    champs = champs_temps[distance]

    try:
        heures = int(champs["heures"].get())
        minutes = int(champs["minutes"].get())
        secondes = int(champs["secondes"].get())

    except (TypeError, ValueError) as erreur:
        raise DonneeInvalideError(
            f"Le chrono au {NOMS_DISTANCES[distance]} "
            "doit contenir uniquement des nombres."
        ) from erreur

    if not 0 <= heures <= 9:
        raise DonneeInvalideError(
            f"Les heures au {NOMS_DISTANCES[distance]} "
            "doivent être entre 0 et 9."
        )

    if not 0 <= minutes <= 59:
        raise DonneeInvalideError(
            f"Les minutes au {NOMS_DISTANCES[distance]} "
            "doivent être entre 0 et 59."
        )

    if not 0 <= secondes <= 59:
        raise DonneeInvalideError(
            f"Les secondes au {NOMS_DISTANCES[distance]} "
            "doivent être entre 0 et 59."
        )

    return heures * 3600 + minutes * 60 + secondes


def valider_chronos(caracteristiques: dict) -> None:
    """Vérifie que les temps sont positifs et croissants."""
    if caracteristiques["5K"] <= 0:
        raise DonneeInvalideError(
            "Le temps au 5 km doit être supérieur à zéro."
        )

    for precedent, suivant in zip(DISTANCES, DISTANCES[1:]):
        temps_precedent = caracteristiques[precedent]
        temps_suivant = caracteristiques[suivant]

        if temps_suivant <= temps_precedent:
            raise DonneeInvalideError(
                f"Le temps au {NOMS_DISTANCES[suivant]} "
                f"({convertir_temps(temps_suivant)}) "
                f"doit être supérieur au temps au "
                f"{NOMS_DISTANCES[precedent]} "
                f"({convertir_temps(temps_precedent)})."
            )
