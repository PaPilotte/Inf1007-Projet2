"""Graphiques affichés par l’application Marathon Predictor."""

from typing import Any

from matplotlib.figure import Figure

import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


DISTANCES_KM = (5, 10, 15, 21.0975)
COLONNES_TEMPS = ("5K", "10K", "15K", "HALF")


def creer_figure_progression(
    caracteristiques: dict[str, Any], prediction: float
) -> Figure:
    """Crée le graphique des temps intermédiaires et du temps final prédit.

    Args:
        caracteristiques: Données validées contenant les temps intermédiaires
            en secondes, sous les clés 5K, 10K, 15K et HALF.
        prediction: Temps final prédit, en secondes.

    Returns:
        Une figure Matplotlib présentant les temps cumulés en minutes.

    Raises:
        KeyError: Si un temps intermédiaire requis est absent.
        TypeError: Si une valeur ne peut pas être convertie en nombre.
        ValueError: Si une chaîne ne représente pas un nombre valide.
    """
    distances = list(DISTANCES_KM) + [42.195]
    temps_minutes = [
        float(caracteristiques[colonne]) / 60
        for colonne in COLONNES_TEMPS
    ] + [float(prediction) / 60]

    figure = Figure(figsize=(7, 4.5), tight_layout=True)
    axes = figure.subplots()

    axes.plot(
        distances[:-1], temps_minutes[:-1],
        marker="o", linewidth=2, color="tab:blue",
        label="Temps saisis"
    )
    axes.plot(
        distances[-2:], temps_minutes[-2:],
        marker="o", linewidth=2, linestyle="--", color="tab:orange",
        label="Projection jusqu'au marathon"
    )

    axes.set_title("Progression des temps et prédiction au marathon")
    axes.set_xlabel("Distance parcourue (km)")
    axes.set_ylabel("Temps cumulé (minutes)")
    axes.set_xticks(
        distances, ["5 km", "10 km", "15 km", "Semi", "Marathon"]
    )
    axes.grid(True, linestyle=":", alpha=0.6)
    axes.legend()

    return figure


def afficher_graphique_progression(
    parent: Any, caracteristiques: dict[str, Any], prediction: float
) -> None:
    """Ouvre une fenêtre Tkinter contenant le graphique de progression.

    Args:
        parent: Fenêtre Tkinter parente.
        caracteristiques: Données validées contenant les temps intermédiaires
            en secondes.
        prediction: Temps final prédit, en secondes.

    Raises:
        ImportError: Si le module d’intégration Tk de Matplotlib est indisponible.
        tkinter.TclError: Si Tkinter ne peut pas créer la fenêtre.
        KeyError: Si un temps intermédiaire requis est absent.
        TypeError: Si une valeur ne peut pas être convertie en nombre.
        ValueError: Si une chaîne ne représente pas un nombre valide.
    """
    

    figure = creer_figure_progression(caracteristiques, prediction)
    fenetre = tk.Toplevel(parent)
    fenetre.title("Progression de la prédiction")
    fenetre.transient(parent)
    fenetre.geometry("760x520")

    conteneur = ttk.Frame(fenetre, padding=10)
    conteneur.pack(fill="both", expand=True)

    canvas = FigureCanvasTkAgg(figure, master=conteneur)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    def nettoyer_figure(event: Any) -> None:
        """Libère la figure même lorsque la fenêtre parente est fermée."""
        if event.widget is fenetre:
            figure.clear()

    def fermer_fenetre() -> None:
        """Détruit les éléments Tkinter et libère la figure à la fermeture."""
        canvas.get_tk_widget().destroy()
        figure.clear()
        fenetre.destroy()

    fenetre.bind("<Destroy>", nettoyer_figure, add="+")
    fenetre.protocol("WM_DELETE_WINDOW", fermer_fenetre)