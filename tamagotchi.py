#!/usr/bin/env python3
"""
Terminal Tamagotchi - Retro Game UI
"""

import json
import random
from datetime import datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static
from textual.reactive import reactive


class GameData:
    """Manages game state persistence"""

    def __init__(self, save_file: Path = Path.home() / ".tamagotchi_save.json"):
        self.save_file = save_file

    def load(self) -> dict:
        defaults = {
            "name": "Mochi",
            "age_hours": 0,
            "hunger": 4,
            "health": 4,
            "weight": 5,
            "last_save": datetime.now().isoformat(),
        }

        if self.save_file.exists():
            try:
                with open(self.save_file) as f:
                    loaded = json.load(f)
                    result = {**defaults, **{k: v for k, v in loaded.items() if k in defaults}}
                    result["age_hours"] = 0
                    return result
            except Exception:
                pass

        return defaults

    def save(self, data: dict):
        data["last_save"] = datetime.now().isoformat()
        with open(self.save_file, "w") as f:
            json.dump(data, f, indent=2)


class TopBar(Static):
    """Top HUD bar"""
    name = reactive("Mochi")

    def render(self) -> str:
        title = f"[bold cyan]< {self.name.upper()} >[/bold cyan]"
        controls = "[dim]Feed: [cyan]F[/cyan]  |  Quit: [cyan]Q[/cyan][/dim]"
        # Pad to fill width
        return f"{title:<40}{controls:>40}"


class Character(Static):
    """The floating character - bigger size"""

    emotion = reactive("normal")
    char_frame = reactive(0)
    x = reactive(35)
    y = reactive(10)

    def on_mount(self):
        self.set_interval(0.4, self.animate)
        self.set_interval(2.0, self.move)

    def animate(self):
        self.char_frame = (self.char_frame + 1) % 2

    def move(self):
        if random.random() < 0.5:
            self.x = max(25, min(45, self.x + random.choice([-2, -1, 0, 1, 2])))
        if random.random() < 0.3:
            self.y = max(8, min(14, self.y + random.choice([-1, 0, 1])))

    def get_sprite(self) -> str:
        """Get bigger character sprite"""
        if self.emotion == "happy":
            return """
      \\\\  //
       \\\\//
    .=======.
    | ^   ^ |
    |   v   |
    |  \\_/  |
    '======='
      |   |
     /     \\
    """ if self.char_frame == 0 else """
      //  \\\\
       //\\\\
    .=======.
    | ^   ^ |
    |   o   |
    |  \\_/  |
    '======='
      |   |
     /     \\
    """
        elif self.emotion == "hungry":
            return """
    .=======.
    | O   O |
    |   ~   |
    |  ___  |
    '======='
      |   |
     /     \\
    """
        elif self.emotion == "sick":
            return """
    .=======.
    | X   X |
    |   ~   |
    |  ...  |
    '======='
      |   |
     /     \\
    """
        else:
            return """
    .=======.
    | o   o |
    |   >   |
    |  ___  |
    '======='
      |   |
     /     \\
    """ if self.char_frame == 0 else """
    .=======.
    | o   o |
    |   <   |
    |  ___  |
    '======='
      |   |
     /     \\
    """

    def render(self) -> str:
        sprite = self.get_sprite().strip()
        # Position the sprite
        lines = sprite.split('\n')
        positioned = []
        for i, line in enumerate(lines):
            # Add vertical positioning
            if i < self.y:
                positioned.append('')
            else:
                # Add horizontal positioning
                positioned.append(' ' * self.x + line)

        return '\n'.join(positioned)


class BottomBar(Static):
    """Bottom HUD bar with stats"""

    hunger = reactive(4)
    health = reactive(4)
    age = reactive(0)
    weight = reactive(5)

    def render(self) -> str:
        hf, he = chr(0x2665), chr(0x2661)
        h_hearts = hf * self.hunger + he * (4 - self.hunger)
        hp_hearts = hf * self.health + he * (4 - self.health)

        return f"[cyan]HUNGRY:[/cyan] {h_hearts}  [cyan]|[/cyan]  [cyan]HEALTH:[/cyan] {hp_hearts}  [cyan]|[/cyan]  [cyan]AGE:[/cyan] {self.age}h  [cyan]|[/cyan]  [cyan]WT:[/cyan] {self.weight}kg"


