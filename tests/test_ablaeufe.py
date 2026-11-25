"""Komplette Abläufe in eigenen Prozessen (je ein unsichtbares Fenster)."""

import os
import subprocess
import sys

import pytest

TESTS = os.path.dirname(os.path.abspath(__file__))


def starte(skript, *argumente):
    umgebung = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
    ergebnis = subprocess.run(
        [sys.executable, "-W", "ignore", os.path.join(TESTS, skript), *argumente],
        capture_output=True,
        text=True,
        timeout=120,
        env=umgebung,
    )
    return ergebnis


def test_bedienung_wie_im_editor():
    """Platzieren, Verschieben, Methoden aufrufen, Act – über miniworlds' ScenarioHost wie im Editor."""
    ergebnis = starte("editor_ablauf.py")
    assert ergebnis.returncode == 0 and "OK" in ergebnis.stdout, ergebnis.stdout + ergebnis.stderr


@pytest.mark.parametrize("modus", ["fahren", "schliessen"])
def test_desktop(modus):
    ergebnis = starte("desktop_ablauf.py", modus)
    assert ergebnis.returncode == 0, ergebnis.stdout + ergebnis.stderr
    if modus == "fahren":
        assert "OK" in ergebnis.stdout
