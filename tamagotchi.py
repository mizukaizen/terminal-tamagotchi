#!/usr/bin/env python3
"""
Terminal Tamagotchi - Simple and authentic
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Center
from textual.widgets import Static
from textual.reactive import reactive


class GameData:
    """Manages game state persistence"""

    def __init__(self, save_file: Path = Path.home() / ".tamagotchi_save.json"):
        self.save_file = save_file

    def load(self) -> dict:
        defaults = {
            "name": "Blob",
            "age_hours": 0,
            "hunger": 4,  # 0-4 hearts
            "health": 4,
            "weight": 10,
            "last_fed": datetime.now().isoformat(),
            "last_save": datetime.now().isoformat(),
        }

        if self.save_file.exists():
            try:
                with open(self.save_file) as f:
                    loaded = json.load(f)
                    return {**defaults, **{k: v for k, v in loaded.items() if k in defaults}}
            except Exception:
                pass

        return defaults

    def save(self, data: dict):
        data["last_save"] = datetime.now().isoformat()
        with open(self.save_file, "w") as f:
            json.dump(data, f, indent=2)


class TamagotchiScreen(Static):
    """The main Tamagotchi screen"""

    hunger = reactive(4)
    health = reactive(4)
    age = reactive(0)
    weight = reactive(10)
    name = reactive("Blob")
    emotion = reactive("normal")
    char_frame = reactive(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.char_pos = 10

    def on_mount(self):
        self.set_interval(0.5, self.animate)
        self.set_interval(3.0, self.move)

    def animate(self):
        self.char_frame = (self.char_frame + 1) % 2

    def move(self):
        if random.random() < 0.6:
            direction = random.choice([-1, 1])
            self.char_pos = max(5, min(15, self.char_pos + direction))

    def get_character(self) -> list:
        """Get character sprite lines"""
        if self.emotion == "happy":
            return [
                "  \\o/",
                " (^.^)",
                "  > <"
            ] if self.char_frame == 0 else [
                "  \\o/",
                " (^o^)",
                "  < >"
            ]
        elif self.emotion == "hungry":
            return [
                "  .-.",
                " (O.O)",
                "  ~~~"
            ] if self.char_frame == 0 else [
                "  .-.",
                " (@.@)",
                "  > <"
            ]
        elif self.emotion == "sick":
            return [
                "  .-.",
                " (X.X)",
                "  ..."
            ]
        elif self.emotion == "sleep":
            return [
                "  .-.",
                " (- -)",
                " z z z"
            ]
        else:  # normal
            return [
                "  .-.",
                " (o.o)",
                "  > ^"
            ] if self.char_frame == 0 else [
                "  .-.",
                " (o.o)",
                "  ^ <"
            ]

    def render(self) -> str:
        """Render the Tamagotchi screen"""

        # Get character
        char = self.get_character()
        padding = ' ' * self.char_pos

        # Hearts
        hf = chr(0x2665)  # ♥
        he = chr(0x2661)  # ♡
        hunger_h = hf * self.hunger + he * (4 - self.hunger)
        health_h = hf * self.health + he * (4 - self.health)

        # Build screen - compact and aligned
        return f"""
      .----------------------.
     /                        \\
    |    {self.name} - {self.age}h old    |
    |                          |
    |                          |
    |  {padding}{char[0]}           |
    |  {padding}{char[1]}           |
    |  {padding}{char[2]}           |
    |                          |
    |  --------------------    |
    |                          |
    |  HUNGER: {hunger_h}         |
    |  HEALTH: {health_h}         |
    |  WEIGHT: {self.weight:2d} kg         |
    |                          |
     \\                        /
      '----------------------'
"""


class TamagotchiApp(App):
    """Main Tamagotchi application"""

    CSS = """
    Screen {
        align: center middle;
        background: $surface;
    }

    TamagotchiScreen {
        width: auto;
        height: auto;
        color: #00ff00;
        background: #000000;
        padding: 1 2;
    }
    """

    BINDINGS = [
        ("f", "feed", "Feed (F)"),
        ("space", "feed", "Feed (Space)"),
        ("q", "quit", "Quit (Q)"),
    ]

    def __init__(self):
        super().__init__()
        self.game_data = GameData()
        self.state = self.game_data.load()

    def compose(self) -> ComposeResult:
        with Center():
            yield TamagotchiScreen(id="screen")

    def on_mount(self):
        screen = self.query_one("#screen", TamagotchiScreen)
        screen.hunger = self.state["hunger"]
        screen.health = self.state["health"]
        screen.age = self.state["age_hours"]
        screen.weight = self.state["weight"]
        screen.name = self.state["name"]

        # Check if need to decay from last session
        self.calculate_decay()
        self.update_emotion()

        # Update age and stats
        self.set_interval(60.0, self.age_tick)  # Age every minute (faster for demo)
        self.set_interval(10.0, self.save_game)
        self.set_interval(2.0, self.check_hunger)

    def calculate_decay(self):
        """Calculate what happened while the game was closed"""
        try:
            last_save = datetime.fromisoformat(self.state["last_save"])
            now = datetime.now()
            hours_passed = (now - last_save).total_seconds() / 3600

            # Lose 1 hunger per hour
            hunger_loss = int(hours_passed)
            screen = self.query_one("#screen", TamagotchiScreen)
            screen.hunger = max(0, screen.hunger - hunger_loss)
            self.state["hunger"] = screen.hunger
        except Exception:
            pass

    def age_tick(self):
        """Age the pet and handle hunger decay"""
        screen = self.query_one("#screen", TamagotchiScreen)
        screen.age += 1
        self.state["age_hours"] = screen.age

    def check_hunger(self):
        """Check hunger and update health"""
        screen = self.query_one("#screen", TamagotchiScreen)

        # If very hungry, lose health
        if screen.hunger == 0:
            if random.random() < 0.3:  # Sometimes
                screen.health = max(0, screen.health - 1)
                self.state["health"] = screen.health
                self.update_emotion()

    def update_emotion(self):
        """Update character emotion based on stats"""
        screen = self.query_one("#screen", TamagotchiScreen)

        if screen.health <= 1:
            screen.emotion = "sick"
        elif screen.hunger <= 1:
            screen.emotion = "hungry"
        elif screen.hunger == 4 and screen.health == 4:
            screen.emotion = "happy"
        else:
            screen.emotion = "normal"

    def save_game(self):
        """Save current state"""
        screen = self.query_one("#screen", TamagotchiScreen)
        self.state["hunger"] = screen.hunger
        self.state["health"] = screen.health
        self.state["age_hours"] = screen.age
        self.state["weight"] = screen.weight
        self.game_data.save(self.state)

    def action_feed(self):
        """Feed the pet"""
        screen = self.query_one("#screen", TamagotchiScreen)

        if screen.hunger >= 4:
            # Already full - just show happy
            screen.emotion = "happy"
            self.set_timer(1.0, lambda: self.update_emotion())
        else:
            # Feed!
            screen.hunger = min(4, screen.hunger + 1)
            screen.weight += 1
            self.state["hunger"] = screen.hunger
            self.state["weight"] = screen.weight
            self.state["last_fed"] = datetime.now().isoformat()

            # Show happy briefly
            screen.emotion = "happy"
            self.set_timer(1.5, lambda: self.update_emotion())


if __name__ == "__main__":
    app = TamagotchiApp()
    app.run()
