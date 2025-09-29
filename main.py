from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import json
import math

# Initialisierung der Ursina-Anwendung
app = Ursina(
    title='Arena Shooter',
    borderless=False,
    fullscreen=False,
    size=(1280, 720),
    vsync=True,
    icon=''
)

# Kamera-Einstellungen für UI
camera.orthographic = False
camera.fov = 90

# Fenster in den Vordergrund bringen
window.color = color.black

# Spiel direkt starten
game_started = True

# Map-System
current_map = 1
waves_completed_on_map = 0
waves_per_map = 3

maps = {
    1: {
        "name": "Standard Arena",
        "type": "square",
        "size": 25,
        "enemies": 5,
        "color": color.dark_gray
    },
    2: {
        "name": "Kreisförmige Arena", 
        "type": "circle",
        "size": 20,
        "enemies": 6,
        "color": color.rgb(60, 60, 80)
    },
    3: {
        "name": "Labyrinth",
        "type": "maze",
        "size": 30,
        "enemies": 8,
        "color": color.rgb(40, 60, 40)
    },
    4: {
        "name": "Multi-Level Arena",
        "type": "multilevel", 
        "size": 28,
        "enemies": 10,
        "color": color.rgb(80, 60, 40)
    },
    5: {
        "name": "Offene Wüste",
        "type": "desert",
        "size": 35,
        "enemies": 12,
        "color": color.rgb(120, 100, 60)
    },
    6: {
        "name": "Industriegebiet",
        "type": "industrial",
        "size": 32,
        "enemies": 15,
        "color": color.rgb(50, 50, 50)
    }
}

# Globale Variablen für Map-Objekte
map_objects = []
ground = None

# Beleuchtung hinzufügen
DirectionalLight(direction=(1, -1, 1), color=color.white)
AmbientLight(color=color.rgb(100, 100, 100))

# Zusätzliche Beleuchtung für bessere Menü-Sichtbarkeit
menu_light = DirectionalLight(direction=(0, -1, 0), color=color.white)
menu_light.intensity = 1.5

# Partikel-System für Explosionen
class ParticleSystem:
    @staticmethod
    def create_explosion(position, color_particle=color.orange):
        for i in range(15):
            particle = Entity(
                model='cube',
                color=color_particle,
                scale=random.uniform(0.05, 0.15),
                position=position + Vec3(
                    random.uniform(-0.5, 0.5),
                    random.uniform(-0.5, 0.5),
                    random.uniform(-0.5, 0.5)
                )
            )
            
            # Partikel-Animation
            particle.animate_scale(0, duration=1.0)
            particle.animate_position(
                particle.position + Vec3(
                    random.uniform(-2, 2),
                    random.uniform(0, 3),
                    random.uniform(-2, 2)
                ),
                duration=1.0
            )
            destroy(particle, delay=1.0)
    
    @staticmethod
    def create_blood_effect(position):
        for i in range(8):
            particle = Entity(
                model='cube',
                color=color.red,
                scale=random.uniform(0.03, 0.08),
                position=position + Vec3(
                    random.uniform(-0.3, 0.3),
                    random.uniform(-0.3, 0.3),
                    random.uniform(-0.3, 0.3)
                )
            )
            
            particle.animate_scale(0, duration=0.5)
            particle.animate_position(
                particle.position + Vec3(
                    random.uniform(-1, 1),
                    random.uniform(-2, 0),
                    random.uniform(-1, 1)
                ),
                duration=0.5
            )
            destroy(particle, delay=0.5)

# Map-Erstellungsfunktionen
def create_square_arena(size, map_color):
    """Standard quadratische Arena mit Hindernissen"""
    global ground, map_objects
    
    # Boden
    ground = Entity(model='plane', scale=size*2, color=map_color, collider='box')
    map_objects.append(ground)
    
    wall_height = 6
    wall_color = color.rgb(80, 80, 80)
    
    # Vier Wände
    walls = [
        Entity(model='cube', position=(0, wall_height/2, size), scale=(size*2, wall_height, 1), color=wall_color, collider='box'),
        Entity(model='cube', position=(0, wall_height/2, -size), scale=(size*2, wall_height, 1), color=wall_color, collider='box'),
        Entity(model='cube', position=(size, wall_height/2, 0), scale=(1, wall_height, size*2), color=wall_color, collider='box'),
        Entity(model='cube', position=(-size, wall_height/2, 0), scale=(1, wall_height, size*2), color=wall_color, collider='box')
    ]
    map_objects.extend(walls)
    
    # Zentrale Hindernisse
    obstacles = [
        Entity(model='cube', position=(0, 1.5, 0), scale=(4, 3, 4), color=color.rgb(100, 100, 100), collider='box'),
        Entity(model='cube', position=(-10, 1, -10), scale=(3, 2, 3), color=color.rgb(90, 90, 90), collider='box'),
        Entity(model='cube', position=(10, 1, 10), scale=(3, 2, 3), color=color.rgb(90, 90, 90), collider='box'),
        Entity(model='cube', position=(-10, 1, 10), scale=(3, 2, 3), color=color.rgb(90, 90, 90), collider='box'),
        Entity(model='cube', position=(10, 1, -10), scale=(3, 2, 3), color=color.rgb(90, 90, 90), collider='box'),
        # Säulen
        Entity(model='cube', position=(-15, 2.5, 0), scale=(1, 5, 1), color=color.rgb(70, 70, 70), collider='box'),
        Entity(model='cube', position=(15, 2.5, 0), scale=(1, 5, 1), color=color.rgb(70, 70, 70), collider='box'),
        Entity(model='cube', position=(0, 2.5, -15), scale=(1, 5, 1), color=color.rgb(70, 70, 70), collider='box'),
        Entity(model='cube', position=(0, 2.5, 15), scale=(1, 5, 1), color=color.rgb(70, 70, 70), collider='box')
    ]
    map_objects.extend(obstacles)

