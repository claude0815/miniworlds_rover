"""Verhalten von Rover, Gestein, Huegel und Marke – verglichen mit den Java-Klassen."""

import pytest

from classes.Feldakteur import ZELLENGROESSE
from classes.Gestein import Gestein
from classes.Huegel import Huegel
from classes.Marke import Marke
from classes.Rover import Rover

# Greenfoot-Rotation -> miniworlds-Richtung
RICHTUNG = {0: 90, 90: 180, 180: 270, 270: 0}

# Aus Rover.huegelVorhanden (Java): welche Zellenverschiebung wird geprüft?
JAVA_VERSATZ = {
    ("vorne", 0): (1, 0), ("rechts", 270): (1, 0), ("links", 90): (1, 0),
    ("vorne", 180): (-1, 0), ("rechts", 90): (-1, 0), ("links", 270): (-1, 0),
    ("vorne", 90): (0, 1), ("rechts", 0): (0, 1), ("links", 180): (0, 1),
    ("vorne", 270): (0, -1), ("rechts", 180): (0, -1), ("links", 0): (0, -1),
}


def mitte(f):
    """Pixel-Mitte des Feldes (spalte, zeile)."""
    return (f[0] * ZELLENGROESSE + 25, f[1] * ZELLENGROESSE + 25)


def feld(akteur):
    return (akteur.spalte, akteur.zeile)


def neu(klasse, planet, f):
    return klasse(mitte(f), world=planet)


def rover(planet, f, rotation=0):
    r = neu(Rover, planet, f)
    r.direction = RICHTUNG[rotation]
    return r


def anzahl(planet, klasse):
    return len([a for a in planet.actors if isinstance(a, klasse)])


def test_neuer_rover_meldet_sich_und_schaut_nach_rechts(planet, meldungen):
    r = neu(Rover, planet, (4, 5))
    assert feld(r) == (4, 5)
    assert r.direction == 90
    assert meldungen == ["Ich bin bereit"]
    assert isinstance(r.anzeige, Rover.Display)
    assert r.anzeige.center == (375, 25)  # Mitte von Feld (7, 0)
    assert tuple(r.anzeige.size) == (500, 50)


def test_objekte_rasten_auf_feldmitte_ein(planet):
    g = Gestein((112, 290), world=planet)
    assert g.center == (125, 275) and feld(g) == (2, 5)
    g.center = (149, 301)
    assert g.center == (125, 325)
    assert tuple(g.size) == (50, 50)


def test_rover_in_zeile_0_wird_in_zeile_1_gesetzt(planet):
    assert feld(neu(Rover, planet, (3, 0))) == (3, 1)


def test_fahre_ein_feld(planet, meldungen):
    r = rover(planet, (2, 2))
    r.fahre()
    assert feld(r) == (3, 2) and r.center == mitte((3, 2))
    assert meldungen == ["Ich bin bereit"]


@pytest.mark.parametrize("rotation, ziel", [(0, (6, 6)), (90, (5, 7)), (180, (4, 6)), (270, (5, 5))])
def test_fahre_in_alle_richtungen(planet, rotation, ziel):
    r = rover(planet, (5, 6), rotation)
    r.fahre()
    assert feld(r) == ziel


def test_fahre_gegen_huegel(planet, meldungen):
    r = rover(planet, (2, 2))
    neu(Huegel, planet, (3, 2))
    r.fahre()
    assert feld(r) == (2, 2)
    assert meldungen[1:] == ["Zu steil!"]


@pytest.mark.parametrize("start, rotation", [((15, 5), 0), ((0, 5), 180), ((5, 11), 90)])
def test_fahre_am_rand(planet, meldungen, start, rotation):
    r = rover(planet, start, rotation)
    r.fahre()
    assert feld(r) == start
    assert meldungen[1:] == ["Ich kann mich nicht bewegen"]


def test_fahre_nach_oben_in_zeile_1_meldet_zweimal(planet, meldungen):
    # Wie im Java-Original: Meldung im else-if-Zweig und in der Prüfung am Ende.
    r = rover(planet, (5, 1), 270)
    r.fahre()
    assert feld(r) == (5, 1)
    assert meldungen[1:] == ["Ich kann mich nicht bewegen", "Ich kann mich nicht bewegen"]


def test_drehe(planet, meldungen):
    r = rover(planet, (5, 5))
    r.drehe("rechts")
    assert r.direction % 360 == 180
    r.drehe("links")
    r.drehe("links")
    assert r.direction % 360 == 0
    r.drehe("oben")
    assert r.direction % 360 == 0
    assert meldungen[1:] == ["Befehl nicht korrekt!"]


