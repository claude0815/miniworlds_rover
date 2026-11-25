import os

import miniworlds
import pygame

from classes.Feldakteur import ZELLENGROESSE, Feldakteur, warte
from classes.Gestein import Gestein
from classes.Huegel import Huegel
from classes.Marke import Marke


class Rover(Feldakteur):
    """Der Rover erkundet den Planeten.

    Richtungen: In Greenfoot bedeutet Rotation 0 "nach rechts", 90 "nach unten"
    und 270 "nach oben". miniworlds zählt wie Scratch: direction 0 heißt
    "nach oben", 90 "nach rechts", 180 "nach unten" und -90 "nach links".
    """

    def act(self):
        """Die Anweisungen der Methode act werden ausgeführt, wenn der Act-Button
        im Hauptfenster geklickt wird."""
        while not self.huegelVorhanden("vorne"):
            self.fahre()
            if self.gesteinVorhanden():
                self.nimmGestein()
            self.markeVorhanden()

    def fahre(self):
        """Der Rover bewegt sich ein Feld in Fahrtrichtung weiter.
        Sollte sich in Fahrtrichtung ein Objekt der Klasse Huegel befinden oder er sich an der Grenze der Welt befinden,
        dann erscheint eine entsprechende Meldung auf dem Display."""
        posX = self.spalte
        posY = self.zeile

        if self.huegelVorhanden("vorne"):
            self._nachricht("Zu steil!")
        elif self.direction % 360 == 0 and self.zeile == 1:  # Greenfoot: getRotation() == 270
            self._nachricht("Ich kann mich nicht bewegen")
        else:
            # Wie move(1) in Greenfoot: Am Rand der Welt bleibt der Rover stehen.
            if self.world.is_in_world(self._mitteDesNachbarfelds(self.direction)):
                self.move(ZELLENGROESSE)
            warte(1)

        if posX == self.spalte and posY == self.zeile and not self.huegelVorhanden("vorne"):
            self._nachricht("Ich kann mich nicht bewegen")

    def drehe(self, richtung: str):
        """Der Rover dreht sich um 90 Grad in die Richtung, die mit richtung („links“ oder „rechts“) übergeben wurde.
        Sollte ein anderer Text (String) als "rechts" oder "links" übergeben werden, dann erscheint eine entsprechende Meldung auf dem Display."""
        if richtung == "rechts":
            self.turn_right(90)
        elif richtung == "links":
            self.turn_left(90)
        else:
            self._nachricht("Befehl nicht korrekt!")

    def gesteinVorhanden(self) -> bool:
        """Der Rover gibt durch einen Wahrheitswert (True oder False) zurück, ob sich auf seiner
        Position ein Objekt der Klasse Gestein befindet.
        Eine entsprechende Meldung erscheint auch auf dem Display."""
        if self.detect(Gestein) is not None:
            self._nachricht("Gestein gefunden!")
            return True

        self._nachricht("Kein Gestein vorhanden!")
        return False

    def huegelVorhanden(self, richtung: str) -> bool:
        """Der Rover überprüft, ob sich in richtung ("rechts", "links", oder "vorne") ein Objekt der Klasse Huegel befindet.
        Das Ergebnis wird auf dem Display angezeigt.
        Sollte ein anderer Text (String) als "rechts", "links" oder "vorne" übergeben werden, dann erscheint eine entsprechende Meldung auf dem Display."""
        if richtung == "vorne":
            blickrichtung = self.direction
        elif richtung == "rechts":
            blickrichtung = self.direction + 90
        elif richtung == "links":
            blickrichtung = self.direction - 90
        else:
            self._nachricht("Befehl nicht korrekt!")
            return False

        return self.detect_actor_at(blickrichtung, ZELLENGROESSE, Huegel) is not None

    def nimmGestein(self):
        """Der Rover nimmt das Gestein auf seiner Position auf.
        Sollte kein Objekt der Klasse Gestein vorhanden sein, dann erscheint
        eine entsprechende Meldung auf dem Display."""
        if self.gesteinVorhanden():
            warte(1)
            gestein = self.detect(Gestein)  # Greenfoot: removeTouching(Gestein.class)
            if gestein is not None:
                gestein.remove()
        else:
            self._nachricht("Hier ist kein Gestein")

    def setzeMarke(self):
        """Der Rover erzeugt ein Objekt der Klasse „Marke“ auf seiner Position."""
        Marke(self.center, world=self.world)

    def markeVorhanden(self) -> bool:
        """Der Rover gibt durch einen Wahrheitswert (True oder False) zurück,
        ob sich auf seiner Position ein Objekt der Marke befindet.
        Eine entsprechende Meldung erscheint auch auf dem Display."""
        if self.detect(Marke) is not None:
            self._nachricht("Marke gefunden!")
            return True

        self._nachricht("Keine Marke vorhanden!")
        return False

    def entferneMarke(self):
        if self.markeVorhanden():
            marke = self.detect(Marke)  # Greenfoot: removeTouching(Marke.class)
            if marke is not None:
                marke.remove()

    # private Methoden (in Java "private", in Python mit _ am Anfang)

    def _nachricht(self, pText):
        if self.anzeige is not None:
            self.anzeige.anzeigen(pText)
            warte(1)
            self.anzeige.loeschen()

    def _displayAusschalten(self):
        self.anzeige.remove()

    def _mitteDesNachbarfelds(self, richtung):
        schritt = {0: (0, -1), 90: (1, 0), 180: (0, 1), 270: (-1, 0)}[round(richtung) % 360]
        x, y = self.center
        return (x + schritt[0] * ZELLENGROESSE, y + schritt[1] * ZELLENGROESSE)

    def on_setup(self):
        """Wird aufgerufen, sobald der Rover in der Welt ist (addedToWorld in Greenfoot)."""
        self.add_costume("images/rover.png")
        self.size = (50, 50)
        self.orientation = -90  # Das Bild zeigt nach rechts, miniworlds erwartet "nach oben".
        self.direction = "right"  # wie Rotation 0 in Greenfoot
        # addObject(anzeige, 7, 0): Mitte des Feldes (7, 0)
        self.anzeige = Rover.Display((7 * ZELLENGROESSE + ZELLENGROESSE // 2, ZELLENGROESSE // 2), world=self.world)
        if self.zeile == 0:
            self.setzeFeld(self.spalte, 1)
        self.anzeige.anzeigen("Ich bin bereit")

    class Display(miniworlds.Actor):
        """Die Anzeige am oberen Rand, auf der der Rover Meldungen ausgibt."""

        _bild = None
        _schrift = None

        def on_setup(self):
            self.add_costume("images/nachricht.png")
            self.size = (500, 50)

        def act(self):
            pass

        def anzeigen(self, pText):
            self.loeschen()
            # Greenfoot: getImage().drawImage(new GreenfootImage(pText, 25, Color.BLACK, ...), 10, 10)
            if Rover.Display._bild is None:
                projekt = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                Rover.Display._bild = pygame.image.load(os.path.join(projekt, "images", "nachricht.png"))
                Rover.Display._schrift = pygame.font.Font(None, 34)
            bild = Rover.Display._bild.copy()
            bild.blit(Rover.Display._schrift.render(str(pText), True, (0, 0, 0)), (10, 10))
            self.costume.set_image(self.costume.add_image(bild))

        def loeschen(self):
            # Greenfoot: getImage().clear(); setImage("images/nachricht.png")
            while len(self.costume.images) > 1:
                self.costume.set_image(0)
                self.costume.remove_last_image()