def create_circle_arena(size, map_color):
    """Kreisförmige Arena mit runden Wänden und konzentrischen Hindernissen"""
    global ground, map_objects
    
    # Boden
    ground = Entity(model='plane', scale=size*2, color=map_color, collider='box')
    map_objects.append(ground)
    
    wall_height = 6
    wall_color = color.rgb(80, 80, 80)
    
    # Kreisförmige Wände (viele kleine Segmente)
    segments = 32
    for i in range(segments):
        angle = (i / segments) * 2 * 3.14159
        x = size * math.cos(angle)
        z = size * math.sin(angle)
        
        wall = Entity(
            model='cube',
            position=(x, wall_height/2, z),
            scale=(1.5, wall_height, 1.5),
            color=wall_color,
            collider='box',
            rotation_y=angle * 57.2958
        )
        map_objects.append(wall)
    
    # Konzentrische Hindernisse
    inner_obstacles = []
    # Innerer Ring
    for i in range(8):
        angle = (i / 8) * 2 * 3.14159
        x = (size * 0.4) * math.cos(angle)
        z = (size * 0.4) * math.sin(angle)
        obstacle = Entity(model='cube', position=(x, 1, z), scale=(2, 2, 2), color=color.rgb(100, 80, 80), collider='box')
        inner_obstacles.append(obstacle)
    
    # Mittlerer Ring
    for i in range(12):
        angle = (i / 12) * 2 * 3.14159
        x = (size * 0.7) * math.cos(angle)
        z = (size * 0.7) * math.sin(angle)
        obstacle = Entity(model='cube', position=(x, 0.5, z), scale=(1.5, 1, 1.5), color=color.rgb(80, 100, 80), collider='box')
        inner_obstacles.append(obstacle)
    
    map_objects.extend(inner_obstacles)

def create_maze_arena(size, map_color):
    """Komplexes Labyrinth mit vielen Gängen"""
    global ground, map_objects
    
    # Boden
    ground = Entity(model='plane', scale=size*2, color=map_color, collider='box')
    map_objects.append(ground)
    
    wall_height = 6
    wall_color = color.rgb(60, 60, 60)
    
    # Äußere Wände
    outer_walls = [
        Entity(model='cube', position=(0, wall_height/2, size), scale=(size*2, wall_height, 1), color=wall_color, collider='box'),
        Entity(model='cube', position=(0, wall_height/2, -size), scale=(size*2, wall_height, 1), color=wall_color, collider='box'),
        Entity(model='cube', position=(size, wall_height/2, 0), scale=(1, wall_height, size*2), color=wall_color, collider='box'),
        Entity(model='cube', position=(-size, wall_height/2, 0), scale=(1, wall_height, size*2), color=wall_color, collider='box')
    ]
    map_objects.extend(outer_walls)
    
    # Komplexes Labyrinth-System
    maze_walls = [
        # Hauptkorridore (horizontal)
        Entity(model='cube', position=(-12, wall_height/2, 0), scale=(8, wall_height, 1), color=wall_color, collider='box'),
        Entity(model='cube', position=(12, wall_height/2, 8), scale=(8, wall_height, 1), color=wall_color, collider='box'),
        Entity(model='cube', position=(0, wall_height/2, -12), scale=(12, wall_height, 1), color=wall_color, collider='box'),
        Entity(model='cube', position=(-8, wall_height/2, 12), scale=(16, wall_height, 1), color=wall_color, collider='box'),
        Entity(model='cube', position=(8, wall_height/2, -8), scale=(12, wall_height, 1), color=wall_color, collider='box'),
        
        # Hauptkorridore (vertikal)
        Entity(model='cube', position=(0, wall_height/2, 4), scale=(1, wall_height, 8), color=wall_color, collider='box'),
        Entity(model='cube', position=(-15, wall_height/2, -8), scale=(1, wall_height, 12), color=wall_color, collider='box'),
        Entity(model='cube', position=(15, wall_height/2, -4), scale=(1, wall_height, 16), color=wall_color, collider='box'),
        Entity(model='cube', position=(8, wall_height/2, 15), scale=(1, wall_height, 12), color=wall_color, collider='box'),
        Entity(model='cube', position=(-8, wall_height/2, -15), scale=(1, wall_height, 8), color=wall_color, collider='box'),
        
        # Kleine Kammern und Hindernisse
        Entity(model='cube', position=(-20, wall_height/2, 20), scale=(6, wall_height, 6), color=wall_color, collider='box'),
        Entity(model='cube', position=(20, wall_height/2, -20), scale=(6, wall_height, 6), color=wall_color, collider='box'),
        Entity(model='cube', position=(-4, wall_height/2, -4), scale=(4, wall_height, 4), color=wall_color, collider='box'),
        Entity(model='cube', position=(4, wall_height/2, 4), scale=(4, wall_height, 4), color=wall_color, collider='box')
    ]
    map_objects.extend(maze_walls)

def create_multilevel_arena(size, map_color):
    """Multi-Level Arena mit verschiedenen Höhen"""
    global ground, map_objects
    
    # Hauptboden
    ground = Entity(model='plane', scale=size*2, color=map_color, collider='box')
    map_objects.append(ground)
    
    wall_height = 5
    wall_color = color.rgb(80, 60, 40)
    
    # Äußere Wände
    outer_walls = [
        Entity(model='cube', position=(0, wall_height/2, size), scale=(size*2, wall_height, 1), color=wall_color, collider='box'),
        Entity(model='cube', position=(0, wall_height/2, -size), scale=(size*2, wall_height, 1), color=wall_color, collider='box'),
        Entity(model='cube', position=(size, wall_height/2, 0), scale=(1, wall_height, size*2), color=wall_color, collider='box'),
        Entity(model='cube', position=(-size, wall_height/2, 0), scale=(1, wall_height, size*2), color=wall_color, collider='box')
    ]
    map_objects.extend(outer_walls)
    
    # Erhöhte Plattformen
    platforms = [
        Entity(model='cube', position=(-8, 1, -8), scale=(6, 2, 6), color=color.rgb(100, 80, 60), collider='box'),
        Entity(model='cube', position=(8, 1.5, 8), scale=(6, 3, 6), color=color.rgb(100, 80, 60), collider='box'),
        Entity(model='cube', position=(0, 2, 0), scale=(4, 4, 4), color=color.rgb(100, 80, 60), collider='box'),
        Entity(model='cube', position=(-8, 0.5, 8), scale=(6, 1, 6), color=color.rgb(100, 80, 60), collider='box')
    ]
    map_objects.extend(platforms)
    
    # Rampen
    ramps = [
        Entity(model='cube', position=(-5, 0.5, -5), scale=(3, 1, 3), color=color.rgb(90, 70, 50), collider='box', rotation=(0, 0, 15)),
        Entity(model='cube', position=(5, 0.75, 5), scale=(3, 1.5, 3), color=color.rgb(90, 70, 50), collider='box', rotation=(0, 0, -15))
    ]
    map_objects.extend(ramps)

