import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

PROJEKT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJEKT not in sys.path:
    sys.path.insert(0, PROJEKT)

import pytest  # noqa: E402


@pytest.fixture(scope="session")
def _planet():
    # Nur eine Welt pro Prozess: miniworlds erkennt Berührungen im Kamerabereich
    # der laufenden Welt – wie im Editor gibt es deshalb genau einen Planeten.
    from classes.Planet import Planet

    welt = Planet()
    welt.on_setup()
    return welt


@pytest.fixture
def planet(_planet):
    """Ein leerer Planet (ohne Fenster-Hauptschleife)."""
    yield _planet
    for akteur in list(_planet.actors):
        akteur.remove()


@pytest.fixture
def meldungen(monkeypatch):
    """Alle Texte, die auf einem Rover-Display angezeigt werden."""
    from classes.Rover import Rover

    liste = []
    original = Rover.Display.anzeigen

    def anzeigen(self, text):
        liste.append(text)
        original(self, text)

    monkeypatch.setattr(Rover.Display, "anzeigen", anzeigen)
    return liste
