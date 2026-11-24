import miniworlds

from classes.Feldakteur import ZELLENGROESSE, Feldakteur, setzeGeschwindigkeit
from classes.Gestein import Gestein
from classes.Huegel import Huegel
from classes.Marke import Marke
from classes.Rover import Rover


class Planet(miniworlds.World):
    """Die einzigen aktiven Akteure in der Roboterwelt sind die Roboter.
    Die Welt besteht aus 16 * 12 Feldern."""

    zellenGroesse = ZELLENGROESSE

    # setPaintOrder(...): Objekte der zuerst genannten Klasse liegen ganz oben.
    zeichenreihenfolge = (Rover, Marke, Gestein, Huegel)

    def __init__(self):
        """Erschaffe eine Welt mit 16 * 12 Zellen."""
        super().__init__(16 * Planet.zellenGroesse, 12 * Planet.zellenGroesse)

    def on_setup(self):
        self.add_background("images/boden.png")
        # Wie setBackground in Greenfoot: Das Bild füllt die Welt kachelartig.
        self.background.is_textured = True
        self.background.texture_size = (Planet.zellenGroesse, Planet.zellenGroesse)
        setzeGeschwindigkeit(20)

    def on_new_actor(self, actor):
        """Wird für jedes neue Objekt in der Welt aufgerufen."""
        if isinstance(actor, Feldakteur):
            actor.center = actor.center  # in die Mitte seines Feldes setzen
            actor.collision_type = "rect"  # berühren = auf demselben Feld stehen
        for nummer, klasse in enumerate(self.zeichenreihenfolge):
            if isinstance(actor, klasse):
                actor.layer = len(self.zeichenreihenfolge) - nummer
                break