def create_desert_arena(size, map_color):
    """Offene Wüste mit wenigen Hindernissen"""
    global ground, map_objects
    
    # Großer Boden
    ground = Entity(model='plane', scale=size*2, color=map_color, collider='box')
    map_objects.append(ground)
    
    wall_height = 3  # Niedrigere Wände für offenes Gefühl
    wall_color = color.rgb(140, 120, 80)
    
    # Weit entfernte Wände
    walls = [
        Entity(model='cube', position=(0, wall_height/2, size), scale=(size*2, wall_height, 1), color=wall_color, collider='box'),
        Entity(model='cube', position=(0, wall_height/2, -size), scale=(size*2, wall_height, 1), color=wall_color, collider='box'),
        Entity(model='cube', position=(size, wall_height/2, 0), scale=(1, wall_height, size*2), color=wall_color, collider='box'),
        Entity(model='cube', position=(-size, wall_height/2, 0), scale=(1, wall_height, size*2), color=wall_color, collider='box')
    ]
    map_objects.extend(walls)
    
    # Wenige Felsen als Deckung
    rocks = [
        Entity(model='cube', position=(-10, 1, -10), scale=(2, 2, 2), color=color.rgb(100, 90, 70), collider='box'),
        Entity(model='cube', position=(12, 0.5, 8), scale=(3, 1, 3), color=color.rgb(100, 90, 70), collider='box'),
        Entity(model='cube', position=(0, 1.5, -15), scale=(2, 3, 2), color=color.rgb(100, 90, 70), collider='box'),
        Entity(model='cube', position=(-15, 0.8, 5), scale=(2.5, 1.5, 2.5), color=color.rgb(100, 90, 70), collider='box')
    ]
    map_objects.extend(rocks)

def create_industrial_arena(size, map_color):
    """Industriegebiet mit vielen Containern und Hindernissen"""
    global ground, map_objects
    
    # Boden
    ground = Entity(model='plane', scale=size*2, color=map_color, collider='box')
    map_objects.append(ground)
    
    wall_height = 6
    wall_color = color.rgb(40, 40, 40)
    
    # Äußere Wände
    outer_walls = [
        Entity(model='cube', position=(0, wall_height/2, size), scale=(size*2, wall_height, 1), color=wall_color, collider='box'),
        Entity(model='cube', position=(0, wall_height/2, -size), scale=(size*2, wall_height, 1), color=wall_color, collider='box'),
        Entity(model='cube', position=(size, wall_height/2, 0), scale=(1, wall_height, size*2), color=wall_color, collider='box'),
        Entity(model='cube', position=(-size, wall_height/2, 0), scale=(1, wall_height, size*2), color=wall_color, collider='box')
    ]
    map_objects.extend(outer_walls)
    
    # Container und Hindernisse
    containers = [
        # Große Container
        Entity(model='cube', position=(-8, 1.5, -8), scale=(4, 3, 8), color=color.rgb(80, 40, 40), collider='box'),
        Entity(model='cube', position=(10, 1.5, 5), scale=(6, 3, 4), color=color.rgb(40, 80, 40), collider='box'),
        Entity(model='cube', position=(0, 2, -12), scale=(8, 4, 4), color=color.rgb(40, 40, 80), collider='box'),
        
        # Kleine Container
        Entity(model='cube', position=(-12, 1, 8), scale=(3, 2, 3), color=color.rgb(60, 60, 40), collider='box'),
        Entity(model='cube', position=(8, 1, -5), scale=(3, 2, 3), color=color.rgb(60, 40, 60), collider='box'),
        Entity(model='cube', position=(5, 0.5, 12), scale=(2, 1, 4), color=color.rgb(40, 60, 60), collider='box'),
        
        # Rohre und Säulen
        Entity(model='cube', position=(-5, 2.5, 0), scale=(1, 5, 1), color=color.rgb(70, 70, 70), collider='box'),
        Entity(model='cube', position=(0, 2.5, 8), scale=(1, 5, 1), color=color.rgb(70, 70, 70), collider='box'),
        Entity(model='cube', position=(12, 1.5, -10), scale=(2, 3, 2), color=color.rgb(70, 70, 70), collider='box')
    ]
    map_objects.extend(containers)

def load_map(map_id):
    """Lädt eine bestimmte Map"""
    global current_map, map_objects, ground
    
    # Alte Map-Objekte entfernen
    for obj in map_objects:
        destroy(obj)
    map_objects.clear()
    
    current_map = map_id
    map_data = maps[map_id]
    
    # Map basierend auf Typ erstellen
    if map_data["type"] == "square":
        create_square_arena(map_data["size"], map_data["color"])
    elif map_data["type"] == "circle":
        create_circle_arena(map_data["size"], map_data["color"])
    elif map_data["type"] == "maze":
        create_maze_arena(map_data["size"], map_data["color"])
    elif map_data["type"] == "multilevel":
        create_multilevel_arena(map_data["size"], map_data["color"])
    elif map_data["type"] == "desert":
        create_desert_arena(map_data["size"], map_data["color"])
    elif map_data["type"] == "industrial":
        create_industrial_arena(map_data["size"], map_data["color"])

# Erste Map laden
load_map(1)

# Himmel erstellen
sky = Sky()

# Spieler erstellen (FirstPersonController)
player = FirstPersonController(position=(0, 1, 0))

# Maus für Spiel sperren
mouse.locked = True

# Pause-System
paused = False
pause_text = None

# Game Over System
game_over = False
game_over_menu = None
game_over_text = None
restart_button = None
quit_button = None

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

# Fall-Erkennungssystem
fall_threshold = -5.0  # Y-Position unter der der Spieler als "gefallen" gilt
is_falling = False
fall_start_time = 0
fall_death_delay = 4.0  # 4 Sekunden bis zum Tod

