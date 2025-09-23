from ursina import *

class MainMenu:
    def __init__(self):
        self.menu_active = True
        self.settings_active = False
        self.highscore_active = False
        
        # Menü-Hintergrund
        self.background = Entity(model='cube', color=color.dark_gray, scale=(2, 2, 1), position=(0, 0, -0.5), parent=camera.ui)
        
        # Titel
        self.title = Text('ARENA SHOOTER', origin=(0, 0), scale=4, color=color.white, position=(0, 0.3, -0.1), parent=camera.ui)
        
        # Hauptmenü Buttons
        self.start_button = Button(text='Spiel starten', color=color.green, scale=(0.4, 0.1), position=(0, 0.1, -0.1), parent=camera.ui)
        self.settings_button = Button(text='Einstellungen', color=color.blue, scale=(0.4, 0.1), position=(0, -0.05, -0.1), parent=camera.ui)
        self.highscore_button = Button(text='Highscores', color=color.orange, scale=(0.4, 0.1), position=(0, -0.2, -0.1), parent=camera.ui)
        self.quit_button = Button(text='Beenden', color=color.red, scale=(0.4, 0.1), position=(0, -0.35, -0.1), parent=camera.ui)
        
        # Button-Funktionen zuweisen
        self.start_button.on_click = self.start_game
        self.settings_button.on_click = self.show_settings
        self.highscore_button.on_click = self.show_highscores
        self.quit_button.on_click = application.quit
        
        # Einstellungsmenü Elemente (versteckt)
        self.settings_elements = []
        self.create_settings_menu()
        
        # Highscore Elemente (versteckt)
        self.highscore_elements = []
        self.create_highscore_menu()
        
        # Alle Menü-Elemente sammeln
        self.main_menu_elements = [self.background, self.title, self.start_button, 
                                  self.settings_button, self.highscore_button, self.quit_button]
    
    def create_settings_menu(self):
        # Einstellungen Titel
        settings_title = Text('EINSTELLUNGEN', origin=(0, 0), scale=3, color=color.white, position=(0, 0.3, -0.1), parent=camera.ui)
        settings_title.enabled = False
        
        # Lautstärke Einstellung (Platzhalter)
        volume_text = Text('Lautstärke: 100%', origin=(0, 0), scale=1.5, color=color.white, position=(0, 0.1, -0.1), parent=camera.ui)
        volume_text.enabled = False
        
        # Grafik Einstellung (Platzhalter)
        graphics_text = Text('Grafik: Hoch', origin=(0, 0), scale=1.5, color=color.white, position=(0, 0, -0.1), parent=camera.ui)
        graphics_text.enabled = False
        
        # Zurück Button
        back_button = Button(text='Zurück', color=color.gray, scale=(0.3, 0.1), position=(0, -0.3, -0.1), parent=camera.ui)
        back_button.on_click = self.show_main_menu
        back_button.enabled = False
        
        self.settings_elements = [settings_title, volume_text, graphics_text, back_button]
    
    def create_highscore_menu(self):
        # Highscore Titel
        highscore_title = Text('HIGHSCORES', origin=(0, 0), scale=3, color=color.white, position=(0, 0.3, -0.1), parent=camera.ui)
        highscore_title.enabled = False
        
        # Highscore Liste laden
        scores = self.load_highscores()
        
        # Top 5 Scores anzeigen
        score_texts = []
        for i, score in enumerate(scores[:5]):
            score_text = Text(f'{i+1}. {score} Punkte', origin=(0, 0), scale=1.5, color=color.yellow, 
                            position=(0, 0.15 - i*0.08, -0.1), parent=camera.ui)
            score_text.enabled = False
            score_texts.append(score_text)
        
        # Zurück Button
        back_button = Button(text='Zurück', color=color.gray, scale=(0.3, 0.1), position=(0, -0.3, -0.1), parent=camera.ui)
        back_button.on_click = self.show_main_menu
        back_button.enabled = False
        
        self.highscore_elements = [highscore_title, back_button] + score_texts
    
    def load_highscores(self):
        try:
            with open('highscores.txt', 'r') as f:
                scores = [int(line.strip()) for line in f.readlines()]
                return sorted(scores, reverse=True)
        except FileNotFoundError:
            return [0, 0, 0, 0, 0]
    
    def save_highscore(self, score):
        scores = self.load_highscores()
        scores.append(score)
        scores = sorted(scores, reverse=True)[:10]  # Top 10 behalten
        
        with open('highscores.txt', 'w') as f:
            for score in scores:
                f.write(f'{score}\n')
    
    def start_game(self):
        self.hide_all_menus()
        # Game wird in main.py gestartet
    
    def show_settings(self):
        self.hide_all_menus()
        self.settings_active = True
        for element in self.settings_elements:
            element.enabled = True
    
    def show_highscores(self):
        self.hide_all_menus()
        self.highscore_active = True
        # Highscores neu laden
        self.refresh_highscores()
        for element in self.highscore_elements:
            element.enabled = True
    
    def show_main_menu(self):
        self.hide_all_menus()
        self.menu_active = True
        for element in self.main_menu_elements:
            element.enabled = True
    
    def hide_all_menus(self):
        self.menu_active = False
        self.settings_active = False
        self.highscore_active = False
        
        for element in self.main_menu_elements:
            element.enabled = False
        for element in self.settings_elements:
            element.enabled = False
        for element in self.highscore_elements:
            element.enabled = False
    
    def refresh_highscores(self):
        # Alte Score-Texte entfernen
        for element in self.highscore_elements[2:]:  # Titel und Button überspringen
            destroy(element)
        
        # Neue Scores laden
        scores = self.load_highscores()
        score_texts = []
        for i, score in enumerate(scores[:5]):
            score_text = Text(f'{i+1}. {score} Punkte', origin=(0, 0), scale=1.5, color=color.yellow, 
                            position=(0, 0.15 - i*0.08, -0.1), parent=camera.ui)
            score_text.enabled = False
            score_texts.append(score_text)
        
        self.highscore_elements = self.highscore_elements[:2] + score_texts
    
    def cleanup(self):
        for element in self.main_menu_elements + self.settings_elements + self.highscore_elements:
            destroy(element)
