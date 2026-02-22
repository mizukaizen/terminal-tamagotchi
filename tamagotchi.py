#!/usr/bin/env python3
"""
Terminal Tamagotchi - Authentic retro design
"""

import json
import random
from datetime import datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal, Center
from textual.widgets import Static, Label
from textual.reactive import reactive


class GameData:
    """Manages game state persistence"""

    def __init__(self, save_file: Path = Path.home() / ".tamagotchi_save.json"):
        self.save_file = save_file

    def load(self) -> dict:
        if self.save_file.exists():
            try:
                with open(self.save_file) as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "name": "Blob",
            "age_hours": 0,
            "hunger": 4,  # 0-4 hearts
            "happy": 4,
            "health": 4,
            "weight": 10,
            "discipline": 2,
            "last_save": datetime.now().isoformat(),
        }

    def save(self, data: dict):
        data["last_save"] = datetime.now().isoformat()
        with open(self.save_file, "w") as f:
            json.dump(data, f, indent=2)


class TamagotchiScreen(Static):
    """The main Tamagotchi egg-shaped screen"""

    hunger = reactive(4)
    happy = reactive(4)
    health = reactive(4)
    age = reactive(0)
    weight = reactive(10)
    name = reactive("Blob")
    emotion = reactive("normal")
    char_frame = reactive(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.char_pos = 15

    def on_mount(self):
        self.set_interval(0.5, self.animate_character)
        self.set_interval(2.0, self.move_character)

    def animate_character(self):
        self.char_frame = (self.char_frame + 1) % 4

    def move_character(self):
        if random.random() < 0.7:  # Sometimes move
            direction = random.choice([-1, 1])
            self.char_pos = max(0, min(25, self.char_pos + direction))

    def get_character(self) -> str:
        """Get character sprite based on emotion"""
        sprites = {
            "normal": [
                "  .-.\n (o.o)\n  > ^",
                "  .-.\n (o.o)\n  ^ <",
            ],
            "happy": [
                "  \\o/\n (^.^)\n  > <",
                "  \\o/\n (^o^)\n  < >",
            ],
            "sad": [
                "  .-.\n (T.T)\n  ...",
                "  .-.\n (;.;)\n  ...",
            ],
            "hungry": [
                "  .-.\n (O.O)\n  ~~~",
                "  .-.\n (@.@)\n  ~~~",
            ],
            "sleep": [
                "  .-.\n (- -)\n z z z",
                "  .-.\n (- -)\n  zzZ",
            ],
        }

        emotion_sprites = sprites.get(self.emotion, sprites["normal"])
        return emotion_sprites[self.char_frame % 2]

    def render(self) -> str:
        """Render the complete Tamagotchi screen"""

        # Hearts display
        heart_full = chr(0x2665)  # ♥
        heart_empty = chr(0x2661)  # ♡

        hunger_hearts = heart_full * self.hunger + heart_empty * (4 - self.hunger)
        happy_hearts = heart_full * self.happy + heart_empty * (4 - self.happy)
        health_hearts = heart_full * self.health + heart_empty * (4 - self.health)

        # Get character with position
        char_lines = self.get_character().split('\n')
        char_padding = ' ' * self.char_pos
        positioned_char = '\n'.join(char_padding + line for line in char_lines)

        # Build the screen
        screen = f"""
        .-=========================================-.
       /                                             \\
      |   {self.name} - Age: {self.age}h            |
      |                                               |
      |                                               |
      |  {positioned_char.split(chr(10))[0] if len(positioned_char.split(chr(10))) > 0 else ''}                |
      |  {positioned_char.split(chr(10))[1] if len(positioned_char.split(chr(10))) > 1 else ''}                |
      |  {positioned_char.split(chr(10))[2] if len(positioned_char.split(chr(10))) > 2 else ''}                |
      |                                               |
      | =========================================     |
      |                                               |
      |  HUNGRY: {hunger_hearts}    HAPPY: {happy_hearts}     |
      |  HEALTH: {health_hearts}    WT: {self.weight:02d}kg      |
      |                                               |
       \\                                             /
        '-==========================================-'
"""
        return screen


class InfoPanel(Static):
    """Side information panel"""

    def render(self) -> str:
        return """
[bold cyan]CONTROLS:[/bold cyan]
  F - Feed
  P - Play
  L - Light (sleep)
  M - Medicine
  C - Clean

  Q - Quit

[dim]Stats update every
few seconds...[/dim]
"""


class TamagotchiApp(App):
    """Main Tamagotchi application"""

    CSS = """
    Screen {
        align: center middle;
        background: $surface;
    }

    #main {
        width: auto;
        height: auto;
    }

    TamagotchiScreen {
        width: 100%;
        color: #00ff00;
        background: #000000;
        border: heavy #00ff00;
    }

    InfoPanel {
        width: 30;
        margin-left: 2;
        padding: 1;
        border: solid cyan;
    }
    """

    BINDINGS = [
        ("f", "feed", "Feed"),
        ("p", "play", "Play"),
        ("l", "light", "Light"),
        ("m", "medicine", "Medicine"),
        ("c", "clean", "Clean"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.game_data = GameData()
        self.state = self.game_data.load()

    def compose(self) -> ComposeResult:
        with Center():
            with Horizontal(id="main"):
                yield TamagotchiScreen(id="screen")
                yield InfoPanel()

    def on_mount(self):
        screen = self.query_one("#screen", TamagotchiScreen)
        screen.hunger = self.state["hunger"]
        screen.happy = self.state["happy"]
        screen.health = self.state["health"]
        screen.age = self.state["age_hours"]
        screen.weight = self.state["weight"]
        screen.name = self.state["name"]

        # Update emotion based on stats
        self.update_emotion()

        # Game loops
        self.set_interval(5.0, self.update_stats)
        self.set_interval(10.0, self.save_game)

    def update_emotion(self):
        screen = self.query_one("#screen", TamagotchiScreen)

        if screen.health < 2:
            screen.emotion = "sad"
        elif screen.hunger < 2:
            screen.emotion = "hungry"
        elif screen.happy > 3:
            screen.emotion = "happy"
        else:
            screen.emotion = "normal"

    def update_stats(self):
        """Decay stats over time"""
        screen = self.query_one("#screen", TamagotchiScreen)

        # Age increases
        screen.age += 1
        self.state["age_hours"] = screen.age

        # Stats decay
        if random.random() < 0.3:
            screen.hunger = max(0, screen.hunger - 1)
            self.state["hunger"] = screen.hunger

        if random.random() < 0.2:
            screen.happy = max(0, screen.happy - 1)
            self.state["happy"] = screen.happy

        self.update_emotion()

    def save_game(self):
        screen = self.query_one("#screen", TamagotchiScreen)
        self.state["hunger"] = screen.hunger
        self.state["happy"] = screen.happy
        self.state["health"] = screen.health
        self.state["age_hours"] = screen.age
        self.state["weight"] = screen.weight
        self.game_data.save(self.state)

    def action_feed(self):
        screen = self.query_one("#screen", TamagotchiScreen)
        if screen.hunger < 4:
            screen.hunger = min(4, screen.hunger + 1)
            screen.weight += 1
            self.state["weight"] = screen.weight
            self.update_emotion()

    def action_play(self):
        screen = self.query_one("#screen", TamagotchiScreen)
        if screen.happy < 4:
            screen.happy = min(4, screen.happy + 1)
            screen.hunger = max(0, screen.hunger - 1)
            if screen.weight > 5:
                screen.weight -= 1
                self.state["weight"] = screen.weight
            self.update_emotion()

    def action_light(self):
        screen = self.query_one("#screen", TamagotchiScreen)
        if screen.emotion == "sleep":
            screen.emotion = "normal"
        else:
            screen.emotion = "sleep"

    def action_medicine(self):
        screen = self.query_one("#screen", TamagotchiScreen)
        if screen.health < 4:
            screen.health = min(4, screen.health + 1)
            self.state["health"] = screen.health
            self.update_emotion()

    def action_clean(self):
        # Clean poop (placeholder for now)
        pass


if __name__ == "__main__":
    app = TamagotchiApp()
    app.run()
