"""Script d'entraînement : charge, explore, entraîne, évalue et sauvegarde."""

import os

import matplotlib
matplotlib.use("Agg")  # aucun affichage à l'écran : on enregistre les images
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.donnees import CHEMIN_NETTOYE, charger_donnees
from src.modele import CHEMIN_METADONNEES, CHEMIN_MODELE, DOSSIER_PROJET, Modele


DOSSIER_GRAPHIQUES = os.path.join(DOSSIER_PROJET, "graphiques")


def tracer_exploration(df: pd.DataFrame, chemin_image: str) -> None:
    """Enregistre un nuage de points HALF contre Finish Net, coloré par genre."""
    fig, ax = plt.subplots(figsize=(7, 5))
    for genre, couleur in [("M", "tab:blue"), ("F", "tab:orange")]:
        sous_df = df[df["M/F"] == genre]
        ax.scatter(sous_df["HALF"] / 60, sous_df["Finish Net"] / 60,
                   s=2, alpha=0.3, color=couleur, label=genre)
    ax.set_title("Temps final selon le temps au semi-marathon")
    ax.set_xlabel("Temps au HALF (minutes)")
    ax.set_ylabel("Temps final (minutes)")
    ax.legend(markerscale=5)
    fig.savefig(chemin_image, dpi=150, bbox_inches="tight")
    plt.close(fig)


def tracer_predit_vs_reel(y_reel: np.ndarray, y_predit: np.ndarray,
                          chemin_image: str) -> None:
    """Enregistre le graphique prédit contre réel (diagonale = prédiction parfaite)."""
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(y_reel / 60, y_predit / 60, s=2, alpha=0.3, label="Coureurs (test)")
    limites = [np.min(y_reel) / 60, np.max(y_reel) / 60]
    ax.plot(limites, limites, color="red", label="Prédiction parfaite")
    ax.set_title("Temps prédit contre temps réel (jeu de test)")
    ax.set_xlabel("Temps réel (minutes)")
    ax.set_ylabel("Temps prédit (minutes)")
    ax.legend(markerscale=5)
    fig.savefig(chemin_image, dpi=150, bbox_inches="tight")
    plt.close(fig)


def afficher_resultats(resultats: dict) -> None:
    """Affiche les métriques en minutes, plus lisibles qu'en secondes."""
    print("\n=== RÉSULTATS (jeu de test) ===")
    print(f"MAE modèle             : {resultats['mae_modele'] / 60:.2f} min")
    print(f"MAE référence moyenne  : {resultats['mae_reference_moyenne'] / 60:.2f} min")
    print(f"MAE référence 2 x HALF : {resultats['mae_reference_naive'] / 60:.2f} min")
    print(f"R² modèle              : {resultats['r2_modele']:.4f}")


def main() -> None:
    """Pipeline complet d'entraînement."""
    df = charger_donnees(CHEMIN_NETTOYE)
    os.makedirs(DOSSIER_GRAPHIQUES, exist_ok=True)

    tracer_exploration(df, os.path.join(DOSSIER_GRAPHIQUES, "exploration.png"))

    modele = Modele()
    resultats = modele.entrainer(df)
    afficher_resultats(resultats)

    y_test, predictions = modele.donnees_test()
    tracer_predit_vs_reel(y_test, predictions,
                          os.path.join(DOSSIER_GRAPHIQUES, "predit_vs_reel.png"))

    modele.sauvegarder(CHEMIN_MODELE, CHEMIN_METADONNEES, df)
    print(f"\nModèle sauvegardé : {CHEMIN_MODELE}")
    print(f"Métadonnées       : {CHEMIN_METADONNEES}")


if __name__ == "__main__":
    main()