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

# HP-System
max_hp = 100
current_hp = max_hp

# Stamina-Leiste UI
stamina_bar_bg = Entity(model='cube', color=color.dark_gray, scale=(0.3, 0.03, 1), position=(0.6, -0.4, 0), parent=camera.ui)
stamina_bar = Entity(model='cube', color=color.blue, scale=(0.3, 0.03, 1), position=(0.6, -0.4, -0.01), parent=camera.ui)
stamina_text = Text('STAMINA', position=(0.45, -0.35, -0.02), scale=1, color=color.white, parent=camera.ui)

# HP-Leiste UI
hp_bar_bg = Entity(model='cube', color=color.dark_gray, scale=(0.3, 0.03, 1), position=(-0.6, -0.4, 0), parent=camera.ui)
hp_bar = Entity(model='cube', color=color.red, scale=(0.3, 0.03, 1), position=(-0.6, -0.4, -0.01), parent=camera.ui)
hp_text = Text('HP', position=(-0.75, -0.35, -0.02), scale=1, color=color.white, parent=camera.ui)

# Enemy-Klasse
class Enemy(Entity):
    def __init__(self, position, **kwargs):
        super().__init__(
            model='cube',
            scale=(1, 2, 1),
            position=position,
            collider='box',
            color=color.red,
            **kwargs
        )
        
        # Schießparameter
        self.shoot_timer = 0
        self.shoot_interval = random.uniform(1.5, 3.0)  # Schießt alle 1.5-3 Sekunden
        
        # Kopf des Feindes
        self.head = Entity(
            model='cube',
            color=color.red,
            scale=(0.8, 0.8, 0.8),
            position=(0, 0.6, 0),
            parent=self
        )
    
    def update(self):
        if paused:
            return
            
        # Schießtimer aktualisieren
        self.shoot_timer += time.dt
        
        # Schießen wenn Timer abgelaufen
        if self.shoot_timer >= self.shoot_interval:
            self.shoot_at_player()
            self.shoot_timer = 0
            self.shoot_interval = random.uniform(1.5, 3.0)
    
    def shoot_at_player(self):
        # Richtung zum Spieler berechnen
        direction_to_player = (player.position - self.position).normalized()
        
        # Feindliche Kugel erstellen
        enemy_bullet = EnemyBullet(
            position=self.position + Vec3(0, 1, 0),  # Etwas höher spawnen
            direction=direction_to_player
        )

# Funktion zum Erstellen neuer Feinde
def spawn_enemies(count=5):
    global enemies
    for i in range(count):
        x = random.uniform(-arena_size + 3, arena_size - 3)
        z = random.uniform(-arena_size + 3, arena_size - 3)
        y = 1  # Feinde stehen auf dem Boden
        
        enemy = Enemy(position=(x, y, z))
        enemies.append(enemy)

# Feinde erstellen
enemies = []
spawn_enemies(5)

# Spieler-Kugel-Klasse
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
            
        # Kollisionsprüfung mit Feinden
        for enemy in enemies[:]:  # Kopie der Liste verwenden
            dist = distance(self.position, enemy.position)
            if dist < 1.5:  # Kollision mit Feind
                enemies.remove(enemy)
                destroy(enemy)
                destroy(self)
                
                # Neue Feinde spawnen wenn alle eliminiert wurden
                if len(enemies) == 0:
                    spawn_enemies(5)
                return
                
        # Prüfung auf Wand- oder Bodenkollision
        if (self.intersects(ground) or 
            self.intersects(wall_north) or 
            self.intersects(wall_south) or 
            self.intersects(wall_east) or 
            self.intersects(wall_west)):
            destroy(self)

# Feindliche Kugel-Klasse
class EnemyBullet(Entity):
    def __init__(self, direction, **kwargs):
        super().__init__(
            model='sphere',
            color=color.orange,
            scale=0.08,
            **kwargs
        )
        self.speed = 15
        self.lifetime = 3.0
        self.direction = direction
        
    def update(self):
        # Kugel bewegen
        self.position += self.direction * self.speed * time.dt
        
        # Lebensdauer verringern
        self.lifetime -= time.dt
        if self.lifetime <= 0:
            destroy(self)
            return
            
        # Kollisionsprüfung mit Spieler
        dist = distance(self.position, player.position)
        if dist < 1.0:  # Spieler getroffen
            global current_hp
            current_hp -= 10  # 10 HP Schaden
            current_hp = max(0, current_hp)
            destroy(self)
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
    
    # HP-Leiste aktualisieren
    hp_percentage = current_hp / max_hp
    hp_bar.scale_x = 0.3 * hp_percentage
    
    # Position des roten Balkens anpassen, damit er links am Hintergrund ausgerichtet ist
    hp_bar.x = -0.6 - (0.3 * (1 - hp_percentage)) / 2

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
