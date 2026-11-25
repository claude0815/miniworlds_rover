import random

from classes.Feldakteur import Feldakteur


class Gestein(Feldakteur):
    """Ein Gesteinsbrocken, den der Rover aufnehmen kann."""

    def on_setup(self):
        # Konstruktor in Gestein.java: zufällig rotes oder blaues Gestein
        if random.randint(0, 1) == 0:  # Greenfoot.getRandomNumber(2) == 0
            self.add_costume("images/gesteinRot.png")
        else:
            self.add_costume("images/gesteinBlau.png")
        self.size = (50, 50)

    def act(self):
        """Die Anweisungen der Methode act werden ausgeführt, wenn der Act-Button
        im Hauptfenster geklickt wird."""
        pass
