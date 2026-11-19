
"""Interface graphique principale de Marathon Predictor."""

import csv
import json
import math
import tkinter as tk
from tkinter import ttk, messagebox

from src.chronos import (
    DISTANCES,
    NOMS_DISTANCES,
    convertir_temps,
    calculer_allure,
    lire_chrono,
    valider_chronos
)
from src.donnees import VariableNumerique, VariableCategorielle
from src.exceptions import DonneeInvalideError
from src.fenetre_historique import afficher_historique
from src.historique import HistoriquePredictions
from src.modele import Modele, CHEMIN_MODELE, CHEMIN_METADONNEES
from src.graphiques import afficher_graphique_progression


class Application:
    """Application Tkinter de prédiction des temps au marathon."""

    def __init__(self) -> None:
        """Charge le modèle et construit l'interface."""
        self._fenetre = tk.Tk()
        self._fenetre.title("Marathon Predictor")

        try:
            self._fenetre.state("zoomed")
        except tk.TclError:
            self._fenetre.geometry("1100x750")

        largeur = self._fenetre.winfo_screenwidth()
        hauteur = self._fenetre.winfo_screenheight()

        self._echelle = min(largeur / 1400, hauteur / 850)
        self._echelle = max(0.80, min(self._echelle, 1.35))

        self._variables = {}
        self._champs_temps = {}
        self._historique = HistoriquePredictions()

        self._derniere_prediction = None
        self._dernieres_caracteristiques = None

        self._charger_modele()
        self._construire_interface()

    def _taille(self, valeur: int) -> int:
        """Adapte les dimensions à la résolution."""
        return round(valeur * self._echelle)

    def _charger_modele(self) -> None:
        """Charge le modèle et les métadonnées de validation."""
        self._modele = Modele.charger(CHEMIN_MODELE)

        with open(CHEMIN_METADONNEES, "r", encoding="utf-8") as fichier:
            metadonnees = json.load(fichier)

        self._intervalles = metadonnees["intervalles"]
        self._categories = metadonnees["categories"]["M/F"]

        minimum, maximum = self._intervalles["Age"]

        self._variables["Age"] = VariableNumerique(
            "Age", minimum, maximum
        )

        self._variables["M/F"] = VariableCategorielle(
            "M/F", self._categories
        )

        for distance in DISTANCES:
            self._variables[distance] = VariableNumerique(
                distance, 0, 35999
            )

    def _construire_interface(self) -> None:
        """Crée le formulaire et les boutons de l'application."""
        self._police_titre = ("Arial", self._taille(30), "bold")
        self._police_texte = ("Arial", self._taille(16))
        self._police_entetes = ("Arial", self._taille(13), "bold")

        contenu = ttk.Frame(self._fenetre)
        contenu.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(
            contenu,
            text="Marathon Predictor",
            font=self._police_titre
        ).pack(pady=(0, self._taille(12)))

        ttk.Label(
            contenu,
            text=(
                "Prédisez votre temps au marathon "
                "en remplissant les champs ci-dessous."
            ),
            font=("Arial", self._taille(14))
        ).pack(pady=(0, self._taille(30)))

        formulaire = ttk.Frame(contenu)
        formulaire.pack()

        self._ajouter_selection(formulaire)
        self._ajouter_chronos(formulaire)
        self._ajouter_resultats(contenu)

    def _ajouter_selection(self, formulaire: ttk.Frame) -> None:
        """Ajoute les menus déroulants pour l'âge et le sexe."""
        minimum, maximum = self._intervalles["Age"]
        ages = list(range(math.ceil(minimum), math.floor(maximum) + 1))

        selections = (
            ("Âge :", ages, 25 if 25 in ages else (ages[0] if ages else "")),
            ("Sexe :", self._categories, "")
        )

        for ligne, (titre, valeurs, defaut) in enumerate(selections):
            ttk.Label(
                formulaire,
                text=titre,
                font=self._police_texte
            ).grid(
                row=ligne, column=0,
                padx=self._taille(15),
                pady=self._taille(12),
                sticky="e"
            )

            champ = ttk.Combobox(
                formulaire,
                values=valeurs,
                state="readonly",
                width=16,
                font=self._police_texte
            )

            if defaut != "":
                champ.set(defaut)

            champ.grid(
                row=ligne,
                column=1,
                columnspan=3,
                padx=self._taille(10),
                pady=self._taille(12),
                sticky="w"
            )

            if ligne == 0:
                self._champ_age = champ
            else:
                self._champ_sexe = champ

        self._fenetre.option_add(
            "*TCombobox*Listbox.font",
            self._police_texte
        )

    def _ajouter_chronos(self, formulaire: ttk.Frame) -> None:
        """Ajoute les champs heures, minutes et secondes."""
        for colonne, titre in enumerate(
            ("Heures", "Minutes", "Secondes"), start=1
        ):
            ttk.Label(
                formulaire,
                text=titre,
                font=self._police_entetes
            ).grid(
                row=2,
                column=colonne,
                padx=self._taille(10),
                pady=(self._taille(22), self._taille(8))
            )

        for ligne, distance in enumerate(DISTANCES, start=3):
            ttk.Label(
                formulaire,
                text=f"{NOMS_DISTANCES[distance].capitalize()} :",
                font=self._police_texte
            ).grid(
                row=ligne,
                column=0,
                padx=self._taille(15),
                pady=self._taille(13),
                sticky="e"
            )

            champs = {}

            for colonne, (nom, maximum) in enumerate(
                (("heures", 9), ("minutes", 59), ("secondes", 59)),
                start=1
            ):
                champ = ttk.Spinbox(
                    formulaire,
                    from_=0,
                    to=maximum,
                    width=5,
                    format="%02.0f",
                    font=self._police_texte
                )

                champ.set("00")
                champ.grid(
                    row=ligne,
                    column=colonne,
                    padx=self._taille(9),
                    pady=self._taille(13)
                )

                champs[nom] = champ

            self._champs_temps[distance] = champs

    def _ajouter_resultats(self, contenu: ttk.Frame) -> None:
        """Ajoute les boutons et les champs de résultats."""
        tk.Button(
            contenu,
            text="Prédire mon marathon",
            command=self.predire_marathon,
            font=("Arial", self._taille(17), "bold"),
            bg="#2563EB",
            fg="white",
            activebackground="#1D4ED8",
            activeforeground="white",
            padx=self._taille(28),
            pady=self._taille(15),
            cursor="hand2",
            relief="flat"
        ).pack(pady=(self._taille(25), self._taille(12)))

        self._resultat = ttk.Label(
            contenu,
            text="",
            font=("Arial", self._taille(23), "bold")
        )
        self._resultat.pack(pady=(self._taille(5), self._taille(5)))

        self._allure_resultat = ttk.Label(
            contenu,
            text="",
            font=self._police_texte
        )
        self._allure_resultat.pack(pady=(0, self._taille(10)))

        ttk.Button(
            contenu,
            text="Voir le graphique de progression",
            command=self.voir_graphique
        ).pack(pady=(self._taille(8), 0))

        ttk.Button(
            contenu,
            text="Voir l'historique",
            command=self.voir_historique
        ).pack(pady=(self._taille(8), 0))

    def _lire_caracteristiques(self) -> dict:
        """Récupère et valide les données du coureur."""
        saisies = {
            "Age": self._champ_age.get(),
            "M/F": self._champ_sexe.get()
        }

        for distance in DISTANCES:
            saisies[distance] = lire_chrono(
                distance, self._champs_temps
            )

        caracteristiques = {}

        # Validation polymorphe des variables
        for nom, variable in self._variables.items():
            caracteristiques[nom] = variable.valider(saisies[nom])

        valider_chronos(caracteristiques)

        return caracteristiques

    def predire_marathon(self) -> None:
        """Calcule, affiche et enregistre une prédiction."""

        self._derniere_prediction = None
        self._dernieres_caracteristiques = None

        try:
            caracteristiques = self._lire_caracteristiques()
            prediction = self._modele.predire(caracteristiques)

            if (
                not math.isfinite(prediction)
                or prediction <= caracteristiques["HALF"]
            ):
                raise DonneeInvalideError(
                    "La prédiction est incohérente avec "
                    "le temps au demi-marathon."
                )

            self._derniere_prediction = prediction
            self._dernieres_caracteristiques = dict(caracteristiques)

            self._resultat.config(
                text=f"Temps prédit : {convertir_temps(prediction)}"
            )

            self._allure_resultat.config(
                text=f"Allure moyenne : {calculer_allure(prediction)}"
            )

        except (DonneeInvalideError, ValueError, TypeError) as erreur:
            self._resultat.config(text="")
            self._allure_resultat.config(text="")
            messagebox.showerror("Erreur de saisie", str(erreur))
            return

        try:
            self._historique.ajouter(caracteristiques, prediction)
        except (OSError, csv.Error) as erreur:
            messagebox.showwarning(
                "Historique",
                "La prédiction a été calculée, mais elle n'a "
                f"pas pu être enregistrée.\n\nDétails : {erreur}"
            )

    def voir_graphique(self) -> None:
        """Affiche le graphique de la dernière prédiction valide."""
        if (
            self._derniere_prediction is None
            or self._dernieres_caracteristiques is None
        ):
            messagebox.showinfo(
                "Graphique de progression",
                "Effectuez d'abord une prédiction valide."
            )
            return

        try:
            afficher_graphique_progression(
                self._fenetre,
                self._dernieres_caracteristiques,
                self._derniere_prediction
            )
        except (ImportError, KeyError, tk.TclError, TypeError, ValueError) as erreur:
            messagebox.showerror(
                "Graphique indisponible",
                "Impossible d'afficher le graphique.\n\n"
                f"Détails : {erreur}"
            )

    def voir_historique(self) -> None:
        """Ouvre la fenêtre des prédictions enregistrées."""
        try:
            predictions = self._historique.consulter()
        except (OSError, UnicodeError, csv.Error) as erreur:
            messagebox.showerror(
                "Erreur de l'historique",
                f"Impossible de lire l'historique.\n\n{erreur}"
            )
            return

        afficher_historique(self._fenetre, predictions)

    def demarrer(self) -> None:
        """Démarre la boucle principale de Tkinter."""
        self._fenetre.mainloop()


def main() -> None:
    """Lance Marathon Predictor."""
    try:
        application = Application()
    except (
        FileNotFoundError, OSError, ValueError,
        KeyError, json.JSONDecodeError
    ) as erreur:
        messagebox.showerror(
            "Erreur de chargement",
            "Impossible de charger le modèle ou ses métadonnées.\n\n"
            "Exécutez d'abord : python -m src.entrainement\n\n"
            f"Détails : {erreur}"
        )
        return

    application.demarrer()


if __name__ == "__main__":
    main()
