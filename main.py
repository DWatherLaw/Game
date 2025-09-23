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
        'bullet_color': color.yellow
    },
    'rifle': {
        'damage': 40,
        'fire_rate': 0.3,
        'max_ammo': 30,
        'current_ammo': 30,
        'reload_time': 3.0,
        'bullet_speed': 25,
        'bullet_color': color.orange
    },
    'shotgun': {
        'damage': 60,
        'fire_rate': 1.0,
        'max_ammo': 8,
        'current_ammo': 8,
        'reload_time': 2.5,
        'bullet_speed': 18,
        'bullet_color': color.red
    }
}

# Schießsystem
last_shot_time = 0
is_reloading = False
reload_start_time = 0

# Punktesystem
score = 0
wave_number = 1
enemies_killed_this_wave = 0
enemies_per_wave = 5

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
    def __init__(self, weapon_stats, **kwargs):
        super().__init__(
            model='sphere',
            color=weapon_stats['bullet_color'],
            scale=0.1,
            **kwargs
        )
        self.speed = weapon_stats['bullet_speed']
        self.damage = weapon_stats['damage']
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
                global score, enemies_killed_this_wave, wave_number
                
                # Feind eliminieren
                enemies.remove(enemy)
                destroy(enemy)
                destroy(self)
                
                # Score erhöhen
                score += 100 * wave_number
                enemies_killed_this_wave += 1
                
                # Prüfen ob Welle abgeschlossen
                if enemies_killed_this_wave >= enemies_per_wave:
                    wave_number += 1
                    enemies_killed_this_wave = 0
                    spawn_enemies(5 + wave_number)  # Mehr Feinde pro Welle
                elif len(enemies) == 0:
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
    global current_hp, current_stamina, game_over, enemies
    
    # Game Over Menü entfernen
    destroy(game_over_menu)
    destroy(game_over_text)
    destroy(restart_button)
    destroy(quit_button)
    
    # Spieler zurücksetzen
    current_hp = max_hp
    current_stamina = max_stamina
    player.position = (0, 1, 0)
    game_over = False
    mouse.locked = True
    
    # Alle Feinde entfernen und neue spawnen
    for enemy in enemies[:]:
        destroy(enemy)
    enemies.clear()
    spawn_enemies(5)

# Spiel beenden
def quit_game():
    application.quit()

# Waffe wechseln
def switch_weapon(new_weapon):
    global current_weapon
    if new_weapon in weapons:
        current_weapon = new_weapon

# Nachladen
def reload_weapon():
    global is_reloading, reload_start_time
    if not is_reloading and weapons[current_weapon]['current_ammo'] < weapons[current_weapon]['max_ammo']:
        is_reloading = True
        reload_start_time = time.time()

# Schießen
def shoot():
    global last_shot_time
    current_time = time.time()
    weapon = weapons[current_weapon]
    
    if (current_time - last_shot_time >= weapon['fire_rate'] and 
        weapon['current_ammo'] > 0 and 
        not is_reloading):
        
        # Kugel erstellen
        bullet = Bullet(weapon, position=camera.world_position)
        
        # Munition verringern
        weapon['current_ammo'] -= 1
        last_shot_time = current_time
        
        # Muzzle Flash Effekt
        muzzle_flash = Entity(model='sphere', color=color.yellow, scale=0.3, 
                             position=camera.world_position + camera.forward * 2)
        destroy(muzzle_flash, delay=0.1)

# Update-Funktion für Stamina-System
def update():
    global current_stamina, is_sprinting, game_over, is_reloading
    
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
    
    # UI Texte aktualisieren
    weapon = weapons[current_weapon]
    ammo_text.text = f'Munition: {weapon["current_ammo"]}/{weapon["max_ammo"]}'
    weapon_text.text = f'Waffe: {current_weapon.upper()}'
    score_text.text = f'Score: {score}'
    wave_text.text = f'Welle: {wave_number}'
    
    # Nachladen-Text anzeigen
    if is_reloading:
        reload_text.text = 'NACHLADEN...'
        reload_text.enabled = True
    else:
        reload_text.enabled = False

# Eingabe-Funktion für Schießen
def input(key):
    global paused, pause_text
    
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
        elif key == 'r':
            reload_weapon()

# Spiel starten
app.run()
