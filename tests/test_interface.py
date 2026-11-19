
"""Tests de l'interface Marathon Predictor, sans ouverture de fenêtres Tkinter."""

import csv
import json
from types import SimpleNamespace
from unittest.mock import Mock, mock_open

import pytest

import src.interface as interface
from src.donnees import VariableNumerique, VariableCategorielle
from src.exceptions import DonneeInvalideError
from src.interface import Application


@pytest.fixture
def caracteristiques():
    return {
        "Age": 25.0,
        "M/F": "M",
        "5K": 1500.0,
        "10K": 3000.0,
        "15K": 4500.0,
        "HALF": 6300.0,
    }


@pytest.fixture
def application(monkeypatch, caracteristiques):
    """Simule la logique de l'application sans construire l'interface."""
    app = object.__new__(Application)

    app._fenetre = object()
    app._modele = SimpleNamespace(predire=Mock(return_value=13000))
    app._historique = SimpleNamespace(
        ajouter=Mock(),
        consulter=Mock(return_value=[]),
    )

    app._resultat = SimpleNamespace(config=Mock())
    app._allure_resultat = SimpleNamespace(config=Mock())
    app._derniere_prediction = None
    app._dernieres_caracteristiques = None

    monkeypatch.setattr(
        app,
        "_lire_caracteristiques",
        Mock(return_value=caracteristiques.copy()),
    )

    monkeypatch.setattr(interface.messagebox, "showerror", Mock())
    monkeypatch.setattr(interface.messagebox, "showwarning", Mock())
    monkeypatch.setattr(interface.messagebox, "showinfo", Mock())

    return app


# --------------------------------------------------
# Tests des prédictions et interactions
# --------------------------------------------------

def test_prediction_valide(application, caracteristiques):
    application.predire_marathon()

    assert application._derniere_prediction == 13000
    assert application._dernieres_caracteristiques == caracteristiques

    application._modele.predire.assert_called_once()
    application._historique.ajouter.assert_called_once_with(
        caracteristiques, 13000
    )


def test_prediction_affiche_resultats(application):
    application.predire_marathon()

    application._resultat.config.assert_called_with(
        text="Temps prédit : 03:36:40"
    )

    application._allure_resultat.config.assert_called_with(
        text="Allure moyenne : 5:08/km"
    )


def test_prediction_saisie_invalide(application, monkeypatch):
    monkeypatch.setattr(
        application,
        "_lire_caracteristiques",
        Mock(side_effect=DonneeInvalideError("Chrono invalide")),
    )

    application.predire_marathon()

    interface.messagebox.showerror.assert_called_once()
    application._historique.ajouter.assert_not_called()

    assert application._derniere_prediction is None


def test_prediction_inferieure_au_demi(application):
    application._modele.predire.return_value = 6000

    application.predire_marathon()

    interface.messagebox.showerror.assert_called_once()
    application._historique.ajouter.assert_not_called()


@pytest.mark.parametrize("prediction", [float("nan"), float("inf")])
def test_prediction_non_finie(application, prediction):
    application._modele.predire.return_value = prediction

    application.predire_marathon()

    interface.messagebox.showerror.assert_called_once()
    application._historique.ajouter.assert_not_called()


def test_prediction_echec_historique(application):
    application._historique.ajouter.side_effect = OSError(
        "Accès refusé"
    )

    application.predire_marathon()

    assert application._derniere_prediction == 13000
    interface.messagebox.showwarning.assert_called_once()


def test_graphique_avant_prediction(application):
    application.voir_graphique()

    interface.messagebox.showinfo.assert_called_once()


def test_graphique_apres_prediction(application, monkeypatch):
    faux_graphique = Mock()

    monkeypatch.setattr(
        interface,
        "afficher_graphique_progression",
        faux_graphique,
    )

    application.predire_marathon()
    application.voir_graphique()

    faux_graphique.assert_called_once_with(
        application._fenetre,
        application._dernieres_caracteristiques,
        13000,
    )


def test_graphique_erreur_affichage(application, monkeypatch):
    monkeypatch.setattr(
        interface,
        "afficher_graphique_progression",
        Mock(side_effect=ValueError("Graphique invalide")),
    )

    application.predire_marathon()
    application.voir_graphique()

    interface.messagebox.showerror.assert_called_once()


def test_historique_affichage(application, monkeypatch):
    predictions = [{"Date": "2026-11-19", "Age": "25"}]

    application._historique.consulter.return_value = predictions

    faux_affichage = Mock()

    monkeypatch.setattr(
        interface,
        "afficher_historique",
        faux_affichage,
    )

    application.voir_historique()

    faux_affichage.assert_called_once_with(
        application._fenetre,
        predictions,
    )