@pytest.mark.parametrize("richtung, rotation", sorted(JAVA_VERSATZ))
def test_huegel_vorhanden_wie_in_java(planet, richtung, rotation):
    r = rover(planet, (6, 6), rotation)
    versatz = JAVA_VERSATZ[(richtung, rotation)]
    huegel = neu(Huegel, planet, (6 + versatz[0], 6 + versatz[1]))
    assert r.huegelVorhanden(richtung) is True
    huegel.remove()
    assert r.huegelVorhanden(richtung) is False
    # Hügel auf den anderen Nachbarfeldern und schräg daneben zählen nicht
    for anderer in {(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)} - {versatz}:
        neu(Huegel, planet, (6 + anderer[0], 6 + anderer[1]))
    assert r.huegelVorhanden(richtung) is False


def test_huegel_vorhanden_falscher_befehl(planet, meldungen):
    r = rover(planet, (6, 6))
    neu(Huegel, planet, (7, 6))
    assert r.huegelVorhanden("hinten") is False
    assert meldungen[1:] == ["Befehl nicht korrekt!"]


def test_huegel_vorhanden_am_rand(planet):
    assert rover(planet, (15, 3)).huegelVorhanden("vorne") is False


def test_gestein_vorhanden_und_nehmen(planet, meldungen):
    r = rover(planet, (3, 3))
    assert r.gesteinVorhanden() is False
    neu(Gestein, planet, (3, 3))
    neu(Gestein, planet, (3, 3))
    assert r.gesteinVorhanden() is True
    r.nimmGestein()  # entfernt genau ein Gestein (removeTouching)
    assert anzahl(planet, Gestein) == 1
    r.nimmGestein()
    assert r.gesteinVorhanden() is False
    r.nimmGestein()
    assert meldungen[1:] == [
        "Kein Gestein vorhanden!",
        "Gestein gefunden!",
        "Gestein gefunden!",
        "Gestein gefunden!",
        "Kein Gestein vorhanden!",
        "Kein Gestein vorhanden!",
        "Hier ist kein Gestein",
    ]


def test_gestein_auf_nachbarfeld_zaehlt_nicht(planet):
    r = rover(planet, (3, 3))
    for f in [(2, 3), (4, 3), (3, 2), (3, 4), (4, 4), (2, 2)]:
        neu(Gestein, planet, f)
    assert r.gesteinVorhanden() is False


def test_marken(planet, meldungen):
    r = rover(planet, (3, 3))
    assert r.markeVorhanden() is False
    r.setzeMarke()
    r.setzeMarke()
    marken = [a for a in planet.actors if isinstance(a, Marke)]
    assert len(marken) == 2 and all(feld(m) == (3, 3) for m in marken)
    assert r.markeVorhanden() is True
    r.entferneMarke()
    assert anzahl(planet, Marke) == 1
    r.entferneMarke()
    r.entferneMarke()
    assert r.markeVorhanden() is False
    assert meldungen[1:] == [
        "Keine Marke vorhanden!",
        "Marke gefunden!",
        "Marke gefunden!",
        "Marke gefunden!",
        "Keine Marke vorhanden!",
        "Keine Marke vorhanden!",
    ]


def test_marke_auf_nachbarfeld_zaehlt_nicht(planet):
    r = rover(planet, (3, 3))
    for f in [(2, 3), (4, 3), (3, 2), (3, 4)]:
        neu(Marke, planet, f)
    assert r.markeVorhanden() is False


def test_display_ausschalten(planet):
    r = rover(planet, (3, 3))
    r._displayAusschalten()
    assert r.anzeige not in planet.actors
    r.fahre()  # Meldungen gehen weiter an das (unsichtbare) Display
    r.drehe("x")
    assert feld(r) == (4, 3)


def test_display_zeigt_text_und_loescht(planet):
    r = rover(planet, (3, 3))
    assert len(r.anzeige.costume.images) == 2  # "Ich bin bereit" bleibt stehen
    r.anzeige.loeschen()
    assert len(r.anzeige.costume.images) == 1
    r.anzeige.anzeigen("Hallo")
    r.anzeige.anzeigen("Welt")
    assert len(r.anzeige.costume.images) == 2


def test_zeichenreihenfolge(planet):
    r = rover(planet, (3, 3))
    m = neu(Marke, planet, (3, 3))
    g = neu(Gestein, planet, (3, 3))
    h = neu(Huegel, planet, (4, 3))
    assert r.layer > m.layer > g.layer > h.layer > r.anzeige.layer


def test_gestein_ist_rot_oder_blau(planet):
    quellen = set()
    for _ in range(40):
        g = neu(Gestein, planet, (1, 1))
        quellen.add(g.costume.image_manager.images_list[0]["source"])
        g.remove()
    assert quellen == {"images/gesteinRot.png", "images/gesteinBlau.png"}


def test_act_faehrt_bis_zum_huegel_und_sammelt(planet, meldungen):
    r = rover(planet, (1, 4))
    neu(Gestein, planet, (3, 4))
    neu(Gestein, planet, (5, 4))
    neu(Gestein, planet, (5, 6))
    neu(Marke, planet, (4, 4))
    neu(Huegel, planet, (8, 4))
    r.act()
    assert feld(r) == (7, 4)
    assert [feld(a) for a in planet.actors if isinstance(a, Gestein)] == [(5, 6)]
    assert "Marke gefunden!" in meldungen
