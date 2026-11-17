import tkinter as tk
from tkinter import ttk, messagebox

from src.modele import Modele, CHEMIN_MODELE


def convertir_temps(secondes):
    """Convertit un nombre de secondes en HH:MM:SS."""
    secondes = round(secondes)

    heures = secondes // 3600
    minutes = (secondes % 3600) // 60
    secondes_restantes = secondes % 60

    return f"{heures:02d}:{minutes:02d}:{secondes_restantes:02d}"


def calculer_allure(secondes):
    """Calcule l'allure moyenne prévue sur 42,195 km."""
    secondes_par_km = round(secondes / 42.195)

    minutes = secondes_par_km // 60
    secondes_restantes = secondes_par_km % 60

    return f"{minutes}:{secondes_restantes:02d}/km"


def lire_chrono(distance, champs_temps):
    """Récupère les heures, minutes et secondes d'un chrono."""
    champs = champs_temps[distance]

    try:
        heures = int(champs["heures"].get())
        minutes = int(champs["minutes"].get())
        secondes = int(champs["secondes"].get())
    except ValueError as erreur:
        raise ValueError(
            f"Le chrono {distance} doit contenir uniquement des nombres."
        ) from erreur

    if not 0 <= heures <= 9:
        raise ValueError(
            f"Les heures du chrono {distance} doivent être entre 0 et 9."
        )

    if not 0 <= minutes <= 59 or not 0 <= secondes <= 59:
        raise ValueError(
            f"Les minutes et secondes du chrono {distance} doivent être entre 0 et 59."
        )

    return heures * 3600 + minutes * 60 + secondes


def main():
    """Crée et démarre l'interface graphique de Marathon Predictor."""

    # --------------------------------------------------
    # Fenêtre principale
    # --------------------------------------------------

    fenetre = tk.Tk()
    fenetre.title("Marathon Predictor")
    fenetre.geometry("650x620")
    fenetre.resizable(False, False)

    # Titre
    ttk.Label(
        fenetre,
        text="Marathon Predictor",
        font=("Arial", 20, "bold")
    ).pack(pady=(25, 10))

    # Sous-titre
    ttk.Label(
        fenetre,
        text="Prédisez votre temps au marathon grâce à l'intelligence artificielle."
    ).pack(pady=(0, 15))

    # --------------------------------------------------
    # Formulaire
    # --------------------------------------------------

    formulaire = ttk.Frame(fenetre, padding=15)
    formulaire.pack()

    # Âge : liste déroulante
    ttk.Label(
        formulaire,
        text="Âge :"
    ).grid(row=0, column=0, padx=10, pady=10, sticky="e")

    champ_age = ttk.Combobox(
        formulaire,
        values=list(range(1, 121)),
        state="readonly",
        width=17
    )
    champ_age.set("25")
    champ_age.grid(
        row=0, column=1, columnspan=3,
        padx=10, pady=10, sticky="w"
    )

    # Sexe : liste déroulante
    ttk.Label(
        formulaire,
        text="Sexe :"
    ).grid(row=1, column=0, padx=10, pady=10, sticky="e")

    champ_sexe = ttk.Combobox(
        formulaire,
        values=["M", "F"],
        state="readonly",
        width=17
    )
    champ_sexe.grid(
        row=1, column=1, columnspan=3,
        padx=10, pady=10, sticky="w"
    )

    # En-têtes des chronos
    for colonne, titre in enumerate(
        ("Heures", "Minutes", "Secondes"), start=1
    ):
        ttk.Label(
            formulaire,
            text=titre
        ).grid(
            row=2, column=colonne,
            padx=5, pady=(15, 5)
        )

    # Chronos avec trois Spinbox par distance
    champs_temps = {}

    distances = [
        ("5K", "5 km"),
        ("10K", "10 km"),
        ("15K", "15 km"),
        ("HALF", "Demi-marathon")
    ]

    for ligne, (distance, nom) in enumerate(distances, start=3):
        ttk.Label(
            formulaire,
            text=f"{nom} :"
        ).grid(
            row=ligne, column=0,
            padx=10, pady=10, sticky="e"
        )

        champs = {}

        for colonne, (cle, maximum) in enumerate(
            (("heures", 9), ("minutes", 59), ("secondes", 59)),
            start=1
        ):
            champ = ttk.Spinbox(
                formulaire,
                from_=0,
                to=maximum,
                width=6,
                format="%02.0f"
            )
            champ.set("00")
            champ.grid(
                row=ligne, column=colonne,
                padx=5, pady=10
            )

            champs[cle] = champ

        champs_temps[distance] = champs

    # --------------------------------------------------
    # Chargement du modèle entraîné
    # --------------------------------------------------

    try:
        modele = Modele.charger(CHEMIN_MODELE)

    except (FileNotFoundError, OSError, ValueError) as erreur:
        messagebox.showerror(
            "Modèle introuvable",
            "Impossible de charger le modèle entraîné.\n\n"
            "Exécutez : python -m src.entrainement\n\n"
            f"Détails : {erreur}"
        )
        fenetre.destroy()
        return

    # --------------------------------------------------
    # Fonction appelée par le bouton
    # --------------------------------------------------

    def predire_marathon():
        """Récupère les données saisies et affiche la prédiction."""
        try:
            caracteristiques = {
                "Age": int(champ_age.get()),
                "M/F": champ_sexe.get()
            }

            if caracteristiques["M/F"] not in ("M", "F"):
                raise ValueError("Veuillez sélectionner un sexe.")

            for distance in ("5K", "10K", "15K", "HALF"):
                caracteristiques[distance] = lire_chrono(
                    distance, champs_temps
                )

            # Vérification des temps de passage
            if not (
                0 < caracteristiques["5K"]
                < caracteristiques["10K"]
                < caracteristiques["15K"]
                < caracteristiques["HALF"]
            ):
                raise ValueError(
                    "Les temps de passage doivent être positifs et croissants."
                )

            # Prédiction avec le modèle entraîné
            prediction = modele.predire(caracteristiques)

            if prediction <= caracteristiques["HALF"]:
                raise ValueError(
                    "La prédiction est incohérente avec le temps au demi-marathon."
                )

            # Affichage du temps prédit et de l'allure
            resultat.config(
                text=f"Temps prédit : {convertir_temps(prediction)}"
            )

            allure_resultat.config(
                text=f"Allure moyenne : {calculer_allure(prediction)}"
            )

        except (ValueError, TypeError) as erreur:
            resultat.config(text="")
            allure_resultat.config(text="")
            messagebox.showerror("Erreur de saisie", str(erreur))

    # --------------------------------------------------
    # Bouton de prédiction
    # --------------------------------------------------

    bouton_predire = tk.Button(
        fenetre,
        text="Prédire mon marathon",
        command=predire_marathon,
        font=("Arial", 12, "bold"),
        bg="#2563EB",
        fg="white",
        activebackground="#1D4ED8",
        activeforeground="white",
        padx=20,
        pady=10,
        cursor="hand2",
        relief="flat"
    )
    bouton_predire.pack(pady=(20, 15))

    # --------------------------------------------------
    # Affichage des résultats
    # --------------------------------------------------

    resultat = ttk.Label(
        fenetre,
        text="",
        font=("Arial", 16, "bold")
    )
    resultat.pack(pady=(5, 5))

    allure_resultat = ttk.Label(
        fenetre,
        text="",
        font=("Arial", 12)
    )
    allure_resultat.pack(pady=(0, 10))

    # --------------------------------------------------
    # Démarrage de l'application
    # --------------------------------------------------

    fenetre.mainloop()


if __name__ == "__main__":
    main()
