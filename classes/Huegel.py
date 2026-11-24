from classes.Feldakteur import Feldakteur


class Huegel(Feldakteur):
    """Ein Hügel – zu steil für den Rover."""

    def on_setup(self):
        self.add_costume("images/huegel.png")
        self.size = (50, 50)

    def act(self):
        pass