# Waffensystem
current_weapon = 'pistol'
weapons = {
    'pistol': {
        'damage': 25,
        'fire_rate': 0.5,
        'max_ammo': 12,
        'current_ammo': 12,
        'reload_time': 2.0,
        'bullet_speed': 20,
        'bullet_color': color.yellow,
        'burst_mode': False,
        'burst_count': 1,
        'burst_delay': 0.1
    },
    'rifle': {
        'damage': 40,
        'fire_rate': 0.3,
        'max_ammo': 30,
        'current_ammo': 30,
        'reload_time': 3.0,
        'bullet_speed': 25,
        'bullet_color': color.orange,
        'burst_mode': False,
        'burst_count': 1,
        'burst_delay': 0.1
    },
    'shotgun': {
        'damage': 60,
        'fire_rate': 1.0,
        'max_ammo': 8,
        'current_ammo': 8,
        'reload_time': 2.5,
        'bullet_speed': 18,
        'bullet_color': color.red,
        'burst_mode': False,
        'burst_count': 1,
        'burst_delay': 0.1
    },
    'machinegun': {
        'damage': 30,
        'fire_rate': 0.8,
        'max_ammo': 50,
        'current_ammo': 50,
        'reload_time': 4.0,
        'bullet_speed': 22,
        'bullet_color': color.lime,
        'burst_mode': True,
        'burst_count': 5,
        'burst_delay': 0.08
    }
}

# Schießsystem
last_shot_time = 0
is_reloading = False
reload_start_time = 0

# Salvenfeuer-System
is_bursting = False
burst_shots_fired = 0
burst_start_time = 0
burst_queue = []

# Punktesystem
score = 0
wave_number = 1
enemies_killed_this_wave = 0
enemies_per_wave = 10  # Startet mit 10 Gegnern
enemies_spawned_this_wave = 0
max_enemies_per_wave = {1: 10, 2: 15, 3: 20}

# Stamina-Leiste UI
stamina_bar_bg = Entity(model='cube', color=color.dark_gray, scale=(0.3, 0.03, 1), position=(0.6, -0.4, 0), parent=camera.ui)
stamina_bar = Entity(model='cube', color=color.blue, scale=(0.3, 0.03, 1), position=(0.6, -0.4, -0.01), parent=camera.ui)
stamina_text = Text('STAMINA', position=(0.45, -0.35, -0.02), scale=1, color=color.white, parent=camera.ui)

# HP-Leiste UI
hp_bar_bg = Entity(model='cube', color=color.dark_gray, scale=(0.3, 0.03, 1), position=(-0.6, -0.4, 0), parent=camera.ui)
hp_bar = Entity(model='cube', color=color.red, scale=(0.3, 0.03, 1), position=(-0.6, -0.4, -0.01), parent=camera.ui)
hp_text = Text('HP', position=(-0.75, -0.35, -0.02), scale=1, color=color.white, parent=camera.ui)

# Crosshair
crosshair_h = Entity(model='cube', color=color.white, scale=(0.02, 0.002, 1), position=(0, 0, -0.1), parent=camera.ui)
crosshair_v = Entity(model='cube', color=color.white, scale=(0.002, 0.02, 1), position=(0, 0, -0.1), parent=camera.ui)

# UI Texte
ammo_text = Text('', position=(-0.9, -0.45), scale=1.5, color=color.white, parent=camera.ui)
weapon_text = Text('', position=(-0.9, -0.4), scale=1, color=color.white, parent=camera.ui)
score_text = Text('', position=(-0.9, 0.45), scale=1.5, color=color.white, parent=camera.ui)
wave_text = Text('', position=(-0.9, 0.4), scale=1, color=color.white, parent=camera.ui)
map_text = Text('', position=(-0.9, 0.35), scale=1, color=color.cyan, parent=camera.ui)
reload_text = Text('', position=(0, -0.2), scale=2, color=color.red, parent=camera.ui)

