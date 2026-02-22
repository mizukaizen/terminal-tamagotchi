#!/usr/bin/env python3
"""
Terminal Tamagotchi - Mochi Edition
Perfect centering and alignment
"""

import json
import random
from datetime import datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Center, Vertical
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


class TamagotchiDevice(Static):
    """The complete Tamagotchi device"""

    hunger = reactive(4)
    health = reactive(4)
    age = reactive(0)
    weight = reactive(5)
    emotion = reactive("normal")
    char_frame = reactive(0)
    char_x = reactive(7)

    def on_mount(self):
        self.set_interval(0.4, self.animate)
        self.set_interval(2.5, self.move)

    def animate(self):
        self.char_frame = (self.char_frame + 1) % 2

    def move(self):
        if random.random() < 0.6:
            self.char_x = max(3, min(11, self.char_x + random.choice([-1, 0, 1])))

    def get_character(self) -> list:
        """Get character sprite lines"""
        if self.emotion == "happy":
            return ["  \\o/", " (^.^)", "  > <"] if self.char_frame == 0 else ["  \\o/", " (^o^)", "  < >"]
        elif self.emotion == "hungry":
            return ["  .-.", " (O.O)", "  ~~~"]
        elif self.emotion == "sick":
            return ["  .-.", " (X.X)", "  ..."]
        elif self.emotion == "sleep":
            return ["  .-.", " (- -)", " z z z"]
        else:
            return ["  .-.", " (o.o)", "  > ^"] if self.char_frame == 0 else ["  .-.", " (o.o)", "  ^ <"]

    def render(self) -> str:
        """Render device with perfect alignment"""

        # Hearts
        hf = chr(0x2665)
        he = chr(0x2661)
        hunger_h = hf * self.hunger + he * (4 - self.hunger)
        health_h = hf * self.health + he * (4 - self.health)

        # Build character positioned - exactly 20 chars wide
        char = self.get_character()
        c1 = (" " * self.char_x + char[0])[:20].ljust(20)
        c2 = (" " * self.char_x + char[1])[:20].ljust(20)
        c3 = (" " * self.char_x + char[2])[:20].ljust(20)

        return f"""
        .-==================-.
       /                      \\
      |  {c1}  |
      |  {c2}  |
      |  {c3}  |
      |                        |
      |------------------------|
      |  HUNGRY: {hunger_h:12}  |
      |  HEALTH: {health_h:12}  |
      |  AGE: {self.age}h  WT: {self.weight}kg{' ' * (7 - len(str(self.age)) - len(str(self.weight)))}  |
       \\                      /
        '-==================-'
             ___     ___
            | F |   | Q |
            |___|   |___|
            FEED    QUIT
    """


class EnvDecoration(Static):
    """Static environment decorations"""

    def render(self) -> str:
        return "          ☀️    ☁️     ☁️           🌸  🌳  🌸"


class Title(Static):
    """Title display"""
    name = reactive("Mochi")

    def render(self) -> str:
        return f"[bold cyan]{self.name:^32}[/bold cyan]"


class Instructions(Static):
    """Game instructions"""

    def render(self) -> str:
        return "[dim cyan]Feed Mochi every 5 minutes! If hungry (♡♡♡♡), health drops.[/dim cyan]"


class TamagotchiApp(App):
    """Main Tamagotchi application"""

    CSS = """
    Screen {
        align: center middle;
        background: #000000;
    }

    #container {
        width: auto;
        height: auto;
        align: center middle;
    }

    Title {
        text-align: center;
        width: 100%;
    }

    EnvDecoration {
        text-align: center;
        width: 100%;
        padding: 0 0 1 0;
    }

    TamagotchiDevice {
        width: auto;
        height: auto;
        color: #00ff00;
        background: #000000;
    }

    Instructions {
        text-align: center;
        width: 100%;
        padding: 1 0 0 0;
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
        with Center():
            with Vertical(id="container"):
                yield Title(id="title")
                yield EnvDecoration(id="env")
                yield TamagotchiDevice(id="device")
                yield Instructions(id="instructions")

    def on_mount(self):
        title = self.query_one("#title", Title)
        device = self.query_one("#device", TamagotchiDevice)

        title.name = self.state["name"]
        device.hunger = self.state["hunger"]
        device.health = self.state["health"]
        device.age = self.state["age_hours"]
        device.weight = self.state["weight"]

        self.calculate_decay()
        self.update_emotion()

        self.set_interval(60.0, self.age_tick)
        self.set_interval(300.0, self.hunger_tick)
        self.set_interval(10.0, self.check_health)
        self.set_interval(10.0, self.save_game)

    def calculate_decay(self):
        try:
            last_save = datetime.fromisoformat(self.state["last_save"])
            now = datetime.now()
            minutes_passed = (now - last_save).total_seconds() / 60
            hunger_loss = int(minutes_passed / 5)

            device = self.query_one("#device", TamagotchiDevice)
            device.hunger = max(0, device.hunger - hunger_loss)
            self.state["hunger"] = device.hunger
        except Exception:
            pass

    def age_tick(self):
        device = self.query_one("#device", TamagotchiDevice)
        device.age += 1
        self.state["age_hours"] = device.age

    def hunger_tick(self):
        device = self.query_one("#device", TamagotchiDevice)
        if device.hunger > 0:
            device.hunger -= 1
            self.state["hunger"] = device.hunger
            self.update_emotion()

    def check_health(self):
        device = self.query_one("#device", TamagotchiDevice)
        if device.hunger == 0:
            if random.random() < 0.4:
                device.health = max(0, device.health - 1)
                self.state["health"] = device.health
                self.update_emotion()

    def update_emotion(self):
        device = self.query_one("#device", TamagotchiDevice)
        if device.health <= 1:
            device.emotion = "sick"
        elif device.hunger == 0:
            device.emotion = "hungry"
        elif device.hunger >= 3 and device.health >= 3:
            device.emotion = "happy"
        else:
            device.emotion = "normal"

    def save_game(self):
        device = self.query_one("#device", TamagotchiDevice)
        self.state["hunger"] = device.hunger
        self.state["health"] = device.health
        self.state["age_hours"] = device.age
        self.state["weight"] = device.weight
        self.game_data.save(self.state)

    def action_feed(self):
        device = self.query_one("#device", TamagotchiDevice)
        if device.hunger >= 4:
            device.emotion = "happy"
            self.set_timer(1.0, lambda: self.update_emotion())
        else:
            device.hunger = min(4, device.hunger + 1)
            device.weight += 1
            self.state["hunger"] = device.hunger
            self.state["weight"] = device.weight
            device.emotion = "happy"
            self.set_timer(1.5, lambda: self.update_emotion())


if __name__ == "__main__":
    app = TamagotchiApp()
    app.run()
