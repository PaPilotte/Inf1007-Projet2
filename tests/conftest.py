import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def donnees_marathon():
    """Crée 200 coureurs fictifs avec des temps cohérents."""
    generateur = np.random.default_rng(0)
    nombre = 200

    cinq_k = generateur.uniform(1100, 2000, nombre)
    # Les temps suivants sont proportionnels, avec un peu de bruit
    bruit = generateur.normal(0, 60, nombre)

    return pd.DataFrame({
        "Age": generateur.integers(20, 60, nombre),
        "M/F": generateur.choice(["M", "F"], nombre),
        "5K": cinq_k,
        "10K": cinq_k * 2.05,
        "15K": cinq_k * 3.10,
        "HALF": cinq_k * 4.40,
        "Finish Net": cinq_k * 8.90 + bruit,
    })


@pytest.fixture
def coureur_exemple():
    """Un coureur valide pour tester predire()."""
    return {
        "Age": 30,
        "M/F": "F",
        "5K": 1500,
        "10K": 3075,
        "15K": 4650,
        "HALF": 6600,
    }