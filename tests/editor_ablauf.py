"""Bedient das Szenario über dieselbe Schnittstelle wie der Editor (miniworlds ScenarioHost).

Der Editor schickt Befehle wie ``place``, ``move``, ``call`` oder ``act`` als
JSON an ``ScenarioHost.dispatch``. Dieses Skript tut dasselbe – ohne Browser,
mit unsichtbarem Fenster. Aufruf: ``python tests/editor_ablauf.py [bildordner]``.
"""

import json
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
PROJEKT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJEKT)
os.chdir(PROJEKT)

import pygame  # noqa: E402
from miniworlds.base import runtime_host  # noqa: E402
from miniworlds.tools.scenario_host import ScenarioHost  # noqa: E402

from classes import Feldakteur  # noqa: E402
from classes.Planet import Planet  # noqa: E402

BILDER = sys.argv[1] if len(sys.argv) > 1 else None
merke = {}


def befehl(name, *argumente):
    antwort = json.loads(host.dispatch(name, json.dumps(list(argumente))))
    if not antwort["ok"]:
        raise AssertionError(f"{name}{argumente}: {antwort['error']}")
    return antwort["value"]


def objekt(name):
    for eintrag in befehl("snapshot")["actors"]:
        if eintrag["handle"] == merke[name]:
            return eintrag
    return None


def feld(name):
    eintrag = objekt(name)
    return (int(eintrag["x"] // 50), int(eintrag["y"] // 50))


def pruefe(bedingung, text):
    if not bedingung:
        raise AssertionError(text)


def foto(name):
    if BILDER:
        pygame.image.save(pygame.display.get_surface(), os.path.join(BILDER, name))


def platziere(name, klasse, x, y):
    merke[name] = befehl("place", klasse, x, y)


class Warte:
    """Ein Schritt, der in jedem Bild erneut geprüft wird, bis die Bedingung erfüllt ist."""

    def __init__(self, bedingung):
        self.bedingung = bedingung


schritte = [
    lambda: pruefe(
        {"Planet", "Rover", "Gestein", "Huegel", "Marke"} <= {k["name"] for k in befehl("classes")},
        "Klassen fehlen",
    ),
    # Klicks irgendwo in ein Feld: Objekte rasten in der Feldmitte ein
    lambda: platziere("rover", "Rover", 112, 160),
    lambda: pruefe((objekt("rover")["x"], objekt("rover")["y"]) == (125, 175), f"Rover: {objekt('rover')}"),
    lambda: platziere("gestein", "Gestein", 230, 199),
    lambda: platziere("marke", "Marke", 290, 152),
    lambda: platziere("huegel", "Huegel", 420, 180),
    lambda: befehl("move", merke["huegel"], 381, 160),  # Hügel ein Feld nach links ziehen
    lambda: pruefe(feld("huegel") == (7, 3), f"Hügel auf {feld('huegel')}"),
    lambda: platziere("rover_oben", "Rover", 600, 20),  # Zeile 0 ist für das Display reserviert
    lambda: befehl("delete", merke["rover_oben"]),
    lambda: pruefe(befehl("pick", 130, 170) == merke["rover"], "Rechtsklick findet den Rover nicht"),
    lambda: pruefe(
        {"act", "fahre", "drehe", "gesteinVorhanden", "huegelVorhanden", "nimmGestein", "setzeMarke",
         "markeVorhanden", "entferneMarke"} <= {m["name"] for m in befehl("methods", merke["rover"])},
        "Methoden fehlen im Kontextmenü",
    ),
    lambda: foto("01_platziert.png"),
    # Methoden aufrufen wie per Rechtsklick
    lambda: befehl("call", merke["rover"], "drehe", ['"rechts"']),
    lambda: pruefe(objekt("rover")["direction"] % 360 == 180, "drehe('rechts')"),
    lambda: befehl("call", merke["rover"], "drehe", ["links"]),
    lambda: pruefe(objekt("rover")["direction"] % 360 == 90, "drehe('links')"),
    lambda: pruefe(
        befehl("call", merke["rover"], "huegelVorhanden", ['"vorne"'])["result"] == "False", "huegelVorhanden"
    ),
    lambda: befehl("call", merke["rover"], "fahre", []),
    lambda: pruefe(feld("rover") == (3, 3), f"fahre(): Rover auf {feld('rover')}"),
    lambda: pruefe(
        befehl("call", merke["rover"], "gesteinVorhanden", [])["result"] == "False", "gesteinVorhanden"
    ),
    lambda: pruefe("anzeige" in befehl("inspect", merke["rover"])["fields"], "Inspektor zeigt anzeige nicht"),
    # Act: der Rover fährt in seiner while-Schleife bis vor den Hügel
    lambda: Feldakteur.setzeGeschwindigkeit(70),
    lambda: befehl("act", 1),
    Warte(lambda: feld("rover") == (6, 3)),
    lambda: pruefe(objekt("gestein") is None, "Gestein wurde nicht aufgenommen"),
    lambda: pruefe(objekt("marke") is not None, "Marke darf nicht verschwinden"),
    lambda: foto("02_nach_act.png"),
    lambda: pruefe("Rover((" in befehl("export_code"), "Code-Export ohne Rover"),
]


class Testhost(ScenarioHost):
    """Führt pro Bild einen Schritt aus (der Editor sendet seine Befehle ebenfalls zwischen den Bildern)."""

    nummer = 0
    versuche = 0

    def poll(self, app):
        if self.scenario is None:
            return
        if self.nummer >= len(schritte):
            print("OK")
            app.quit(0)
            return
        schritt = schritte[self.nummer]
        try:
            fertig = schritt.bedingung() if isinstance(schritt, Warte) else (schritt() or True)
        except Exception as fehler:  # noqa: BLE001
            print(f"Schritt {self.nummer} fehlgeschlagen: {fehler}")
            foto("fehler.png")
            app.quit(1)
            return
        if not fertig:
            self.versuche += 1
            if self.versuche > 600:
                print(f"Schritt {self.nummer}: Zeitüberschreitung")
                app.quit(1)
            return
        self.nummer += 1
        self.versuche = 0


host = Testhost()
host.bind_program(globals(), PROJEKT)
runtime_host.install(host)

welt = Planet()
welt.run()