# Enemy-Klasse
class Enemy(Entity):
    def __init__(self, position, **kwargs):
        super().__init__(
            model='cube',
            scale=(0.6, 1.2, 0.4),  # Torso - schmaler und realistischer
            position=position,
            collider='box',
            color=color.dark_gray,  # Körperfarbe
            **kwargs
        )
        
        # Schießparameter
        self.shoot_timer = 0
        self.shoot_interval = random.uniform(1.5, 3.0)  # Schießt alle 1.5-3 Sekunden
        
        # Bewegungsparameter
        self.move_speed = random.uniform(2, 4)
        self.move_timer = 0
        self.move_interval = random.uniform(2, 4)
        self.move_direction = Vec3(random.uniform(-1, 1), 0, random.uniform(-1, 1)).normalized()
        self.last_player_position = player.position
        self.chase_distance = 15
        self.attack_distance = 8
        self.sight_range = 25  # Kann Spieler aus 25 Einheiten sehen
        
        # Physik-Parameter für realistische Bewegung
        self.velocity = Vec3(0, 0, 0)
        self.gravity = -20
        self.jump_force = 8
        self.is_grounded = False
        self.ground_check_distance = 0.1
        self.jump_cooldown = 0
        self.max_jump_cooldown = 2.0
        
        # Kopf des Feindes
        self.head = Entity(
            model='cube',
            color=color.light_gray,
            scale=(0.5, 0.5, 0.5),
            position=(0, 0.85, 0),
            parent=self
        )
        
        # Gesicht - Linkes Auge
        self.left_eye = Entity(
            model='cube',
            color=color.black,
            scale=(0.08, 0.08, 0.08),
            position=(-0.12, 0.9, 0.26),
            parent=self
        )
        
        # Gesicht - Rechtes Auge
        self.right_eye = Entity(
            model='cube',
            color=color.black,
            scale=(0.08, 0.08, 0.08),
            position=(0.12, 0.9, 0.26),
            parent=self
        )
        
        # Gesicht - Mund
        self.mouth = Entity(
            model='cube',
            color=color.black,
            scale=(0.15, 0.05, 0.05),
            position=(0, 0.75, 0.26),
            parent=self
        )
        
        # Linker Arm (Oberarm) - seitlich ausgestreckt
        self.left_arm = Entity(
            model='cube',
            color=color.dark_gray,
            scale=(0.5, 0.15, 0.15),
            position=(-0.55, 0.4, 0),
            rotation=(0, 0, 0),
            parent=self
        )
        
        # Linker Unterarm - seitlich ausgestreckt
        self.left_forearm = Entity(
            model='cube',
            color=color.dark_gray,
            scale=(0.4, 0.12, 0.12),
            position=(-0.9, 0.4, 0),
            rotation=(0, 0, 0),
            parent=self
        )
        
        # Linke Hand - seitlich ausgestreckt
        self.left_hand = Entity(
            model='cube',
            color=color.light_gray,
            scale=(0.15, 0.1, 0.1),
            position=(-1.15, 0.4, 0),
            parent=self
        )
        
        # Rechter Arm (Oberarm) - seitlich ausgestreckt
        self.right_arm = Entity(
            model='cube',
            color=color.dark_gray,
            scale=(0.5, 0.15, 0.15),
            position=(0.55, 0.4, 0),
            rotation=(0, 0, 0),
            parent=self
        )
        
        # Rechter Unterarm - seitlich ausgestreckt
        self.right_forearm = Entity(
            model='cube',
            color=color.dark_gray,
            scale=(0.4, 0.12, 0.12),
            position=(0.9, 0.4, 0),
            rotation=(0, 0, 0),
            parent=self
        )
        
        # Rechte Hand - seitlich ausgestreckt
        self.right_hand = Entity(
            model='cube',
            color=color.light_gray,
            scale=(0.15, 0.1, 0.1),
            position=(1.15, 0.4, 0),
            parent=self
        )
        
        # Linkes Bein (Oberschenkel)
        self.left_leg = Entity(
            model='cube',
            color=color.gray,
            scale=(0.2, 0.5, 0.2),
            position=(-0.15, -0.4, 0),
            parent=self
        )
        
        # Linkes Schienbein
        self.left_shin = Entity(
            model='cube',
            color=color.gray,
            scale=(0.18, 0.5, 0.18),
            position=(-0.15, -0.9, 0),
            parent=self
        )
        
        # Rechtes Bein (Oberschenkel)
        self.right_leg = Entity(
            model='cube',
            color=color.gray,
            scale=(0.2, 0.5, 0.2),
            position=(0.15, -0.4, 0),
            parent=self
        )
        
        # Rechtes Schienbein
        self.right_shin = Entity(
            model='cube',
            color=color.gray,
            scale=(0.18, 0.5, 0.18),
            position=(0.15, -0.9, 0),
            parent=self
        )
        
        # Linker Fuß
        self.left_foot = Entity(
            model='cube',
            color=color.black,
            scale=(0.25, 0.1, 0.4),
            position=(-0.15, -1.2, 0.1),
            parent=self
        )
        
        # Rechter Fuß
        self.right_foot = Entity(
            model='cube',
            color=color.black,
            scale=(0.25, 0.1, 0.4),
            position=(0.15, -1.2, 0.1),
            parent=self
        )
    
    def update(self):
        global waves_completed_on_map, enemies_spawned_this_wave, enemies_per_wave, wave_number
        if paused or not game_started:
            return
        
        # Entfernung zum Spieler berechnen
        distance_to_player = distance(self.position, player.position)
        
        # Jump-Cooldown verringern
        if self.jump_cooldown > 0:
            self.jump_cooldown -= time.dt
        
        # Boden-Erkennung
        self.check_ground()
        
        # Bewegungslogik
        self.move_timer += time.dt
        
        if distance_to_player > self.chase_distance:
            # Zu weit weg - zufällige Bewegung
            if self.move_timer >= self.move_interval:
                self.move_direction = Vec3(random.uniform(-1, 1), 0, random.uniform(-1, 1)).normalized()
                self.move_timer = 0
                self.move_interval = random.uniform(2, 4)
        elif distance_to_player > self.attack_distance:
            # Mittlere Entfernung - zum Spieler bewegen
            direction_to_player = (player.position - self.position).normalized()
            self.move_direction = direction_to_player
        else:
            # Nahe am Spieler - seitliche Bewegung für bessere Positionierung
            if self.move_timer >= self.move_interval * 0.5:
                perpendicular = Vec3(-self.move_direction.z, 0, self.move_direction.x)
                if random.random() > 0.5:
                    perpendicular = -perpendicular
                self.move_direction = perpendicular
                self.move_timer = 0
        
        # Horizontale Bewegung berechnen
        horizontal_velocity = self.move_direction * self.move_speed
        
        # Kollisionsprüfung und Sprung-Logik
        obstacle_ahead = self.check_obstacle_ahead(horizontal_velocity)
        
        if obstacle_ahead and self.is_grounded and self.jump_cooldown <= 0:
            # Über Hindernis springen
            self.velocity.y = self.jump_force
            self.jump_cooldown = self.max_jump_cooldown
            self.is_grounded = False
        
        # Physik anwenden
        self.apply_physics(horizontal_velocity)
        
        # Schießtimer aktualisieren
        self.shoot_timer += time.dt
        
        # Schießen wenn Timer abgelaufen und Spieler sichtbar
        if (self.shoot_timer >= self.shoot_interval and 
            distance_to_player <= self.sight_range and
            self.can_see_player()):
            self.shoot_at_player()
            self.shoot_timer = 0
            self.shoot_interval = random.uniform(1.0, 2.5)  # Schnelleres Schießen
    
    def check_ground(self):
        """Prüft ob der Feind auf dem Boden steht"""
        # Raycast nach unten
        ground_position = self.position.y - 0.6 - self.ground_check_distance
        
        # Prüfung mit Boden
        if ground and self.position.y <= ground.position.y + 0.6:
            self.is_grounded = True
            if self.velocity.y < 0:
                self.velocity.y = 0
            return
        
        # Prüfung mit anderen Map-Objekten
        for map_obj in map_objects:
            if map_obj != ground:
                # Prüfen ob Feind auf einem Objekt steht
                if (abs(self.position.x - map_obj.position.x) < map_obj.scale_x and
                    abs(self.position.z - map_obj.position.z) < map_obj.scale_z and
                    self.position.y >= map_obj.position.y + map_obj.scale_y - 0.1 and
                    self.position.y <= map_obj.position.y + map_obj.scale_y + 0.6):
                    self.is_grounded = True
                    if self.velocity.y < 0:
                        self.velocity.y = 0
                        self.position.y = map_obj.position.y + map_obj.scale_y + 0.6
                    return
        
        self.is_grounded = False
    
    def check_obstacle_ahead(self, horizontal_velocity):
        """Prüft ob ein Hindernis vor dem Feind ist"""
        check_distance = 1.5
        future_position = self.position + horizontal_velocity.normalized() * check_distance
        
        for map_obj in map_objects:
            if map_obj != ground:
                # Prüfen ob Hindernis im Weg ist
                if (abs(future_position.x - map_obj.position.x) < map_obj.scale_x + 0.5 and
                    abs(future_position.z - map_obj.position.z) < map_obj.scale_z + 0.5 and
                    map_obj.position.y + map_obj.scale_y > self.position.y and
                    map_obj.position.y < self.position.y + 1.2):
                    return True
        return False
    
    def apply_physics(self, horizontal_velocity):
        """Wendet Physik auf den Feind an"""
        # Schwerkraft anwenden
        if not self.is_grounded:
            self.velocity.y += self.gravity * time.dt
        
        # Gesamtgeschwindigkeit berechnen
        total_velocity = Vec3(horizontal_velocity.x, self.velocity.y, horizontal_velocity.z)
        
        # Neue Position berechnen
        new_position = self.position + total_velocity * time.dt
        
        # Horizontale Kollisionsprüfung
        can_move_x = True
        can_move_z = True
        
        # X-Achse prüfen
        test_pos_x = Vec3(new_position.x, self.position.y, self.position.z)
        for map_obj in map_objects:
            if map_obj != ground and self.check_collision_with_object(test_pos_x, map_obj):
                can_move_x = False
                break
        
        # Z-Achse prüfen
        test_pos_z = Vec3(self.position.x, self.position.y, new_position.z)
        for map_obj in map_objects:
            if map_obj != ground and self.check_collision_with_object(test_pos_z, map_obj):
                can_move_z = False
                break
        
        # Bewegung anwenden
        if can_move_x:
            self.position.x = new_position.x
        else:
            # Richtung ändern bei Kollision
            self.move_direction = Vec3(random.uniform(-1, 1), 0, random.uniform(-1, 1)).normalized()
        
        if can_move_z:
            self.position.z = new_position.z
        else:
            # Richtung ändern bei Kollision
            self.move_direction = Vec3(random.uniform(-1, 1), 0, random.uniform(-1, 1)).normalized()
        
        # Y-Position (Vertikale Bewegung)
        self.position.y = new_position.y
        
        # Verhindern, dass Feind unter den Boden fällt
        if ground and self.position.y < ground.position.y + 0.6:
            self.position.y = ground.position.y + 0.6
            self.velocity.y = 0
            self.is_grounded = True
    
    def check_collision_with_object(self, position, map_obj):
        """Prüft Kollision mit einem Map-Objekt"""
        return (abs(position.x - map_obj.position.x) < map_obj.scale_x + 0.3 and
                abs(position.z - map_obj.position.z) < map_obj.scale_z + 0.3 and
                abs(position.y - map_obj.position.y) < map_obj.scale_y + 0.6)
    
    def can_see_player(self):
        """Prüft ob der Feind den Spieler sehen kann (Sichtlinie frei)"""
        direction_to_player = (player.position - self.position).normalized()
        distance_to_player = distance(self.position, player.position)
        
        # Raycast zur Sichtlinie-Prüfung
        check_steps = int(distance_to_player * 2)  # Mehr Schritte für genauere Prüfung
        step_size = distance_to_player / check_steps
        
        for i in range(1, check_steps):
            check_position = self.position + direction_to_player * (step_size * i)
            
            # Prüfen ob ein Hindernis die Sicht blockiert
            for map_obj in map_objects:
                if map_obj != ground:  # Boden ignorieren
                    # Prüfen ob der Raycast-Punkt innerhalb eines Objekts liegt
                    if (abs(check_position.x - map_obj.position.x) < map_obj.scale_x and
                        abs(check_position.y - map_obj.position.y) < map_obj.scale_y and
                        abs(check_position.z - map_obj.position.z) < map_obj.scale_z):
                        return False  # Sicht blockiert
        
        return True  # Freie Sicht zum Spieler
    
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
    global enemies, enemies_spawned_this_wave
    map_data = maps[current_map]
    map_size = map_data["size"]
    
    for i in range(count):
        # Spawn-Position basierend auf Map-Typ anpassen
        if map_data["type"] == "circle":
            # Innerhalb des Kreises spawnen
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(3, map_size - 3)
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
        elif map_data["type"] == "maze":
            # In offenen Bereichen des Labyrinths spawnen
            spawn_areas = [(-15, -15), (15, 15), (-15, 15), (15, -15), (0, 10), (-10, 0), (10, -10)]
            area = random.choice(spawn_areas)
            x = area[0] + random.uniform(-2, 2)
            z = area[1] + random.uniform(-2, 2)
        else:
            # Standard-Spawn für andere Maps
            x = random.uniform(-map_size + 3, map_size - 3)
            z = random.uniform(-map_size + 3, map_size - 3)
        
        y = 1  # Feinde stehen auf dem Boden
        
        enemy = Enemy(position=(x, y, z))
        enemies.append(enemy)
    
    enemies_spawned_this_wave += count

