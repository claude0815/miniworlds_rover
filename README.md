# Planet 2.0 – das Rover-Szenario für miniworlds

Nachbau des Greenfoot-Szenarios **Planet 2.0** (Rover, Gestein, Hügel, Marke –
Thomas Kempe & David Tepaße) mit [miniworlds](https://github.com/asbl/miniworlds).
Das Projekt ist für den Editor [editor.opencoding.de](https://editor.opencoding.de/)
aufgebaut. Objekte platzieren und verschieben, Methoden per Rechtsklick aufrufen,
*Act*/*Run*, Geschwindigkeit und Code-Export erledigt dort der Editor, so wie in
Greenfoot die Entwicklungsumgebung. Ohne Editor läuft es auch am Desktop mit `python main.py`.

## Aufbau

```
project.toml          Projektdatei für den Editor
main.py               erzeugt den Planeten und startet ihn
classes/
  Planet.py           Planet.java   – Welt 16 × 12 Felder à 50 px
  Rover.py            Rover.java    – inkl. innerer Klasse Rover.Display
  Gestein.py          Gestein.java  – zufällig rot oder blau
  Huegel.py           Huegel.java
  Marke.py            Marke.java
  Feldakteur.py       was Greenfoot mitbringt: Felder, Greenfoot.delay, Greenfoot.setSpeed
images/               alle Originalbilder
tests/                automatische Tests (pytest)
```

Die Methode `act()` des Rovers steht in `classes/Rover.py` und enthält wie im
Original die `while`-Schleife, die bis zum nächsten Hügel fährt und Gestein einsammelt.

## Benutzen

**Im Editor:** Den Projektordner (bzw. ein ZIP davon) im Editor öffnen und
starten. Klassen wie in Greenfoot in die Welt setzen. Ein Rechtsklick auf den
Rover listet `fahre()`, `drehe(richtung)`, `gesteinVorhanden()`,
`huegelVorhanden(richtung)`, `nimmGestein()`, `setzeMarke()`, `markeVorhanden()`,
`entferneMarke()` und `act()`. Texte kann man mit oder ohne Anführungszeichen
eingeben (`"links"` oder `links`).

**Am Desktop:**

```bash
pip install -r requirements.txt
```

```bash
python main.py
```

Ohne Editor gibt es keine Maus-Platzierung. Die Startaufstellung steht dann im
Code, siehe das Beispiel in `main.py`. `act()` läuft sofort los.

## Von Java nach Python

| Greenfoot (Java) | miniworlds (Python) |
|---|---|
| `class Rover extends Actor` | `class Rover(Feldakteur)` (Feldakteur erbt von `miniworlds.Actor`) |
| `class Planet extends World`, `super(16, 12, 50)` | `class Planet(miniworlds.World)`, 800 × 600 Pixel |
| `addedToWorld(World world)` | `on_setup(self)` |
| `getX()`, `getY()` | `self.spalte`, `self.zeile` |
| `setLocation(x, y)` | `self.setzeFeld(spalte, zeile)` |
| `move(1)` | `self.move(ZELLENGROESSE)` |
| `turn(90)` / `turn(-90)` | `self.turn_right(90)` / `self.turn_left(90)` |
| `getOneIntersectingObject(Gestein.class)` | `self.detect(Gestein)` |
| `getOneObjectAtOffset(dx, dy, Huegel.class)` | `self.detect_actor_at(richtung, ZELLENGROESSE, Huegel)` |
| `removeTouching(Gestein.class)` | `self.detect(Gestein).remove()` |
| `getWorld().addObject(new Marke(), x, y)` | `Marke(self.center, world=self.world)` |
| `setImage("images/rover.png")` | `self.add_costume("images/rover.png")` |
| `setBackground("images/boden.png")` | `self.add_background(...)` + `is_textured` |
| `setPaintOrder(Rover.class, …)` | `zeichenreihenfolge = (Rover, …)` + `layer` |
| `Greenfoot.delay(1)` | `warte(1)` |
| `Greenfoot.setSpeed(20)` | `setzeGeschwindigkeit(20)` |
| `Greenfoot.getRandomNumber(2)` | `random.randint(0, 1)` |
| `private void nachricht(...)` | `def _nachricht(...)` |

Methodennamen, Meldungstexte und Verhalten entsprechen dem Original. Das gilt auch
für die Eigenheiten: An der oberen Grenze meldet `fahre()` zweimal „Ich kann mich
nicht bewegen“, `nimmGestein()` und `entferneMarke()` entfernen genau ein Objekt,
und jeder Rover erzeugt seine eigene Anzeige auf Feld (7, 0).

## Unterschiede zu Greenfoot

* **Richtungen:** miniworlds zählt wie Scratch: `direction` 0 = oben,
  90 = rechts, 180 = unten, −90 = links. In Greenfoot ist Rotation 0 = rechts.
  Ein neuer Rover schaut wie in Greenfoot nach rechts.
* **Felder:** Der Editor platziert Objekte in Pixeln, darum ist der Planet eine
  normale Pixelwelt. Rover, Gestein, Hügel und Marke erben von `Feldakteur` und
  rasten immer in der Mitte eines 50-px-Feldes ein, auch beim Ziehen mit der Maus.
* **`Greenfoot.delay` im Browser:** `warte()` zeichnet die Welt und wartet. Am
  Desktop sieht man den Rover so Feld für Feld fahren. Im Editor geht das nur,
  wenn `act()` über **Schritt** bzw. **Start** läuft und der Browser JSPI kann
  (z. B. aktuelles Chrome/Edge). Per **Rechtsklick** aufgerufene Methoden laufen im
  Editor ohne Pause durch; der Rover steht dann sofort am Ziel.
* **Endlosschleifen:** Liegt vor dem Rover in Fahrtrichtung kein Hügel, endet die
  `while`-Schleife in `act()` nie (auch in Greenfoot nicht). Wo Python nicht
  warten kann, bricht `warte()` nach 3 Sekunden mit der Meldung „Abgebrochen: Das
  Programm hört nicht auf (Endlosschleife?) …“ ab. Sonst würde der Editor das
  Programm hart beenden.
* Im Browser-Editor selbst ist das noch nicht getestet; geprüft ist die
  Schnittstelle, die der Editor aufruft, und das Verhalten mit nachgestelltem
  Pyodide (siehe Tests).
* Ein im Editor in Zeile 0 gesetzter Rover bleibt dort. In Greenfoot rückt
  `addedToWorld` ihn in Zeile 1. Im Code erzeugte Rover werden verschoben.
* Der Code-Export des Editors listet auch die Anzeige-Objekte (`Display`). Diese
  Zeilen kann man löschen, denn jeder Rover erzeugt seine Anzeige selbst.

## Tests

```bash
pip install pytest
```

```bash
python -m pytest
```

Die Tests prüfen jede Rover-Methode gegen das Java-Original (Meldungen, Ränder,
alle Kombinationen von Richtung und Drehung bei `huegelVorhanden`). Dazu kommt ein
kompletter Ablauf über die `ScenarioHost`-Schnittstelle, die der Editor benutzt
(platzieren, verschieben, Methoden aufrufen, Act, Export), und ein Desktop-Lauf.
