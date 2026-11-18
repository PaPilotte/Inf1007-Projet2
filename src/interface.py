
"""Interface graphique de Marathon Predictor."""

import json
import math
import tkinter as tk
from tkinter import ttk, messagebox

from src.donnees import VariableNumerique, VariableCategorielle
from src.exceptions import DonneeInvalideError
from src.modele import Modele, CHEMIN_MODELE, CHEMIN_METADONNEES


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
    """Calcule l'allure moyenne prévue sur 42,195 km."""
    secondes_par_km = round(secondes / 42.195)

    minutes = secondes_par_km // 60
    secondes_restantes = secondes_par_km % 60

    return f"{minutes}:{secondes_restantes:02d}/km"


def lire_chrono(distance: str, champs_temps: dict) -> int:
    """Lit les heures, minutes et secondes d'un chrono."""
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
    """Vérifie que les temps de passage sont positifs et croissants."""
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


class Application:
    """Application Tkinter utilisant un modèle et des variables validées."""

    def __init__(self) -> None:
        """Charge le modèle, les métadonnées et construit la fenêtre."""
        self._fenetre = tk.Tk()
        self._fenetre.title("Marathon Predictor")

        # Fenêtre maximisée sur Windows
        try:
            self._fenetre.state("zoomed")
        except tk.TclError:
            self._fenetre.geometry("1100x750")

        self._fenetre.resizable(True, True)

        # Adaptation des dimensions à la résolution de l'écran
        largeur = self._fenetre.winfo_screenwidth()
        hauteur = self._fenetre.winfo_screenheight()

        self._echelle = min(
            largeur / 1400,
            hauteur / 850
        )

        self._echelle = max(0.80, min(self._echelle, 1.35))

        self._modele = None
        self._variables = {}
        self._champs_temps = {}

        self._charger_modele()
        self._construire_interface()

    def _taille(self, valeur: int) -> int:
        """Adapte une dimension à la résolution de l'écran."""
        return round(valeur * self._echelle)

    def _charger_modele(self) -> None:
        """Charge le modèle et prépare les objets de validation."""
        self._modele = Modele.charger(CHEMIN_MODELE)

        with open(CHEMIN_METADONNEES, "r", encoding="utf-8") as fichier:
            metadonnees = json.load(fichier)

        self._intervalles = metadonnees["intervalles"]
        self._categories = metadonnees["categories"]["M/F"]

        minimum_age, maximum_age = self._intervalles["Age"]

        self._variables["Age"] = VariableNumerique(
            "Age", minimum_age, maximum_age
        )

        self._variables["M/F"] = VariableCategorielle(
            "M/F", self._categories
        )

        for distance in DISTANCES:
            self._variables[distance] = VariableNumerique(
                distance, 0, 35999
            )

    def _construire_interface(self) -> None:
        """Construit une interface agrandie et centrée."""

        # Polices adaptées à la résolution
        police_titre = ("Arial", self._taille(30), "bold")
        police_sous_titre = ("Arial", self._taille(14))
        police_champs = ("Arial", self._taille(16))
        police_entetes = ("Arial", self._taille(13), "bold")
        police_bouton = ("Arial", self._taille(17), "bold")
        police_resultat = ("Arial", self._taille(23), "bold")
        police_allure = ("Arial", self._taille(16))

        # Cadre principal centré verticalement et horizontalement
        contenu = ttk.Frame(self._fenetre)

        contenu.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        # Titre
        ttk.Label(
            contenu,
            text="Marathon Predictor",
            font=police_titre
        ).pack(pady=(0, self._taille(12)))

        # Sous-titre
        ttk.Label(
            contenu,
            text=(
                "Prédisez votre temps au marathon "
                "en remplissant les champs ci-dessous."
            ),
            font=police_sous_titre
        ).pack(pady=(0, self._taille(30)))

        # Formulaire
        formulaire = ttk.Frame(contenu)
        formulaire.pack()

        # Âge
        ttk.Label(
            formulaire,
            text="Âge :",
            font=police_champs
        ).grid(
            row=0,
            column=0,
            padx=self._taille(15),
            pady=self._taille(12),
            sticky="e"
        )

        minimum_age, maximum_age = self._intervalles["Age"]

        ages = list(range(
            math.ceil(minimum_age),
            math.floor(maximum_age) + 1
        ))

        self._champ_age = ttk.Combobox(
            formulaire,
            values=ages,
            state="readonly",
            width=16,
            font=police_champs
        )

        if ages:
            self._champ_age.set(
                25 if 25 in ages else ages[0]
            )

        self._champ_age.grid(
            row=0,
            column=1,
            columnspan=3,
            padx=self._taille(10),
            pady=self._taille(12),
            sticky="w"
        )

        # Sexe
        ttk.Label(
            formulaire,
            text="Sexe :",
            font=police_champs
        ).grid(
            row=1,
            column=0,
            padx=self._taille(15),
            pady=self._taille(12),
            sticky="e"
        )

        self._champ_sexe = ttk.Combobox(
            formulaire,
            values=self._categories,
            state="readonly",
            width=16,
            font=police_champs
        )

        self._champ_sexe.grid(
            row=1,
            column=1,
            columnspan=3,
            padx=self._taille(10),
            pady=self._taille(12),
            sticky="w"
        )

        # Police des menus déroulants
        self._fenetre.option_add(
            "*TCombobox*Listbox.font",
            police_champs
        )

        # En-têtes des chronos
        for colonne, titre in enumerate(
            ("Heures", "Minutes", "Secondes"), start=1
        ):
            ttk.Label(
                formulaire,
                text=titre,
                font=police_entetes
            ).grid(
                row=2,
                column=colonne,
                padx=self._taille(10),
                pady=(self._taille(22), self._taille(8))
            )

        # Champs des chronos
        for ligne, distance in enumerate(DISTANCES, start=3):

            nom = NOMS_DISTANCES[distance]

            ttk.Label(
                formulaire,
                text=f"{nom.capitalize()} :",
                font=police_champs
            ).grid(
                row=ligne,
                column=0,
                padx=self._taille(15),
                pady=self._taille(13),
                sticky="e"
            )

            champs = {}

            for colonne, (cle, maximum) in enumerate(
                (
                    ("heures", 9),
                    ("minutes", 59),
                    ("secondes", 59)
                ),
                start=1
            ):
                champ = ttk.Spinbox(
                    formulaire,
                    from_=0,
                    to=maximum,
                    width=5,
                    format="%02.0f",
                    font=police_champs
                )

                champ.set("00")

                champ.grid(
                    row=ligne,
                    column=colonne,
                    padx=self._taille(9),
                    pady=self._taille(13)
                )

                champs[cle] = champ

            self._champs_temps[distance] = champs

        # Bouton de prédiction
        self._bouton_predire = tk.Button(
            contenu,
            text="Prédire mon marathon",
            command=self.predire_marathon,
            font=police_bouton,
            bg="#2563EB",
            fg="white",
            activebackground="#1D4ED8",
            activeforeground="white",
            padx=self._taille(28),
            pady=self._taille(15),
            cursor="hand2",
            relief="flat"
        )

        self._bouton_predire.pack(
            pady=(self._taille(35), self._taille(20))
        )

        # Temps prédit
        self._resultat = ttk.Label(
            contenu,
            text="",
            font=police_resultat
        )

        self._resultat.pack(
            pady=(self._taille(8), self._taille(8))
        )

        # Allure moyenne
        self._allure_resultat = ttk.Label(
            contenu,
            text="",
            font=police_allure
        )

        self._allure_resultat.pack(
            pady=(0, self._taille(10))
        )

    def _lire_caracteristiques(self) -> dict:
        """Lit et valide les caractéristiques du coureur."""
        saisies = {
            "Age": self._champ_age.get(),
            "M/F": self._champ_sexe.get()
        }

        for distance in DISTANCES:
            saisies[distance] = lire_chrono(
                distance, self._champs_temps
            )

        caracteristiques = {}

        # Polymorphisme
        for nom, variable in self._variables.items():
            caracteristiques[nom] = variable.valider(
                saisies[nom]
            )

        valider_chronos(caracteristiques)

        return caracteristiques

    def predire_marathon(self) -> None:
        """Prédit le marathon et affiche le temps et l'allure."""
        try:
            caracteristiques = self._lire_caracteristiques()

            prediction = self._modele.predire(
                caracteristiques
            )

            if (
                not math.isfinite(prediction)
                or prediction <= caracteristiques["HALF"]
            ):
                raise DonneeInvalideError(
                    "La prédiction est incohérente avec "
                    "le temps au demi-marathon."
                )

            self._resultat.config(
                text=f"Temps prédit : {convertir_temps(prediction)}"
            )

            self._allure_resultat.config(
                text=f"Allure moyenne : {calculer_allure(prediction)}"
            )

        except (DonneeInvalideError, ValueError, TypeError) as erreur:
            self._resultat.config(text="")
            self._allure_resultat.config(text="")

            messagebox.showerror(
                "Erreur de saisie",
                str(erreur)
            )

    def demarrer(self) -> None:
        """Démarre l'application Tkinter."""
        self._fenetre.mainloop()


def main() -> None:
    """Lance Marathon Predictor."""
    try:
        application = Application()

    except (
        FileNotFoundError,
        OSError,
        ValueError,
        KeyError,
        json.JSONDecodeError
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
