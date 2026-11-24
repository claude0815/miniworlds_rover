from classes.Feldakteur import Feldakteur


class Marke(Feldakteur):
    """Eine Markierung, die der Rover setzen, erkennen und entfernen kann."""

    def on_setup(self):
        self.add_costume("images/marke.png")
        self.size = (50, 50)

    def act(self):
        """Die Anweisungen der Methode act werden ausgeführt, wenn der Act-Button
        im Hauptfenster geklickt wird."""
        pass
