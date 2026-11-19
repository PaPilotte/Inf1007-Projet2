import pytest
from matplotlib.figure import Figure

from src.graphiques import creer_figure_progression


@pytest.fixture
def caracteristiques():
    """Retourne des temps de passage fictifs et cohérents."""
    return {
        "Age": 25,
        "M/F": "M",
        "5K": 1500,
        "10K": 3000,
        "15K": 4500,
        "HALF": 6300
    }


def test_creer_figure():
    """Vérifie que le graphique est une figure Matplotlib."""
    donnees = {
        "5K": 1500,
        "10K": 3000,
        "15K": 4500,
        "HALF": 6300
    }

    figure = creer_figure_progression(donnees, 13000)

    assert isinstance(figure, Figure)


def test_graphique_contient_deux_courbes(caracteristiques):
    """Vérifie la présence des temps saisis et de la projection."""
    figure = creer_figure_progression(caracteristiques, 13000)

    axes = figure.axes[0]

    assert len(axes.lines) == 2


def test_distances_du_graphique(caracteristiques):
    """Vérifie les distances utilisées sur les deux courbes."""
    figure = creer_figure_progression(caracteristiques, 13000)

    axes = figure.axes[0]

    distances_saisies = list(axes.lines[0].get_xdata())
    distances_projection = list(axes.lines[1].get_xdata())

    assert distances_saisies == [5, 10, 15, 21.0975]
    assert distances_projection == [21.0975, 42.195]


def test_conversion_des_temps_en_minutes(caracteristiques):
    """Les temps doivent apparaître en minutes sur le graphique."""
    figure = creer_figure_progression(caracteristiques, 13000)

    axes = figure.axes[0]

    temps_saisis = list(axes.lines[0].get_ydata())
    temps_projection = list(axes.lines[1].get_ydata())

    assert temps_saisis == [25, 50, 75, 105]
    assert temps_projection == pytest.approx(
        [105, 13000 / 60]
    )


def test_graphique_possede_titre_et_axes(caracteristiques):
    """Vérifie que le graphique est compréhensible."""
    figure = creer_figure_progression(caracteristiques, 13000)

    axes = figure.axes[0]

    assert axes.get_title() != ""
    assert "Distance" in axes.get_xlabel()
    assert "Temps" in axes.get_ylabel()


def test_graphique_possede_legende(caracteristiques):
    """Vérifie la présence d'une légende."""
    figure = creer_figure_progression(caracteristiques, 13000)

    axes = figure.axes[0]

    legende = axes.get_legend()

    assert legende is not None
    assert len(legende.get_texts()) == 2


def test_graphique_temps_manquant(caracteristiques):
    """Vérifie qu'une distance manquante provoque une erreur."""
    del caracteristiques["10K"]

    with pytest.raises(KeyError):
        creer_figure_progression(caracteristiques, 13000)


def test_graphique_temps_non_numerique(caracteristiques):
    """Vérifie le refus d'un chrono non numérique."""
    caracteristiques["5K"] = "bonjour"

    with pytest.raises(ValueError):
        creer_figure_progression(caracteristiques, 13000)


def test_graphique_prediction_non_numerique(caracteristiques):
    """Vérifie le refus d'une prédiction non numérique."""
    with pytest.raises(ValueError):
        creer_figure_progression(caracteristiques, "invalide")


# --------------------------------------------------
# Tests de la fenêtre du graphique
# --------------------------------------------------

from unittest.mock import Mock
import src.graphiques as module_graphiques


@pytest.fixture
def graphique_simule(monkeypatch):
    """Simule les éléments Tkinter du graphique."""
    fenetre = Mock()
    conteneur = Mock()
    canvas = Mock()
    figure = Mock()

    monkeypatch.setattr(
        module_graphiques.tk,
        "Toplevel",
        Mock(return_value=fenetre)
    )

    monkeypatch.setattr(
        module_graphiques.ttk,
        "Frame",
        Mock(return_value=conteneur)
    )

    monkeypatch.setattr(
        module_graphiques,
        "FigureCanvasTkAgg",
        Mock(return_value=canvas)
    )

    monkeypatch.setattr(
        module_graphiques,
        "creer_figure_progression",
        Mock(return_value=figure)
    )

    return {
        "fenetre": fenetre,
        "conteneur": conteneur,
        "canvas": canvas,
        "figure": figure
    }


