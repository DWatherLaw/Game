from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

# Initialisierung der Ursina-Anwendung
app = Ursina()

# Boden erstellen
ground = Entity(model='plane', scale=30, color=color.green, collider='box')

# Wände erstellen (vier Wände um die Arena)
wall_height = 5
arena_size = 15

# Nördliche Wand
wall_north = Entity(model='cube', position=(0, wall_height/2, arena_size), scale=(arena_size*2, wall_height, 1), color=color.gray, collider='box')
# Südliche Wand  
wall_south = Entity(model='cube', position=(0, wall_height/2, -arena_size), scale=(arena_size*2, wall_height, 1), color=color.gray, collider='box')
# Östliche Wand
wall_east = Entity(model='cube', position=(arena_size, wall_height/2, 0), scale=(1, wall_height, arena_size*2), color=color.gray, collider='box')
# Westliche Wand
wall_west = Entity(model='cube', position=(-arena_size, wall_height/2, 0), scale=(1, wall_height, arena_size*2), color=color.gray, collider='box')

# Himmel erstellen
sky = Sky()

# Spieler erstellen (FirstPersonController)
player = FirstPersonController(position=(0, 1, 0))

# Pause-System
paused = False
pause_text = None

# Zielscheiben-Klasse (Bogenschießziel)
class Target(Entity):
    def __init__(self, position, **kwargs):
        super().__init__(
            model='cylinder',
            scale=(1.2, 0.05, 1.2),
            position=position,
            collider='box',
            color=color.white,
            **kwargs
        )
        
        # Ring 2 (rot)
        self.ring2 = Entity(
            model='cylinder',
            color=color.red,
            scale=(1.0, 1.1, 1.0),
            position=(0, 0, 0),
            parent=self
        )
        
        # Ring 3 (weiß)
        self.ring3 = Entity(
            model='cylinder',
            color=color.white,
            scale=(0.8, 1.2, 0.8),
            position=(0, 0, 0),
            parent=self
        )
        
        # Ring 4 (rot)
        self.ring4 = Entity(
            model='cylinder',
            color=color.red,
            scale=(0.6, 1.3, 0.6),
            position=(0, 0, 0),
            parent=self
        )
        
        # Ring 5 (weiß)
        self.ring5 = Entity(
            model='cylinder',
            color=color.white,
            scale=(0.4, 1.4, 0.4),
            position=(0, 0, 0),
            parent=self
        )
        
        # Bullseye (rot)
        self.bullseye = Entity(
            model='cylinder',
            color=color.red,
            scale=(0.2, 1.5, 0.2),
            position=(0, 0, 0),
            parent=self
        )

# Ziele erstellen (5-10 Zielscheiben an zufälligen Positionen)
targets = []
for i in range(7):
    x = random.uniform(-arena_size + 2, arena_size - 2)
    z = random.uniform(-arena_size + 2, arena_size - 2)
    y = random.uniform(1, 4)
    
    target = Target(position=(x, y, z))
    targets.append(target)

# Kugel-Klasse
class Bullet(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model='sphere',
            color=color.black,
            scale=0.1,
            **kwargs
        )
        self.speed = 20
        self.lifetime = 2.0
        self.direction = camera.forward
        
    def update(self):
        # Kugel vorwärts bewegen
        self.position += self.direction * self.speed * time.dt
        
        # Lebensdauer verringern
        self.lifetime -= time.dt
        if self.lifetime <= 0:
            destroy(self)
            return
            
        # Kollisionsprüfung mit distanzbasierter Erkennung
        for target in targets[:]:  # Kopie der Liste verwenden
            dist = distance(self.position, target.position)
            if dist < 0.5:  # Kollision wenn Distanz kleiner als 0.5 Einheiten
                targets.remove(target)
                destroy(target)
                destroy(self)
                return
                
        # Prüfung auf Wand- oder Bodenkollision
        if (self.intersects(ground) or 
            self.intersects(wall_north) or 
            self.intersects(wall_south) or 
            self.intersects(wall_east) or 
            self.intersects(wall_west)):
            destroy(self)

# Eingabe-Funktion für Schießen
def input(key):
    global paused, pause_text
    
    if key == 'escape':
        paused = not paused
        if paused:
            # Spiel pausieren
            application.paused = True
            mouse.locked = False
            pause_text = Text('PAUSE', origin=(0, 0), scale=5, color=color.white)
        else:
            # Spiel fortsetzen
            application.paused = False
            mouse.locked = True
            if pause_text:
                destroy(pause_text)
                pause_text = None
    
    if not paused and key == 'left mouse down':
        # Kugel an der Kameraposition erstellen
        bullet = Bullet(position=camera.world_position)

# Spiel starten
app.run()
