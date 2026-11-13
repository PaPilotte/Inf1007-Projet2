
"""Exceptions personnalisées du projet."""


class DonneeInvalideError(Exception):
    """Levée quand une donnée (fichier, saisie, valeur) est invalide."""


class ModeleNonEntraineError(Exception):
    """Levée quand on utilise un modèle qui n'a pas encore été entraîné."""