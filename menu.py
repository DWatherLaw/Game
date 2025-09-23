from ursina import *
import json

class MainMenu(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, ignore_paused=True)

        self.menu_active = True
        self.highscore_active = False
        
        # Hauptmenü-Container
        self.main_menu = Entity(parent=self, enabled=True)
        
        # Hauptmenü-Buttons
        self.start_button = Button(parent=self.main_menu, text='Spiel starten', color=color.azure, scale=(0.3, 0.1), y=0.1)
        self.highscore_button = Button(parent=self.main_menu, text='Highscores', color=color.azure, scale=(0.3, 0.1), y=-0.05)
        self.quit_button = Button(parent=self.main_menu, text='Beenden', color=color.red, scale=(0.3, 0.1), y=-0.2)
        
        self.quit_button.on_click = application.quit
        
        # Highscore-Menü
        self.highscore_menu = Entity(parent=self, enabled=False)
        self.highscore_list = Text(parent=self.highscore_menu, text='', origin=(0, 0.5), y=0.4, scale=1.5)
        self.back_button_highscore = Button(parent=self.highscore_menu, text='Zurück', color=color.azure, scale=(0.3, 0.1), y=-0.4)
        
        # Button-Aktionen
        self.highscore_button.on_click = self.show_highscore_menu
        self.back_button_highscore.on_click = self.show_main_menu

    def show_main_menu(self):
        self.menu_active = True
        self.highscore_active = False
        self.main_menu.enable()
        self.highscore_menu.disable()

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