# Feinde erstellen
enemies = []
spawn_enemies(enemies_per_wave)

# Spieler-Kugel-Klasse
class Bullet(Entity):
    def __init__(self, weapon_stats, **kwargs):
        super().__init__(
            model='sphere',
            color=weapon_stats['bullet_color'],
            scale=0.1,
            **kwargs
        )
        self.speed = weapon_stats['bullet_speed']
        self.damage = weapon_stats['damage']
        self.lifetime = 20.0
        self.direction = camera.forward
        
    def update(self):
        global score, enemies_killed_this_wave, wave_number, enemies_per_wave, waves_completed_on_map, enemies_spawned_this_wave
        
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
            if dist < 1.5:  # Optimierte Kollision mit Feind für Fernkampf
                
                # Partikeleffekte erstellen
                ParticleSystem.create_blood_effect(enemy.position)
                ParticleSystem.create_explosion(enemy.position, color.red)
                
                # Feind eliminieren
                enemies.remove(enemy)
                destroy(enemy)
                destroy(self)
                
                # Score erhöhen
                score += 100 * wave_number
                enemies_killed_this_wave += 1
                
                # Prüfen ob alle Feinde der Welle eliminiert wurden
                if enemies_killed_this_wave >= enemies_per_wave and len(enemies) == 0:
                    wave_number += 1
                    enemies_killed_this_wave = 0
                    enemies_spawned_this_wave = 0
                    waves_completed_on_map += 1
                    
                    # Neue Wellen-Größe bestimmen
                    wave_in_cycle = ((wave_number - 1) % 3) + 1
                    enemies_per_wave = max_enemies_per_wave[wave_in_cycle]
                    
                    # Prüfen ob 3 Wellen auf dieser Map abgeschlossen
                    if waves_completed_on_map >= waves_per_map:
                        # Zur nächsten Map wechseln
                        next_map = current_map + 1
                        if next_map > len(maps):
                            next_map = 1  # Zurück zur ersten Map
                        
                        load_map(next_map)
                        waves_completed_on_map = 0
                        
                        # Spieler zur Mitte der neuen Map teleportieren
                        player.position = (0, 1, 0)
                        
                        print(f"Map gewechselt zu: {maps[current_map]['name']}")
                    
                    # Neue Welle spawnen
                    spawn_enemies(enemies_per_wave)
                    print(f"Welle {wave_number} gestartet - {enemies_per_wave} Feinde")
                
                # Nachspawnen falls noch Feinde für diese Welle übrig sind
                elif (len(enemies) == 0 and 
                      enemies_spawned_this_wave < enemies_per_wave):
                    remaining = enemies_per_wave - enemies_spawned_this_wave
                    spawn_count = min(5, remaining)  # Maximal 5 auf einmal spawnen
                    spawn_enemies(spawn_count)
                return
                
        # Prüfung auf Kollision mit Map-Objekten
        for map_obj in map_objects:
            if map_obj != ground:  # Boden ignorieren
                # Weniger aggressive Kollisionserkennung für bessere Fernkampf-Fähigkeiten
                if (abs(self.position.x - map_obj.position.x) < map_obj.scale_x - 0.8 and
                    abs(self.position.y - map_obj.position.y) < map_obj.scale_y - 0.8 and
                    abs(self.position.z - map_obj.position.z) < map_obj.scale_z - 0.8):
                    destroy(self)
                    return

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
        self.lifetime = 12.0
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
            
            # Schaden-Partikeleffekt
            ParticleSystem.create_blood_effect(player.position)
            
            destroy(self)
            return
                
        # Prüfung auf Kollision mit Map-Objekten
        for map_obj in map_objects:
            if map_obj != ground:  # Boden ignorieren
                # Noch präzisere Kollisionserkennung - deutlich kleinere Hitbox
                if (abs(self.position.x - map_obj.position.x) < map_obj.scale_x - 0.3 and
                    abs(self.position.y - map_obj.position.y) < map_obj.scale_y - 0.3 and
                    abs(self.position.z - map_obj.position.z) < map_obj.scale_z - 0.3):
                    destroy(self)
                    return

