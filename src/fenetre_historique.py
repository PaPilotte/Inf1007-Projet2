
"""Fenêtre Tkinter affichant l'historique des prédictions."""

import tkinter as tk
from tkinter import ttk

from src.chronos import convertir_temps


COLONNES = (
    "Date", "Age", "Sexe", "5K",
    "10K", "15K", "HALF", "Prediction"
)

TITRES = (
    "Date", "Âge", "Sexe", "5 km",
    "10 km", "15 km", "Demi-marathon", "Marathon prédit"
)


def afficher_historique(parent: tk.Tk, predictions: list[dict]) -> None:
    """Ouvre une fenêtre contenant les prédictions enregistrées."""
    fenetre = tk.Toplevel(parent)
    fenetre.title("Historique des prédictions")
    fenetre.geometry("1150x500")
    fenetre.minsize(650, 350)

    ttk.Label(
        fenetre,
        text="Historique des prédictions",
        font=("Arial", 20, "bold")
    ).pack(pady=20)

    ttk.Label(
        fenetre,
        text=f"Nombre de prédictions : {len(predictions)}",
        font=("Arial", 12)
    ).pack(pady=(0, 10))

    cadre = ttk.Frame(fenetre)
    cadre.pack(fill="both", expand=True, padx=15, pady=15)

    tableau = ttk.Treeview(
        cadre,
        columns=COLONNES,
        show="headings"
    )

    for colonne, titre in zip(COLONNES, TITRES):
        tableau.heading(colonne, text=titre)

        tableau.column(
            colonne,
            width=170 if colonne == "Date" else 130,
            minwidth=100,
            anchor="center",
            stretch=False
        )

    barre_verticale = ttk.Scrollbar(
        cadre,
        orient="vertical",
        command=tableau.yview
    )

    barre_horizontale = ttk.Scrollbar(
        cadre,
        orient="horizontal",
        command=tableau.xview
    )

    tableau.configure(
        yscrollcommand=barre_verticale.set,
        xscrollcommand=barre_horizontale.set
    )

    tableau.grid(row=0, column=0, sticky="nsew")
    barre_verticale.grid(row=0, column=1, sticky="ns")
    barre_horizontale.grid(row=1, column=0, sticky="ew")

    cadre.rowconfigure(0, weight=1)
    cadre.columnconfigure(0, weight=1)

    # Afficher les prédictions les plus récentes en premier.
    for prediction in reversed(predictions):
        try:
            valeurs = (
                prediction["Date"],
                prediction["Age"],
                prediction["Sexe"],
                convertir_temps(float(prediction["5K"])),
                convertir_temps(float(prediction["10K"])),
                convertir_temps(float(prediction["15K"])),
                convertir_temps(float(prediction["HALF"])),
                convertir_temps(float(prediction["Prediction"]))
            )
        except (KeyError, ValueError, TypeError):
            continue

        tableau.insert("", "end", values=valeurs)

    if not predictions:
        ttk.Label(
            fenetre,
            text="Aucune prédiction enregistrée pour le moment."
        ).pack(pady=10)
