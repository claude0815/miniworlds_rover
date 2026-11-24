"""Startet das Szenario wie ``python main.py`` (unsichtbares Fenster).

* ``python tests/desktop_ablauf.py fahren``: Der Rover fährt in act() bis vor den
  Hügel; dabei wird zwischendurch gezeichnet (warte() = Greenfoot.delay).
* ``python tests/desktop_ablauf.py schliessen``: Der Rover steht vor dem Rand und
  act() läuft endlos; das Schließen des Fensters beendet das Programm trotzdem.
"""

import os
import sys
import threading

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
PROJEKT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJEKT)
os.chdir(PROJEKT)

import pygame  # noqa: E402

from classes import Feldakteur  # noqa: E402
from classes.Gestein import Gestein  # noqa: E402
from classes.Huegel import Huegel  # noqa: E402
from classes.Planet import Planet  # noqa: E402
from classes.Rover import Rover  # noqa: E402

modus = sys.argv[1]


class SchnellerPlanet(Planet):
    def on_setup(self):
        super().on_setup()
        Feldakteur.setzeGeschwindigkeit(75)


welt = SchnellerPlanet()
rover = Rover((75, 175))
Gestein((175, 175))
Huegel((375, 175))
gezeichnet = []
original_refresh = welt.refresh


def refresh():
    gezeichnet.append(rover.spalte)
    original_refresh()


welt.refresh = refresh

if modus == "schliessen":
    rover.direction = 0  # nach oben in Zeile 3: fährt bis Zeile 1, dann endlos "Ich kann mich nicht bewegen"
    threading.Timer(1.5, lambda: pygame.event.post(pygame.event.Event(pygame.QUIT))).start()


@welt.register
def act(self):
    if self.frame > 2 and modus == "fahren":
        assert (rover.spalte, rover.zeile) == (6, 3), (rover.spalte, rover.zeile)
        assert not [a for a in welt.actors if isinstance(a, Gestein)]
        assert {2, 3, 4, 5, 6} <= set(gezeichnet), gezeichnet  # Zwischenstände wurden gezeichnet
        print("OK")
        welt.quit(0)


welt.run()
