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

# Stamina-System
max_stamina = 100
current_stamina = max_stamina
stamina_drain_rate = 30  # Stamina pro Sekunde beim Sprinten
stamina_regen_rate = 20  # Stamina pro Sekunde bei Regeneration
is_sprinting = False
sprint_speed_multiplier = 2.0

# Stamina-Leiste UI
stamina_bar_bg = Entity(model='cube', color=color.dark_gray, scale=(0.3, 0.03, 1), position=(0.6, -0.4, 0), parent=camera.ui)
stamina_bar = Entity(model='cube', color=color.blue, scale=(0.3, 0.03, 1), position=(0.6, -0.4, -0.01), parent=camera.ui)
stamina_text = Text('STAMINA', position=(0.45, -0.38, -0.02), scale=1, color=color.white, parent=camera.ui)

# Zielscheiben-Klasse (Bogenschießziel)
class Target(Entity):
    def __init__(self, position, **kwargs):
        super().__init__(
            model='cube',
            scale=(2.4, 2.4, 0.1),
            position=position,
            collider='box',
            color=color.white,
            **kwargs
        )
        
        # Bewegungsparameter
        self.speed = random.uniform(5, 10)
        self.direction_x = random.uniform(-1, 1)
        self.direction_z = random.uniform(-1, 1)
        self.direction_y = random.uniform(-0.5, 0.5)
        
        # Ring 2 (rot)
        self.ring2 = Entity(
            model='cube',
            color=color.red,
            scale=(0.83, 0.83, 1.1),
            position=(0, 0, 0),
            parent=self
        )
        
        # Ring 3 (weiß)
        self.ring3 = Entity(
            model='cube',
            color=color.white,
            scale=(0.67, 0.67, 1.2),
            position=(0, 0, 0),
            parent=self
        )
        
        # Ring 4 (rot)
        self.ring4 = Entity(
            model='cube',
            color=color.red,
            scale=(0.5, 0.5, 1.3),
            position=(0, 0, 0),
            parent=self
        )
        
        # Ring 5 (weiß)
        self.ring5 = Entity(
            model='cube',
            color=color.white,
            scale=(0.33, 0.33, 1.4),
            position=(0, 0, 0),
            parent=self
        )
        
        # Bullseye (rot)
        self.bullseye = Entity(
            model='cube',
            color=color.red,
            scale=(0.17, 0.17, 1.5),
            position=(0, 0, 0),
            parent=self
        )
    
    def update(self):
        # Ziel bewegen
        self.x += self.direction_x * self.speed * time.dt
        self.z += self.direction_z * self.speed * time.dt
        self.y += self.direction_y * self.speed * time.dt
        
        # Grenzen der Arena prüfen und Richtung umkehren
        if self.x > arena_size - 2 or self.x < -arena_size + 2:
            self.direction_x *= -1
        if self.z > arena_size - 2 or self.z < -arena_size + 2:
            self.direction_z *= -1
        if self.y > 4 or self.y < 1:
            self.direction_y *= -1

# Funktion zum Erstellen neuer Ziele
def spawn_targets(count=7):
    global targets
    for i in range(count):
        x = random.uniform(-arena_size + 2, arena_size - 2)
        z = random.uniform(-arena_size + 2, arena_size - 2)
        y = random.uniform(1, 4)
        
        target = Target(position=(x, y, z))
        targets.append(target)

# Ziele erstellen (5-10 Zielscheiben an zufälligen Positionen)
targets = []
spawn_targets(7)

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
            if dist < 1.5:  # Kollision wenn Distanz kleiner als 1.5 Einheiten (volle Zielscheibe)
                targets.remove(target)
                destroy(target)
                destroy(self)
                
                # Neue Ziele spawnen wenn alle abgeschossen wurden
                if len(targets) == 0:
                    spawn_targets(7)
                return
                
        # Prüfung auf Wand- oder Bodenkollision
        if (self.intersects(ground) or 
            self.intersects(wall_north) or 
            self.intersects(wall_south) or 
            self.intersects(wall_east) or 
            self.intersects(wall_west)):
            destroy(self)

# Update-Funktion für Stamina-System
def update():
    global current_stamina, is_sprinting
    
    if paused:
        return
    
    # Sprint-Eingabe prüfen
    if held_keys['left shift'] and current_stamina > 0:
        if not is_sprinting:
            is_sprinting = True
            player.speed *= sprint_speed_multiplier
        
        # Stamina verbrauchen
        current_stamina -= stamina_drain_rate * time.dt
        current_stamina = max(0, current_stamina)
        
        # Sprint beenden wenn Stamina aufgebraucht
        if current_stamina <= 0:
            is_sprinting = False
            player.speed /= sprint_speed_multiplier
    else:
        # Sprint beenden
        if is_sprinting:
            is_sprinting = False
            player.speed /= sprint_speed_multiplier
        
        # Stamina regenerieren
        if current_stamina < max_stamina:
            current_stamina += stamina_regen_rate * time.dt
            current_stamina = min(max_stamina, current_stamina)
    
    # Stamina-Leiste aktualisieren
    stamina_percentage = current_stamina / max_stamina
    stamina_bar.scale_x = 0.3 * stamina_percentage
    
    # Position des grünen Balkens anpassen, damit er links am Hintergrund ausgerichtet ist
    stamina_bar.x = 0.6 - (0.3 * (1 - stamina_percentage)) / 2
    
    # Stamina-Leiste bleibt immer blau
    stamina_bar.color = color.blue

# Eingabe-Funktion für Schießen
def input(key):
    global paused, pause_text
    
    if key == 'escape':
        paused = not paused
        if paused:
            # Spiel pausieren
            mouse.locked = False
            pause_text = Text('PAUSE', origin=(0, 0), scale=5, color=color.white)
        else:
            # Spiel fortsetzen
            mouse.locked = True
            if pause_text:
                destroy(pause_text)
                pause_text = None
    
    if not paused and key == 'left mouse down':
        # Kugel an der Kameraposition erstellen
        bullet = Bullet(position=camera.world_position)

# Spiel starten
app.run()
