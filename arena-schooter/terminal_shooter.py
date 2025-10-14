import os
import sys
import time
import random
import threading
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Position:
    x: int
    y: int

@dataclass
class Bullet:
    pos: Position
    direction: Tuple[int, int]

@dataclass
class Enemy:
    pos: Position
    health: int = 1

class TerminalShooter:
    def __init__(self, width=40, height=20):
        self.width = width
        self.height = height
        self.player_pos = Position(width // 2, height - 2)
        self.bullets: List[Bullet] = []
        self.enemies: List[Enemy] = []
        self.score = 0
        self.running = True
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def draw_game(self):
        # Erstelle leeres Spielfeld
        field = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        # Zeichne Rahmen
        for x in range(self.width):
            field[0][x] = '#'
            field[self.height-1][x] = '#'
        for y in range(self.height):
            field[y][0] = '#'
            field[y][self.width-1] = '#'
            
        # Zeichne Spieler
        if 0 <= self.player_pos.y < self.height and 0 <= self.player_pos.x < self.width:
            field[self.player_pos.y][self.player_pos.x] = 'P'
            
        # Zeichne Kugeln
        for bullet in self.bullets:
            if 0 <= bullet.pos.y < self.height and 0 <= bullet.pos.x < self.width:
                field[bullet.pos.y][bullet.pos.x] = '|'
                
        # Zeichne Gegner
        for enemy in self.enemies:
            if 0 <= enemy.pos.y < self.height and 0 <= enemy.pos.x < self.width:
                field[enemy.pos.y][enemy.pos.x] = 'E'
        
        # Ausgabe
        self.clear_screen()
        print(f"Score: {self.score}")
        print("Steuerung: A/D = Links/Rechts, W = Schießen, Q = Beenden")
        print()
        
        for row in field:
            print(''.join(row))
            
    def move_player(self, direction):
        new_x = self.player_pos.x + direction
        if 1 <= new_x < self.width - 1:
            self.player_pos.x = new_x
            
    def shoot(self):
        bullet = Bullet(
            pos=Position(self.player_pos.x, self.player_pos.y - 1),
            direction=(0, -1)
        )
        self.bullets.append(bullet)
        
    def spawn_enemy(self):
        if random.random() < 0.3:  # 30% Chance pro Frame
            x = random.randint(1, self.width - 2)
            enemy = Enemy(pos=Position(x, 1))
            self.enemies.append(enemy)
            
    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.pos.y += bullet.direction[1]
            if bullet.pos.y < 0 or bullet.pos.y >= self.height:
                self.bullets.remove(bullet)
                
    def update_enemies(self):
        for enemy in self.enemies[:]:
            enemy.pos.y += 1
            if enemy.pos.y >= self.height - 1:
                self.enemies.remove(enemy)
                
    def check_collisions(self):
        # Kugel-Gegner Kollisionen
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.pos.x == enemy.pos.x and bullet.pos.y == enemy.pos.y:
                    self.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.score += 10
                    break
                    
        # Spieler-Gegner Kollisionen
        for enemy in self.enemies:
            if enemy.pos.x == self.player_pos.x and enemy.pos.y == self.player_pos.y:
                print("\nGame Over! Du wurdest getroffen!")
                print(f"Endpunktzahl: {self.score}")
                self.running = False
                return
                
    def get_input(self):
        """Nicht-blockierende Eingabe (vereinfacht)"""
        try:
            import msvcrt
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8').lower()
                return key
        except ImportError:
            # Für Unix-Systeme (vereinfacht)
            pass
        return None
        
    def run(self):
        print("Arena Shooter gestartet!")
        print("Drücke eine Taste um zu beginnen...")
        input()
        
        last_time = time.time()
        
        while self.running:
            current_time = time.time()
            
            # Eingabe verarbeiten
            key = self.get_input()
            if key == 'a':
                self.move_player(-1)
            elif key == 'd':
                self.move_player(1)
            elif key == 'w':
                self.shoot()
            elif key == 'q':
                self.running = False
                
            # Spiel-Update (60 FPS)
            if current_time - last_time > 1/10:  # 10 FPS für bessere Sichtbarkeit
                self.spawn_enemy()
                self.update_bullets()
                self.update_enemies()
                self.check_collisions()
                self.draw_game()
                last_time = current_time
                
            time.sleep(0.05)  # Kurze Pause
            
        print("\nSpiel beendet!")

if __name__ == "__main__":
    game = TerminalShooter()
    game.run()