def test_ouverture_fenetre_graphique(
    graphique_simule, caracteristiques
):
    """Le graphique s'ouvre dans une fenêtre enfant."""
    parent = Mock()

    module_graphiques.afficher_graphique_progression(
        parent, caracteristiques, 13000
    )

    module_graphiques.tk.Toplevel.assert_called_once_with(
        parent
    )

    graphique_simule["fenetre"].title.assert_called_once_with(
        "Progression de la prédiction"
    )

    graphique_simule["fenetre"].geometry.assert_called_once_with(
        "760x520"
    )


def test_graphique_utilise_bonnes_donnees(
    graphique_simule, caracteristiques
):
    """La figure reçoit les données du coureur."""
    module_graphiques.afficher_graphique_progression(
        Mock(), caracteristiques, 13000
    )

    module_graphiques.creer_figure_progression.assert_called_once_with(
        caracteristiques, 13000
    )


def test_canvas_graphique_affiche(
    graphique_simule, caracteristiques
):
    """Le graphique est dessiné dans le canvas Tkinter."""
    module_graphiques.afficher_graphique_progression(
        Mock(), caracteristiques, 13000
    )

    canvas = graphique_simule["canvas"]

    module_graphiques.FigureCanvasTkAgg.assert_called_once_with(
        graphique_simule["figure"],
        master=graphique_simule["conteneur"]
    )

    canvas.draw.assert_called_once()
    canvas.get_tk_widget().pack.assert_called_once_with(
        fill="both", expand=True
    )


def test_fermeture_graphique_libere_ressources(
    graphique_simule, caracteristiques
):
    """Fermer le graphique détruit les widgets et libère la figure."""
    module_graphiques.afficher_graphique_progression(
        Mock(), caracteristiques, 13000
    )

    fenetre = graphique_simule["fenetre"]
    canvas = graphique_simule["canvas"]
    figure = graphique_simule["figure"]

    # Récupérer la fonction associée au bouton de fermeture.
    appel = fenetre.protocol.call_args

    assert appel.args[0] == "WM_DELETE_WINDOW"

    fonction_fermeture = appel.args[1]

    # Simuler un clic sur le bouton de fermeture.
    fonction_fermeture()

    canvas.get_tk_widget().destroy.assert_called_once()
    figure.clear.assert_called_once()
    fenetre.destroy.assert_called_once()


def test_destruction_fenetre_libere_figure(
    graphique_simule, caracteristiques
):
    """La destruction de la fenêtre libère la figure."""
    module_graphiques.afficher_graphique_progression(
        Mock(), caracteristiques, 13000
    )

    fenetre = graphique_simule["fenetre"]
    figure = graphique_simule["figure"]

    # Récupérer la fonction associée à l'événement Destroy.
    appel = fenetre.bind.call_args

    assert appel.args[0] == "<Destroy>"

    fonction_destruction = appel.args[1]

    evenement = Mock()
    evenement.widget = fenetre

    fonction_destruction(evenement)

    figure.clear.assert_called_once()


def test_destruction_autre_widget_ne_libere_pas_figure(
    graphique_simule, caracteristiques
):
    """Détruire un widget enfant ne doit pas libérer la figure."""
    module_graphiques.afficher_graphique_progression(
        Mock(), caracteristiques, 13000
    )

    fenetre = graphique_simule["fenetre"]
    figure = graphique_simule["figure"]

    fonction_destruction = fenetre.bind.call_args.args[1]

    evenement = Mock()
    evenement.widget = Mock()

    fonction_destruction(evenement)

    figure.clear.assert_not_called()