# Game Over Menü erstellen
def show_game_over_menu():
    global game_over_menu, game_over_text, restart_button, quit_button
    
    # Hintergrund für Game Over Menü
    game_over_menu = Entity(model='cube', color=color.black, scale=(2, 2, 1), position=(0, 0, -0.1), parent=camera.ui, alpha=0.8)
    
    # Game Over Text
    game_over_text = Text('GAME OVER', origin=(0, 0), scale=3, color=color.red, position=(0, 0.2, -0.2), parent=camera.ui)
    
    # Restart Button
    restart_button = Button(text='Spiel neu starten', color=color.green, scale=(0.3, 0.1), position=(-0.2, -0.1, -0.2), parent=camera.ui)
    restart_button.on_click = restart_game
    
    # Quit Button  
    quit_button = Button(text='Beenden', color=color.red, scale=(0.3, 0.1), position=(0.2, -0.1, -0.2), parent=camera.ui)
    quit_button.on_click = quit_game

# Spiel neu starten
def restart_game():
    global current_hp, current_stamina, game_over, enemies, score, wave_number, enemies_killed_this_wave
    
    # Game Over Menü entfernen
    destroy(game_over_menu)
    destroy(game_over_text)
    destroy(restart_button)
    destroy(quit_button)
    
    # Spieler zurücksetzen
    current_hp = max_hp
    current_stamina = max_stamina
    score = 0
    wave_number = 1
    enemies_killed_this_wave = 0
    player.position = (0, 1, 0)
    game_over = False
    mouse.locked = True
    
    # Map-System zurücksetzen
    global waves_completed_on_map, enemies_per_wave, enemies_spawned_this_wave
    waves_completed_on_map = 0
    enemies_per_wave = 10  # Zurück zu Welle 1
    enemies_spawned_this_wave = 0
    load_map(1)  # Zurück zur ersten Map
    
    # Fall-System zurücksetzen
    global is_falling, fall_start_time
    is_falling = False
    fall_start_time = 0
    
    # Alle Feinde entfernen und neue spawnen
    for enemy in enemies[:]:
        destroy(enemy)
    enemies.clear()
    spawn_enemies(enemies_per_wave)

# Fall-Tod-System
def check_fall_death():
    global is_falling, fall_start_time, current_hp
    
    # Prüfen ob Spieler unter die Fall-Schwelle gefallen ist
    if player.position.y < fall_threshold:
        if not is_falling:
            # Fall beginnt
            is_falling = True
            fall_start_time = time.time()
            print(f"Spieler fällt! Tod in {fall_death_delay} Sekunden...")
        else:
            # Prüfen ob 4 Sekunden vergangen sind
            if time.time() - fall_start_time >= fall_death_delay:
                # Spieler stirbt durch Fall
                current_hp = 0
                print("Spieler ist durch Fall gestorben!")
                # Partikeleffekt für Fall-Tod
                ParticleSystem.create_explosion(player.position, color.red)
    else:
        # Spieler ist wieder auf sicherem Boden
        if is_falling:
            is_falling = False
            print("Spieler ist wieder sicher!")

# Spiel beenden
def quit_game():
    application.quit()

# Waffe wechseln
def switch_weapon(new_weapon):
    global current_weapon
    if new_weapon in weapons:
        current_weapon = new_weapon