def test_historique_erreur_lecture(application, monkeypatch):
    application._historique.consulter.side_effect = csv.Error(
        "CSV invalide"
    )

    faux_affichage = Mock()

    monkeypatch.setattr(
        interface,
        "afficher_historique",
        faux_affichage,
    )

    application.voir_historique()

    interface.messagebox.showerror.assert_called_once()
    faux_affichage.assert_not_called()


# --------------------------------------------------
# Tests de lecture et validation des champs
# --------------------------------------------------

@pytest.fixture
def application_avec_champs():
    """Simule les champs de saisie sans ouvrir Tkinter."""
    app = object.__new__(Application)

    app._champ_age = Mock()
    app._champ_age.get.return_value = "25"

    app._champ_sexe = Mock()
    app._champ_sexe.get.return_value = "M"

    chronos = {
        "5K": (0, 25, 0),
        "10K": (0, 50, 0),
        "15K": (1, 15, 0),
        "HALF": (1, 45, 0),
    }

    app._champs_temps = {}

    for distance, (heures, minutes, secondes) in chronos.items():
        app._champs_temps[distance] = {}

        for nom, valeur in zip(
            ("heures", "minutes", "secondes"),
            (heures, minutes, secondes),
        ):
            champ = Mock()
            champ.get.return_value = str(valeur)
            app._champs_temps[distance][nom] = champ

    app._variables = {
        "Age": VariableNumerique("Age", 18, 80),
        "M/F": VariableCategorielle("M/F", ["M", "F"]),
        **{
            distance: VariableNumerique(distance, 0, 35999)
            for distance in chronos
        },
    }

    return app


def test_lecture_caracteristiques_valides(application_avec_champs):
    resultat = application_avec_champs._lire_caracteristiques()

    assert resultat == {
        "Age": 25.0,
        "M/F": "M",
        "5K": 1500.0,
        "10K": 3000.0,
        "15K": 4500.0,
        "HALF": 6300.0,
    }


def test_lecture_age_trop_jeune(application_avec_champs):
    application_avec_champs._champ_age.get.return_value = "15"

    with pytest.raises(DonneeInvalideError):
        application_avec_champs._lire_caracteristiques()


def test_lecture_age_trop_eleve(application_avec_champs):
    application_avec_champs._champ_age.get.return_value = "100"

    with pytest.raises(DonneeInvalideError):
        application_avec_champs._lire_caracteristiques()


def test_lecture_sexe_non_selectionne(application_avec_champs):
    application_avec_champs._champ_sexe.get.return_value = ""

    with pytest.raises(DonneeInvalideError):
        application_avec_champs._lire_caracteristiques()


def test_lecture_chrono_non_numerique(application_avec_champs):
    application_avec_champs._champs_temps[
        "5K"
    ]["minutes"].get.return_value = "abc"

    with pytest.raises(DonneeInvalideError):
        application_avec_champs._lire_caracteristiques()


def test_lecture_chrono_zero(application_avec_champs):
    application_avec_champs._champs_temps[
        "5K"
    ]["minutes"].get.return_value = "0"

    with pytest.raises(DonneeInvalideError):
        application_avec_champs._lire_caracteristiques()


def test_lecture_chronos_non_croissants(application_avec_champs):
    application_avec_champs._champs_temps[
        "10K"
    ]["minutes"].get.return_value = "20"

    with pytest.raises(DonneeInvalideError):
        application_avec_champs._lire_caracteristiques()


def test_lecture_minutes_invalides(application_avec_champs):
    application_avec_champs._champs_temps[
        "HALF"
    ]["minutes"].get.return_value = "60"

    with pytest.raises(DonneeInvalideError):
        application_avec_champs._lire_caracteristiques()


# --------------------------------------------------
# Tests du chargement du modèle et du démarrage
# --------------------------------------------------

@pytest.fixture
def application_chargement():
    app = object.__new__(Application)
    app._variables = {}
    return app


@pytest.fixture
def metadonnees_exemples():
    return {
        "intervalles": {
            "Age": [18, 80],
            "5K": [900, 3000],
            "10K": [1900, 6000],
            "15K": [3000, 9000],
            "HALF": [4500, 13000],
        },
        "categories": {
            "M/F": ["M", "F"],
        },
    }


def test_chargement_modele_valide(
    application_chargement,
    metadonnees_exemples,
    monkeypatch,
):
    faux_modele = Mock()
    charger = Mock(return_value=faux_modele)

    monkeypatch.setattr(interface.Modele, "charger", charger)
    monkeypatch.setattr(
        "builtins.open",
        mock_open(read_data=json.dumps(metadonnees_exemples)),
    )

    application_chargement._charger_modele()

    assert application_chargement._modele is faux_modele
    assert application_chargement._categories == ["M", "F"]
    assert application_chargement._intervalles["Age"] == [18, 80]

    assert set(application_chargement._variables) == {
        "Age", "M/F", "5K", "10K", "15K", "HALF"
    }

    charger.assert_called_once_with(interface.CHEMIN_MODELE)


