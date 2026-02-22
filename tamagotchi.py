#!/usr/bin/env python3
"""
Terminal Tamagotchi - Authentic design with on-screen buttons
"""

import json
import random
from datetime import datetime
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
            "hunger": 4,
            "health": 4,
            "weight": 10,
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


class TamagotchiDevice(Static):
    """The complete Tamagotchi device with screen and buttons"""

    hunger = reactive(4)
    health = reactive(4)
    age = reactive(0)
    weight = reactive(10)
    name = reactive("Blob")
    emotion = reactive("normal")
    char_frame = reactive(0)
    char_pos = reactive(8)

    def on_mount(self):
        self.set_interval(0.5, self.animate)
        self.set_interval(3.0, self.move)

    def animate(self):
        self.char_frame = (self.char_frame + 1) % 2

    def move(self):
        if random.random() < 0.5:
            direction = random.choice([-1, 1])
            self.char_pos = max(3, min(12, self.char_pos + direction))

    def get_character(self) -> str:
        """Get character sprite"""
        if self.emotion == "happy":
            chars = ["  \\o/\n (^.^)\n  > <", "  \\o/\n (^o^)\n  < >"]
        elif self.emotion == "hungry":
            chars = ["  .-.\n (O.O)\n  ~~~", "  .-.\n (@.@)\n  > <"]
        elif self.emotion == "sick":
            chars = ["  .-.\n (X.X)\n  ..."]
        elif self.emotion == "sleep":
            chars = ["  .-.\n (- -)\n z z z"]
        else:
            chars = ["  .-.\n (o.o)\n  > ^", "  .-.\n (o.o)\n  ^ <"]

        char = chars[self.char_frame % len(chars)]
        lines = char.split('\n')
        padding = ' ' * self.char_pos
        return '\n'.join(padding + line for line in lines)

    def render(self) -> str:
        """Render the complete device"""

        # Hearts
        hf = chr(0x2665)  # ♥
        he = chr(0x2661)  # ♡
        hunger_hearts = hf * self.hunger + he * (4 - self.hunger)
        health_hearts = hf * self.health + he * (4 - self.health)

        # Get character and center it properly
        char = self.get_character()
        char_lines = char.split('\n')

        # Center each character line in 20-char space
        centered_lines = []
        for line in char_lines:
            # Strip existing padding, then center
            stripped = line.strip()
            total_padding = 20 - len(stripped)
            left_pad = total_padding // 2
            centered = ' ' * left_pad + stripped
            centered_lines.append(f"{centered:20}")

        # Ensure we have 3 lines
        while len(centered_lines) < 3:
            centered_lines.append(' ' * 20)

        # Format stats with exact spacing
        hunger_line = f"HUNGRY: {hunger_hearts}"
        health_line = f"HEALTH: {health_hearts}"
        stats_line = f"AGE: {self.age:2d}h  WT: {self.weight:2d}kg"

        return f"""
        .-==================-.
       /                      \\
      |{self.name:^24}|
      |                        |
      |{centered_lines[0]:^24}|
      |{centered_lines[1]:^24}|
      |{centered_lines[2]:^24}|
      |                        |
      |------------------------|
      |                        |
      |  {hunger_line:20}  |
      |  {health_line:20}  |
      |  {stats_line:20}  |
      |                        |
       \\                      /
        '-==================-'
               ___   ___
              |   | |   |
              | F | | Q |
              |___| |___|
           FEED    QUIT
    """


class TamagotchiApp(App):
    """Main Tamagotchi application"""

    CSS = """
    Screen {
        align: center middle;
        background: #000000;
    }

    TamagotchiDevice {
        width: auto;
        height: auto;
        color: #00ff00;
        background: #000000;
        padding: 2;
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
            yield TamagotchiDevice(id="device")

    def on_mount(self):
        device = self.query_one("#device", TamagotchiDevice)
        device.hunger = self.state["hunger"]
        device.health = self.state["health"]
        device.age = self.state["age_hours"]
        device.weight = self.state["weight"]
        device.name = self.state["name"]

        self.calculate_decay()
        self.update_emotion()

        # Game loops
        self.set_interval(60.0, self.age_tick)
        self.set_interval(300.0, self.hunger_tick)  # Hunger drops every 5 min
        self.set_interval(10.0, self.check_health)
        self.set_interval(10.0, self.save_game)

    def calculate_decay(self):
        """Calculate decay from time passed"""
        try:
            last_save = datetime.fromisoformat(self.state["last_save"])
            now = datetime.now()
            minutes_passed = (now - last_save).total_seconds() / 60

            # Lose 1 hunger every 5 minutes
            hunger_loss = int(minutes_passed / 5)
            device = self.query_one("#device", TamagotchiDevice)
            device.hunger = max(0, device.hunger - hunger_loss)
            self.state["hunger"] = device.hunger
        except Exception:
            pass

    def age_tick(self):
        """Age the pet"""
        device = self.query_one("#device", TamagotchiDevice)
        device.age += 1
        self.state["age_hours"] = device.age

    def hunger_tick(self):
        """Decrease hunger over time"""
        device = self.query_one("#device", TamagotchiDevice)
        if device.hunger > 0:
            device.hunger -= 1
            self.state["hunger"] = device.hunger
            self.update_emotion()

    def check_health(self):
        """If starving, lose health"""
        device = self.query_one("#device", TamagotchiDevice)

        if device.hunger == 0:
            if random.random() < 0.4:
                device.health = max(0, device.health - 1)
                self.state["health"] = device.health
                self.update_emotion()

    def update_emotion(self):
        """Update character emotion"""
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
        """Save state"""
        device = self.query_one("#device", TamagotchiDevice)
        self.state["hunger"] = device.hunger
        self.state["health"] = device.health
        self.state["age_hours"] = device.age
        self.state["weight"] = device.weight
        self.game_data.save(self.state)

    def action_feed(self):
        """Feed the pet"""
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