# Salvenfeuer-Update-Funktion
def update_burst_fire():
    global is_bursting, burst_shots_fired, burst_start_time
    
    if is_bursting:
        current_time = time.time()
        weapon = weapons[current_weapon]
        
        # Prüfen ob Zeit für nächsten Schuss in der Salve
        if (current_time - burst_start_time >= burst_shots_fired * weapon['burst_delay'] and
            burst_shots_fired < weapon['burst_count'] and
            weapon['current_ammo'] > 0):
            
            fire_single_shot()
            burst_shots_fired += 1
        
        # Salve beenden wenn alle Schüsse abgefeuert oder keine Munition
        if (burst_shots_fired >= weapon['burst_count'] or 
            weapon['current_ammo'] <= 0):
            is_bursting = False
            burst_shots_fired = 0

# Nachladen
def reload_weapon():
    global is_reloading, reload_start_time, is_bursting
    if (not is_reloading and 
        not is_bursting and 
        weapons[current_weapon]['current_ammo'] < weapons[current_weapon]['max_ammo']):
        is_reloading = True
        reload_start_time = time.time()
        # Salvenfeuer unterbrechen falls aktiv
        is_bursting = False

# Einzelschuss abfeuern
def fire_single_shot():
    weapon = weapons[current_weapon]
    
    if weapon['current_ammo'] > 0:
        # Kugel erstellen
        bullet = Bullet(weapon, position=camera.world_position)
        
        # Munition verringern
        weapon['current_ammo'] -= 1
        
        # Verbesserter Muzzle Flash Effekt
        muzzle_flash = Entity(model='sphere', color=color.yellow, scale=0.3, 
                             position=camera.world_position + camera.forward * 2)
        muzzle_flash.animate_scale(0, duration=0.1)
        destroy(muzzle_flash, delay=0.1)
        
        # Zusätzliche Muzzle-Partikel
        for i in range(5):
            spark = Entity(
                model='cube',
                color=color.orange,
                scale=0.02,
                position=camera.world_position + camera.forward * 2 + Vec3(
                    random.uniform(-0.1, 0.1),
                    random.uniform(-0.1, 0.1),
                    random.uniform(-0.1, 0.1)
                )
            )
            spark.animate_position(
                spark.position + camera.forward * random.uniform(1, 3),
                duration=0.3
            )
            spark.animate_scale(0, duration=0.3)
            destroy(spark, delay=0.3)

# Schießen (mit Salvenfeuer-Unterstützung)
def shoot():
    global last_shot_time, is_bursting, burst_shots_fired, burst_start_time
    current_time = time.time()
    weapon = weapons[current_weapon]
    
    if (current_time - last_shot_time >= weapon['fire_rate'] and 
        weapon['current_ammo'] > 0 and 
        not is_reloading and 
        not is_bursting):
        
        if weapon['burst_mode']:
            # Salvenfeuer starten
            is_bursting = True
            burst_shots_fired = 0
            burst_start_time = current_time
            last_shot_time = current_time
            
            # Erste Kugel sofort abfeuern
            fire_single_shot()
            burst_shots_fired = 1
        else:
            # Einzelschuss
            fire_single_shot()
            last_shot_time = current_time

# Update-Funktion für Stamina-System
def update():
    global current_stamina, is_sprinting, game_over, is_reloading, game_started
    
    if paused or game_over:
        return
    
    # Game Over prüfen
    if current_hp <= 0 and not game_over:
        game_over = True
        mouse.locked = False
        show_game_over_menu()
        return
    
    # Nachladen prüfen
    if is_reloading:
        current_time = time.time()
        if current_time - reload_start_time >= weapons[current_weapon]['reload_time']:
            weapons[current_weapon]['current_ammo'] = weapons[current_weapon]['max_ammo']
            is_reloading = False
    
    # Salvenfeuer-System verwalten
    update_burst_fire()
    
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
    
    # Position des blauen Balkens anpassen, damit er links am Hintergrund ausgerichtet ist
    stamina_bar.x = 0.6 - (0.3 * (1 - stamina_percentage)) / 2
    
    # Stamina-Leiste bleibt immer blau
    stamina_bar.color = color.blue
    
    # HP-Leiste aktualisieren
    hp_percentage = current_hp / max_hp
    hp_bar.scale_x = 0.3 * hp_percentage
    
    # Position des roten Balkens anpassen, damit er links am Hintergrund ausgerichtet ist
    hp_bar.x = -0.6 - (0.3 * (1 - hp_percentage)) / 2
    
    # UI Texte aktualisieren
    weapon = weapons[current_weapon]
    ammo_text.text = f'Munition: {weapon["current_ammo"]}/{weapon["max_ammo"]}'
    weapon_text.text = f'Waffe: {current_weapon.upper()}'
    score_text.text = f'Score: {score}'
    wave_text.text = f'Welle: {wave_number}'
    map_text.text = f'Map: {maps[current_map]["name"]}'
    
    # Nachladen-Text anzeigen
    if is_reloading:
        reload_text.text = 'NACHLADEN...'
        reload_text.enabled = True
    else:
        reload_text.enabled = False
    
    # Fall-Erkennung prüfen
    check_fall_death()

# Eingabe-Funktion für Schießen
def input(key):
    global paused, pause_text, game_started, enemies_spawned_this_wave
    
    if key == 'escape' and not game_over:
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
    
    if not paused and not game_over and key == 'left mouse down':
        shoot()
    
    # Waffe wechseln
    if not paused and not game_over:
        if key == '1':
            switch_weapon('pistol')
        elif key == '2':
            switch_weapon('rifle')
        elif key == '3':
            switch_weapon('shotgun')
        elif key == '4':
            switch_weapon('machinegun')
        elif key == 'r':
            reload_weapon()
        # Map wechseln
        elif key == 'n':  # Nächste Map
            next_map = current_map + 1
            if next_map > len(maps):
                next_map = 1
            load_map(next_map)
            # Feinde für neue Map spawnen
            for enemy in enemies[:]:
                destroy(enemy)
            enemies.clear()
            enemies_spawned_this_wave = 0
            spawn_enemies(enemies_per_wave)
        elif key == 'm':  # Vorherige Map
            prev_map = current_map - 1
            if prev_map < 1:
                prev_map = len(maps)
            load_map(prev_map)
            # Feinde für neue Map spawnen
            for enemy in enemies[:]:
                destroy(enemy)
            enemies.clear()
            enemies_spawned_this_wave = 0
            spawn_enemies(enemies_per_wave)

# Spiel starten
app.run()