def test_chargement_variables_validees(
    application_chargement,
    metadonnees_exemples,
    monkeypatch,
):
    monkeypatch.setattr(interface.Modele, "charger", Mock())
    monkeypatch.setattr(
        "builtins.open",
        mock_open(read_data=json.dumps(metadonnees_exemples)),
    )

    application_chargement._charger_modele()

    variables = application_chargement._variables

    assert variables["Age"].valider(25) == 25.0
    assert variables["M/F"].valider("F") == "F"
    assert variables["5K"].valider(1500) == 1500.0

    with pytest.raises(DonneeInvalideError):
        variables["Age"].valider(100)

    with pytest.raises(DonneeInvalideError):
        variables["M/F"].valider("X")


def test_chargement_modele_inexistant(
    application_chargement,
    monkeypatch,
):
    monkeypatch.setattr(
        interface.Modele,
        "charger",
        Mock(side_effect=FileNotFoundError("Modèle absent")),
    )

    with pytest.raises(FileNotFoundError):
        application_chargement._charger_modele()


def test_chargement_metadonnees_incompletes(
    application_chargement,
    monkeypatch,
):
    monkeypatch.setattr(interface.Modele, "charger", Mock())
    monkeypatch.setattr(
        "builtins.open",
        mock_open(
            read_data=json.dumps({
                "categories": {"M/F": ["M", "F"]}
            })
        ),
    )

    with pytest.raises(KeyError):
        application_chargement._charger_modele()


@pytest.mark.parametrize(
    "echelle, valeur, resultat",
    [
        (1.0, 100, 100),
        (1.2, 100, 120),
        (0.8, 100, 80),
    ],
)
def test_adaptation_dimensions(echelle, valeur, resultat):
    app = object.__new__(Application)
    app._echelle = echelle

    assert app._taille(valeur) == resultat


def test_demarrage_application_reussie(monkeypatch):
    fausse_application = Mock()

    monkeypatch.setattr(
        interface,
        "Application",
        Mock(return_value=fausse_application),
    )

    interface.main()

    fausse_application.demarrer.assert_called_once()


@pytest.mark.parametrize(
    "erreur",
    [
        FileNotFoundError("Modèle absent"),
        KeyError("intervalles"),
    ],
)
def test_demarrage_erreur_chargement(monkeypatch, erreur):
    faux_message = Mock()

    monkeypatch.setattr(
        interface,
        "Application",
        Mock(side_effect=erreur),
    )
    monkeypatch.setattr(
        interface.messagebox,
        "showerror",
        faux_message,
    )

    interface.main()

    faux_message.assert_called_once()

    assert "Erreur de chargement" in faux_message.call_args.args[0]


# --------------------------------------------------
# Tests de l'initialisation de l'application
# --------------------------------------------------

@pytest.fixture
def initialisation_simulee(monkeypatch):
    fausse_fenetre = Mock()

    fausse_fenetre.winfo_screenwidth.return_value = 1400
    fausse_fenetre.winfo_screenheight.return_value = 850

    monkeypatch.setattr(
        interface.tk,
        "Tk",
        Mock(return_value=fausse_fenetre),
    )

    charger = Mock()
    construire = Mock()

    monkeypatch.setattr(
        Application,
        "_charger_modele",
        charger,
    )
    monkeypatch.setattr(
        Application,
        "_construire_interface",
        construire,
    )

    return {
        "fenetre": fausse_fenetre,
        "charger": charger,
        "construire": construire,
    }


def test_initialisation_application(initialisation_simulee):
    simulation = initialisation_simulee

    app = Application()

    assert app._fenetre is simulation["fenetre"]
    assert app._variables == {}
    assert app._champs_temps == {}
    assert app._derniere_prediction is None
    assert app._dernieres_caracteristiques is None

    simulation["charger"].assert_called_once()
    simulation["construire"].assert_called_once()


def test_initialisation_titre(initialisation_simulee):
    app = Application()

    app._fenetre.title.assert_called_once_with(
        "Marathon Predictor"
    )


def test_initialisation_fenetre_maximisee(initialisation_simulee):
    app = Application()

    app._fenetre.state.assert_called_once_with("zoomed")


def test_initialisation_fenetre_non_maximisee(
    initialisation_simulee,
):
    fenetre = initialisation_simulee["fenetre"]

    fenetre.state.side_effect = interface.tk.TclError(
        "Maximisation indisponible"
    )

    Application()

    fenetre.geometry.assert_called_once_with("1100x750")