class TamagotchiApp(App):
    """Main app"""

    CSS = """
    Screen {
        background: #000000;
    }

    TopBar {
        dock: top;
        height: 1;
        background: #000000;
        color: #00ff00;
        padding: 0 2;
    }

    Character {
        height: 100%;
        background: #000000;
        color: #00ff00;
    }

    BottomBar {
        dock: bottom;
        height: 1;
        background: #000000;
        color: #00ff00;
        text-align: center;
        padding: 0 2;
    }
    """

    BINDINGS = [
        ("f", "feed", "Feed"),
        ("space", "feed", "Feed"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.game_data = GameData()
        self.state = self.game_data.load()

    def compose(self) -> ComposeResult:
        yield TopBar(id="top")
        yield Character(id="character")
        yield BottomBar(id="bottom")

    def on_mount(self):
        top = self.query_one("#top", TopBar)
        char = self.query_one("#character", Character)
        bottom = self.query_one("#bottom", BottomBar)

        top.name = self.state["name"]
        char.emotion = "happy"
        bottom.hunger = self.state["hunger"]
        bottom.health = self.state["health"]
        bottom.age = self.state["age_hours"]
        bottom.weight = self.state["weight"]

        self.calculate_decay()
        self.update_emotion()

        self.set_interval(60.0, self.age_tick)
        self.set_interval(300.0, self.hunger_tick)
        self.set_interval(10.0, self.check_health)
        self.set_interval(10.0, self.save_game)

    def calculate_decay(self):
        try:
            last_save = datetime.fromisoformat(self.state["last_save"])
            minutes_passed = (datetime.now() - last_save).total_seconds() / 60
            bottom = self.query_one("#bottom", BottomBar)
            bottom.hunger = max(0, bottom.hunger - int(minutes_passed / 5))
            self.state["hunger"] = bottom.hunger
        except Exception:
            pass

    def age_tick(self):
        bottom = self.query_one("#bottom", BottomBar)
        bottom.age += 1
        self.state["age_hours"] = bottom.age

    def hunger_tick(self):
        bottom = self.query_one("#bottom", BottomBar)
        char = self.query_one("#character", Character)
        if bottom.hunger > 0:
            bottom.hunger -= 1
            self.state["hunger"] = bottom.hunger
            self.update_emotion()

    def check_health(self):
        bottom = self.query_one("#bottom", BottomBar)
        if bottom.hunger == 0 and random.random() < 0.4:
            bottom.health = max(0, bottom.health - 1)
            self.state["health"] = bottom.health
            self.update_emotion()

    def update_emotion(self):
        char = self.query_one("#character", Character)
        bottom = self.query_one("#bottom", BottomBar)

        if bottom.health <= 1:
            char.emotion = "sick"
        elif bottom.hunger == 0:
            char.emotion = "hungry"
        elif bottom.hunger >= 3 and bottom.health >= 3:
            char.emotion = "happy"
        else:
            char.emotion = "normal"

    def save_game(self):
        bottom = self.query_one("#bottom", BottomBar)
        self.state["hunger"] = bottom.hunger
        self.state["health"] = bottom.health
        self.state["age_hours"] = bottom.age
        self.state["weight"] = bottom.weight
        self.game_data.save(self.state)

    def action_feed(self):
        bottom = self.query_one("#bottom", BottomBar)
        char = self.query_one("#character", Character)

        if bottom.hunger >= 4:
            char.emotion = "happy"
            self.set_timer(1.0, lambda: self.update_emotion())
        else:
            bottom.hunger = min(4, bottom.hunger + 1)
            bottom.weight += 1
            self.state["hunger"] = bottom.hunger
            self.state["weight"] = bottom.weight
            char.emotion = "happy"
            self.set_timer(1.5, lambda: self.update_emotion())


if __name__ == "__main__":
    app = TamagotchiApp()
    app.run()
