
import os
import pandas as pd


# Chemins et constantes du projet
DOSSIER_PROJET = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

CHEMIN_NETTOYE = os.path.join(
    DOSSIER_PROJET,
    "donnees",
    "boston-nettoye.csv"
)

COLONNES_A_GARDER = [
    "Age",
    "M/F",
    "5K",
    "10K",
    "15K",
    "HALF",
    "Finish Net"
]


def charger_donnees(chemin: str) -> pd.DataFrame:
    """
    Charge un fichier CSV.

    Args:
        chemin: Chemin vers le fichier CSV.

    Returns:
        DataFrame contenant les données.

    Raises:
        FileNotFoundError: Si le fichier n'existe pas.
    """
    if not os.path.exists(chemin):
        raise FileNotFoundError(
            f"Fichier introuvable : {chemin}"
        )

    return pd.read_csv(chemin)


def nettoyer_donnees(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sélectionne les colonnes utiles et conserve M/F.

    Args:
        df: Données originales.

    Returns:
        DataFrame contenant les colonnes sélectionnées.

    Raises:
        ValueError: Si une colonne est manquante.
    """
    colonnes_manquantes = [
        colonne for colonne in COLONNES_A_GARDER
        if colonne not in df.columns
    ]

    if colonnes_manquantes:
        raise ValueError(
            f"Colonnes manquantes : {colonnes_manquantes}"
        )

    df_nettoye = df[COLONNES_A_GARDER].copy()

    df_nettoye = df_nettoye[
        df_nettoye["M/F"].isin(["M", "F"])
    ].copy()

    return df_nettoye


def verifier_temps(df: pd.DataFrame) -> pd.DataFrame:
    """
    Repère les observations aux temps incohérents.

    Args:
        df: Données à vérifier.

    Returns:
        DataFrame des observations incohérentes.
    """
    invalides = df[
        (df["5K"] <= 0) |
        (df["5K"] >= df["10K"]) |
        (df["10K"] >= df["15K"]) |
        (df["15K"] >= df["HALF"]) |
        (df["HALF"] >= df["Finish Net"])
    ]

    return invalides


def echantillonner_donnees(
    df: pd.DataFrame,
    nombre: int = 49000,
    graine: int = 42
) -> pd.DataFrame:
    """
    Sélectionne un échantillon aléatoire reproductible.

    Args:
        df: Données à échantillonner.
        nombre: Nombre de lignes souhaité.
        graine: Graine aléatoire.

    Returns:
        DataFrame échantillonné.

    Raises:
        ValueError: Si le nombre demandé est invalide.
    """
    if nombre <= 0 or nombre > len(df):
        raise ValueError(
            "Nombre d'observations invalide."
        )

    return df.sample(
        n=nombre,
        random_state=graine
    ).reset_index(drop=True)


def sauvegarder_donnees(
    df: pd.DataFrame,
    chemin: str
) -> None:
    """
    Sauvegarde un DataFrame au format CSV.

    Args:
        df: Données à sauvegarder.
        chemin: Destination du fichier CSV.
    """
    df.to_csv(chemin, index=False)


def main() -> None:
    """Charge et vérifie le fichier Boston nettoyé."""

    # 1. Charger les données nettoyées
    df = charger_donnees(CHEMIN_NETTOYE)

    print("=== DONNÉES NETTOYÉES ===")
    print("Dimensions :", df.shape)

    # 2. Vérifier les colonnes
    if list(df.columns) != COLONNES_A_GARDER:
        raise ValueError(
            "Les colonnes du CSV sont incorrectes."
        )

    # 3. Vérifier les valeurs manquantes
    valeurs_manquantes = df.isna().sum().sum()

    print("Valeurs manquantes :", valeurs_manquantes)

    if valeurs_manquantes > 0:
        raise ValueError(
            "Le fichier contient des valeurs manquantes."
        )

    # 4. Vérifier la cohérence des temps
    invalides = verifier_temps(df)

    print("Temps incohérents :", len(invalides))

    if not invalides.empty:
        raise ValueError(
            "Le fichier contient des temps incohérents."
        )

    # 5. Vérifier les catégories M/F
    if not df["M/F"].isin(["M", "F"]).all():
        raise ValueError(
            "Le fichier contient une catégorie M/F invalide."
        )

    # 6. Vérifier le nombre d'observations
    if len(df) != 49000:
        raise ValueError(
            "Le fichier doit contenir 49 000 observations."
        )

    # 7. Afficher les statistiques
    print("\n=== ÉCHANTILLON FINAL ===")
    print("Dimensions :", df.shape)

    print("\nRépartition H/F :")
    print(df["M/F"].value_counts())

    print("\nStatistiques des temps :")
    print(df["Finish Net"].describe())

    print("\n=== VÉRIFICATION TERMINÉE ===")
    print("Fichier vérifié avec succès!")


if __name__ == "__main__":
    main()















# def donnees_test():
#     return 1+1