@pytest.mark.parametrize(
    "largeur, hauteur, echelle_attendue",
    [
        (1400, 850, 1.0),
        (700, 425, 0.80),
        (2800, 1700, 1.35),
        (1400, 425, 0.80),
        (1680, 1020, 1.20),
    ],
)
def test_initialisation_echelle(
    initialisation_simulee,
    largeur,
    hauteur,
    echelle_attendue,
):
    fenetre = initialisation_simulee["fenetre"]

    fenetre.winfo_screenwidth.return_value = largeur
    fenetre.winfo_screenheight.return_value = hauteur

    app = Application()

    assert app._echelle == pytest.approx(echelle_attendue)


def test_demarrer_lance_boucle_tkinter():
    app = object.__new__(Application)
    app._fenetre = Mock()

    app.demarrer()

    app._fenetre.mainloop.assert_called_once()


# --------------------------------------------------
# Tests de construction de l'interface Tkinter
# --------------------------------------------------

@pytest.fixture
def construction_simulee(monkeypatch):
    """Simule les widgets sans ouvrir de fenêtre Tkinter."""
    app = object.__new__(Application)

    app._fenetre = Mock()
    app._echelle = 1.0
    app._intervalles = {"Age": [18, 80]}
    app._categories = ["M", "F"]
    app._champs_temps = {}

    # Normalement définies dans _construire_interface().
    # Nécessaires lorsqu'on teste les sous-méthodes directement.
    app._police_titre = ("Arial", 30, "bold")
    app._police_texte = ("Arial", 16)
    app._police_entetes = ("Arial", 13, "bold")

    widgets = {
        "frame": Mock(
            side_effect=lambda *args, **kwargs: Mock()
        ),
        "label": Mock(
            side_effect=lambda *args, **kwargs: Mock()
        ),
        "combobox": Mock(
            side_effect=lambda *args, **kwargs: Mock()
        ),
        "spinbox": Mock(
            side_effect=lambda *args, **kwargs: Mock()
        ),
        "bouton_ttk": Mock(
            side_effect=lambda *args, **kwargs: Mock()
        ),
        "bouton_tk": Mock(
            side_effect=lambda *args, **kwargs: Mock()
        ),
    }

    monkeypatch.setattr(interface.ttk, "Frame", widgets["frame"])
    monkeypatch.setattr(interface.ttk, "Label", widgets["label"])
    monkeypatch.setattr(interface.ttk, "Combobox", widgets["combobox"])
    monkeypatch.setattr(interface.ttk, "Spinbox", widgets["spinbox"])
    monkeypatch.setattr(interface.ttk, "Button", widgets["bouton_ttk"])
    monkeypatch.setattr(interface.tk, "Button", widgets["bouton_tk"])

    return app, widgets


def test_construction_interface_complete(construction_simulee):
    app, widgets = construction_simulee

    app._construire_interface()

    assert widgets["frame"].call_count == 2
    assert widgets["combobox"].call_count == 2
    assert widgets["spinbox"].call_count == 12
    assert widgets["bouton_tk"].call_count == 1
    assert widgets["bouton_ttk"].call_count == 2


def test_creation_menus_deroulants(construction_simulee):
    app, widgets = construction_simulee

    app._ajouter_selection(Mock())

    assert widgets["combobox"].call_count == 2
    assert app._champ_age is not app._champ_sexe

    appels = widgets["combobox"].call_args_list

    assert 18 in appels[0].kwargs["values"]
    assert 80 in appels[0].kwargs["values"]
    assert appels[1].kwargs["values"] == ["M", "F"]

    app._champ_age.set.assert_called_once_with(25)


def test_creation_champs_chronos(construction_simulee):
    app, widgets = construction_simulee

    app._ajouter_chronos(Mock())

    assert set(app._champs_temps) == {
        "5K", "10K", "15K", "HALF"
    }

    for champs in app._champs_temps.values():
        assert set(champs) == {
            "heures", "minutes", "secondes"
        }

        for champ in champs.values():
            champ.set.assert_called_once_with("00")

    assert widgets["spinbox"].call_count == 12


def test_limites_des_champs_chronos(construction_simulee):
    app, widgets = construction_simulee

    app._ajouter_chronos(Mock())

    appels = widgets["spinbox"].call_args_list

    for index in range(0, 12, 3):
        assert appels[index].kwargs["to"] == 9
        assert appels[index + 1].kwargs["to"] == 59
        assert appels[index + 2].kwargs["to"] == 59


def test_creation_boutons_resultats(construction_simulee):
    app, widgets = construction_simulee

    app._ajouter_resultats(Mock())

    bouton_prediction = widgets["bouton_tk"].call_args

    assert bouton_prediction.kwargs["command"] == app.predire_marathon

    appels = widgets["bouton_ttk"].call_args_list

    assert appels[0].kwargs["command"] == app.voir_graphique
    assert appels[1].kwargs["command"] == app.voir_historique

    assert appels[0].kwargs["text"] == (
        "Voir le graphique de progression"
    )
    assert appels[1].kwargs["text"] == "Voir l'historique"
