"""warte() (Greenfoot.delay) am Desktop und im Browser-Editor (Pyodide wird nachgestellt)."""

import asyncio
import sys
import types

import pytest

from classes import Feldakteur
from classes.Feldakteur import Endlosschleife
from classes.Huegel import Huegel
from classes.Rover import Rover


def mitte(spalte, zeile):
    return (spalte * 50 + 25, zeile * 50 + 25)


@pytest.fixture
def schnell(monkeypatch):
    monkeypatch.setattr(Feldakteur, "GRENZE_OHNE_PAUSE", 0.3)
    Feldakteur.setzeGeschwindigkeit(100)
    yield
    Feldakteur.setzeGeschwindigkeit(20)


@pytest.fixture
def browser(monkeypatch, planet):
    """Stellt den Editor nach: Pyodide, Welt läuft (frame > 0), refresh wird mitgezählt."""
    ffi = types.SimpleNamespace(can_run_sync=lambda: False, run_sync=None)
    monkeypatch.setitem(sys.modules, "pyodide", types.SimpleNamespace(ffi=ffi))
    monkeypatch.setitem(sys.modules, "pyodide.ffi", ffi)
    monkeypatch.setattr(sys, "platform", "emscripten")
    monkeypatch.setattr(planet, "frame", 5)
    gezeichnet = []
    monkeypatch.setattr(planet, "refresh", lambda: gezeichnet.append(1))
    ffi.gezeichnet = gezeichnet
    return ffi


def test_endlosschleife_wird_abgebrochen(planet, schnell):
    """Kein Hügel vor dem Rover: act() endet nie – warte() bricht mit Hinweis ab."""
    rover = Rover(mitte(1, 3), world=planet)
    with pytest.raises(Endlosschleife, match="kein Hügel"):
        rover.act()
    assert rover.spalte == 15


def test_browser_methodenaufruf_ohne_pause(planet, schnell, browser):
    """Rechtsklick im Editor: Python kann nicht warten, act() läuft ohne Pause durch."""
    rover = Rover(mitte(1, 3), world=planet)
    Huegel(mitte(6, 3), world=planet)
    rover.act()
    assert rover.spalte == 5
    assert browser.gezeichnet == []  # Zeichnen wäre ohne Pause sinnlos


def test_browser_endlosschleife_beendet_den_aufruf(planet, schnell, browser):
    rover = Rover(mitte(1, 3), world=planet)
    with pytest.raises(Endlosschleife):
        rover.act()


def test_browser_mit_jspi_zeichnet_und_wartet(planet, schnell, browser):
    pausen = []

    def run_sync(coroutine):
        coroutine.close()
        pausen.append(1)

    browser.can_run_sync = lambda: True
    browser.run_sync = run_sync
    rover = Rover(mitte(1, 3), world=planet)
    Huegel(mitte(6, 3), world=planet)
    rover.act()
    assert rover.spalte == 5
    assert len(pausen) == len(browser.gezeichnet) > 4


def test_browser_mit_jspi_stopp_beendet_act(planet, schnell, browser):
    """Stopp im Editor bricht die Aufgabe ab; warte() beendet act() dann sauber."""
    rover = Rover(mitte(1, 3), world=planet)  # kein Hügel: würde endlos laufen

    async def programm():
        aufgabe = asyncio.current_task()
        pausen = []

        def run_sync(coroutine):
            coroutine.close()
            pausen.append(1)
            if len(pausen) == 3:
                aufgabe.cancel()  # Editor: Stopp gedrückt

        browser.can_run_sync = lambda: True
        browser.run_sync = run_sync
        rover.act()

    with pytest.raises(asyncio.CancelledError):
        asyncio.run(programm())
