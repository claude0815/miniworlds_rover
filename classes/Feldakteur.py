"""Bausteine aus Greenfoot, die miniworlds so nicht mitbringt.

* ``Feldakteur``: Ein Akteur, der immer genau auf einem Feld steht – wie in einer
  Greenfoot-Welt aus Zellen (``super(16, 12, 50)``).
* ``warte(n)``: entspricht ``Greenfoot.delay(n)``.
* ``setzeGeschwindigkeit(n)``: entspricht ``Greenfoot.setSpeed(n)``.
"""

import asyncio
import sys
import time

import miniworlds

#: Kantenlänge eines Feldes in Pixeln (zellenGroesse im Planet-Szenario)
ZELLENGROESSE = 50

#: Bildrate, auf die sich die Geschwindigkeit bezieht. Stellt der Editor die
#: Geschwindigkeit schneller oder langsamer (höhere/niedrigere fps), wartet
#: warte() entsprechend kürzer oder länger.
BASIS_FPS = 60

_geschwindigkeit = 50


class Feldakteur(miniworlds.Actor):
    """Ein Akteur, der immer in der Mitte eines Feldes steht.

    Wird das Objekt irgendwohin gesetzt – im Programm oder mit der Maus im
    Editor –, rastet es auf dem Feld ein, in dem dieser Punkt liegt.
    """

    @property
    def center(self):
        return miniworlds.Actor.center.fget(self)

    @center.setter
    def center(self, punkt):
        spalte = int(punkt[0] // ZELLENGROESSE)
        zeile = int(punkt[1] // ZELLENGROESSE)
        mitte = (spalte * ZELLENGROESSE + ZELLENGROESSE // 2, zeile * ZELLENGROESSE + ZELLENGROESSE // 2)
        miniworlds.Actor.center.fset(self, mitte)

    @property
    def spalte(self) -> int:
        """Nummer der Spalte, beginnend bei 0 (Greenfoot: getX())."""
        return int(self.center[0] // ZELLENGROESSE)

    @property
    def zeile(self) -> int:
        """Nummer der Zeile, beginnend bei 0 (Greenfoot: getY())."""
        return int(self.center[1] // ZELLENGROESSE)

    def setzeFeld(self, spalte: int, zeile: int):
        """Setzt das Objekt auf das Feld (spalte, zeile) (Greenfoot: setLocation(x, y))."""
        self.center = (spalte * ZELLENGROESSE + ZELLENGROESSE // 2, zeile * ZELLENGROESSE + ZELLENGROESSE // 2)


def setzeGeschwindigkeit(wert: int):
    """Wie Greenfoot.setSpeed(wert): 1 (sehr langsam) bis 100 (ohne Pause)."""
    global _geschwindigkeit
    _geschwindigkeit = max(1, min(100, int(wert)))


def verzoegerung() -> float:
    """Dauer eines Zeitschritts in Sekunden – dieselbe Formel wie in Greenfoot.

    Geschwindigkeit 50 ergibt etwa 1/60 Sekunde, Geschwindigkeit 20 (Planet) etwa 0,77 Sekunden.
    """
    if _geschwindigkeit >= 100:
        return 0.0
    kuerzeste, laengste = 30e-6, 10.0
    basis = (laengste / kuerzeste) ** (1 / 99)
    return basis ** (100 - _geschwindigkeit - 1) * kuerzeste


def warte(schritte: int = 1):
    """Wie Greenfoot.delay(schritte): Die Welt wird neu gezeichnet, dann wartet das Programm.

    So sieht man z. B. den Rover in einer while-Schleife Feld für Feld fahren.
    Solange die Welt noch nicht läuft (z. B. beim Aufbau in on_setup), passiert nichts.
    """
    welt = miniworlds.App.get_running_world()
    if welt is None or welt.frame == 0:
        return
    welt.refresh()
    _schlafe(schritte * verzoegerung() * BASIS_FPS / max(1, welt.fps))


def _schlafe(sekunden: float):
    if sekunden <= 0:
        return
    if sys.platform == "emscripten":
        # Im Browser (Pyodide) darf das Programm nicht einfach blockieren:
        # Python wird angehalten, bis die Zeit um ist; dabei zeichnet der Browser.
        # Geht das nicht (Browser ohne JSPI), läuft das Programm ohne Pause weiter.
        try:
            from pyodide.ffi import can_run_sync, run_sync

            if can_run_sync():
                run_sync(asyncio.sleep(sekunden))
        except Exception:
            pass
        return
    import pygame

    ende = time.perf_counter() + sekunden
    while True:
        try:
            if pygame.event.peek(pygame.QUIT):  # Fenster wurde geschlossen
                raise SystemExit(0)
        except pygame.error:
            pass
        rest = ende - time.perf_counter()
        if rest <= 0:
            return
        time.sleep(min(rest, 0.02))
