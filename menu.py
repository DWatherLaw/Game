from ursina import *
import json

class MainMenu(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, ignore_paused=True)

        self.menu_active = False
        self.highscore_active = False
        
        # Menü-Hintergrund
        self.menu_background = Entity(model='cube', color=color.dark_gray, scale=(2, 2, 1), position=(0, 0, -0.5), parent=self, alpha=0.9)
        
        # Titel
        self.title = Text('ARENA SHOOTER', origin=(0, 0), scale=3, color=color.yellow, position=(0, 0.3, -0.1), parent=self)
        
        # Hauptmenü-Container
        self.main_menu = Entity(parent=self, enabled=False)
        
        # Hauptmenü-Buttons
        self.start_button = Button(parent=self.main_menu, text='Spiel starten', color=color.cyan, scale=(0.3, 0.1), y=0.1)
        self.start_button.text_entity.color = color.black
        self.highscore_button = Button(parent=self.main_menu, text='Highscores', color=color.cyan, scale=(0.3, 0.1), y=-0.05)
        self.highscore_button.text_entity.color = color.black
        self.quit_button = Button(parent=self.main_menu, text='Beenden', color=color.orange, scale=(0.3, 0.1), y=-0.2)
        self.quit_button.text_entity.color = color.black
        
        self.quit_button.on_click = application.quit
        
        # Highscore-Menü
        self.highscore_menu = Entity(parent=self, enabled=False)
        self.highscore_list = Text(parent=self.highscore_menu, text='', origin=(0, 0.5), y=0.4, scale=1.5)
        self.back_button_highscore = Button(parent=self.highscore_menu, text='Zurück', color=color.cyan, scale=(0.3, 0.1), y=-0.4)
        self.back_button_highscore.text_entity.color = color.black
        
        # Button-Aktionen
        self.highscore_button.on_click = self.show_highscore_menu
        self.back_button_highscore.on_click = self.show_main_menu

    def show_main_menu(self):
        self.menu_active = True
        self.highscore_active = False
        self.enabled = True
        self.main_menu.enable()
        self.highscore_menu.disable()
        self.title.enabled = True
        self.menu_background.enabled = True

    def show_highscore_menu(self):
        self.menu_active = False
        self.highscore_active = True
        self.main_menu.disable()
        self.highscore_menu.enable()
        self.load_highscores()

    def hide_all_menus(self):
        self.menu_active = False
        self.highscore_active = False
        self.main_menu.disable()
        self.highscore_menu.disable()
        self.title.enabled = False
        self.menu_background.enabled = False
        self.enabled = False

    def load_highscores(self):
        try:
            with open('highscores.json', 'r') as f:
                highscores = json.load(f)
            
            highscore_str = 'Highscores:\n\n' + '\n'.join([f'{i+1}. {score}' for i, score in enumerate(highscores)])
            self.highscore_list.text = highscore_str
        except (FileNotFoundError, json.JSONDecodeError):
            self.highscore_list.text = 'Noch keine Highscores!'

    def save_highscore(self, new_score):
        try:
            with open('highscores.json', 'r') as f:
                highscores = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            highscores = []
            
        highscores.append(new_score)
        highscores.sort(reverse=True)
        highscores = highscores[:10]  # Nur die Top 10 speichern
        
        with open('highscores.json', 'w') as f:
            json.dump(highscores, f)
