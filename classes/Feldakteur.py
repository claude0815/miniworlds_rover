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

    Manchmal kann Python nicht warten: beim Aufbau der Welt, bei einem
    Methodenaufruf per Rechtsklick im Editor und in Browsern ohne JSPI. Dann
    läuft das Programm ohne Pause weiter. Hört es nach GRENZE_OHNE_PAUSE Sekunden
    immer noch nicht auf (Endlosschleife), bricht warte() mit einer Fehlermeldung
    ab, statt das Programm hängen zu lassen.
    """
    welt = miniworlds.App.get_running_world()
    sekunden = schritte * verzoegerung() * BASIS_FPS / max(1, getattr(welt, "fps", BASIS_FPS))
    if welt is not None and welt.frame > 0 and _kann_pausieren():
        _ohne_pause["zuletzt"] = 0.0
        welt.refresh()
        if sys.platform == "emscripten":
            _pausiere_im_browser(sekunden)
        else:
            _pausiere_am_desktop(sekunden)
    else:
        _pruefe_endlosschleife()


#: So lange darf ein Programm ohne Pause in warte() kreisen, bevor es abgebrochen wird.
GRENZE_OHNE_PAUSE = 3.0
_ohne_pause = {"beginn": 0.0, "zuletzt": 0.0}


class Endlosschleife(RuntimeError):
    """Das Programm ruft warte() immer wieder auf, ohne fertig zu werden."""


def _pruefe_endlosschleife():
    jetzt = time.perf_counter()
    if jetzt - _ohne_pause["zuletzt"] > 0.25:  # neuer Aufruf: Zeitmessung beginnt von vorn
        _ohne_pause["beginn"] = jetzt
    _ohne_pause["zuletzt"] = jetzt
    if jetzt - _ohne_pause["beginn"] > GRENZE_OHNE_PAUSE:
        _ohne_pause["zuletzt"] = 0.0
        raise Endlosschleife(
            "Abgebrochen: Das Programm hört nicht auf (Endlosschleife?). "
            "Bei act() des Rovers heißt das meist: Vor dem Rover liegt in Fahrtrichtung kein Hügel, "
            "er steht am Rand und meldet immer wieder \"Ich kann mich nicht bewegen\". "
            "Tipp: act() mit \"Schritt\" oder \"Start\" ausführen – dann sieht man den Rover fahren."
        )


def _kann_pausieren() -> bool:
    if sys.platform != "emscripten":
        return True
    try:
        from pyodide.ffi import can_run_sync

        return bool(can_run_sync())
    except Exception:
        return False


def _pausiere_im_browser(sekunden: float):
    # Python wird angehalten (JSPI), der Browser zeichnet die Welt und der Editor
    # kann weiter Befehle schicken. In kurzen Stücken warten, damit "Stopp" sofort wirkt.
    from pyodide.ffi import run_sync

    ende = time.perf_counter() + sekunden
    while True:
        rest = ende - time.perf_counter()
        run_sync(asyncio.sleep(max(0.0, min(rest, 0.1))))
        try:
            aufgabe = asyncio.current_task()
        except RuntimeError:
            aufgabe = None
        if aufgabe is not None and aufgabe.cancelling():  # Stopp wurde gedrückt
            raise asyncio.CancelledError()
        if rest <= 0.1:
            return


def _pausiere_am_desktop(sekunden: float):
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
