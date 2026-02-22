#!/usr/bin/env python3
"""
Terminal Tamagotchi - Mochi Edition
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
    """The complete Tamagotchi device"""

    hunger = reactive(4)
    health = reactive(4)
    age = reactive(0)
    weight = reactive(10)
    name = reactive("Mochi")
    emotion = reactive("normal")
    char_frame = reactive(0)
    char_x = reactive(8)
    char_y = reactive(2)

    def on_mount(self):
        self.set_interval(0.4, self.animate)
        self.set_interval(2.0, self.move)

    def animate(self):
        self.char_frame = (self.char_frame + 1) % 2

    def move(self):
        """Move character around the screen"""
        if random.random() < 0.6:
            # Move horizontally
            self.char_x = max(1, min(14, self.char_x + random.choice([-1, 0, 1])))
            # Sometimes move vertically
            if random.random() < 0.3:
                self.char_y = max(0, min(3, self.char_y + random.choice([-1, 1])))

    def get_character(self) -> list:
        """Get character sprite lines"""
        if self.emotion == "happy":
            return ["  \\o/", " (^.^)", "  > <"] if self.char_frame == 0 else ["  \\o/", " (^o^)", "  < >"]
        elif self.emotion == "hungry":
            return ["  .-.", " (O.O)", "  ~~~"] if self.char_frame == 0 else ["  .-.", " (@.@)", "  > <"]
        elif self.emotion == "sick":
            return ["  .-.", " (X.X)", "  ..."]
        elif self.emotion == "sleep":
            return ["  .-.", " (- -)", " z z z"]
        else:
            return ["  .-.", " (o.o)", "  > ^"] if self.char_frame == 0 else ["  .-.", " (o.o)", "  ^ <"]

    def render(self) -> str:
        """Render the complete device"""

        # Hearts
        hf = chr(0x2665)  # ♥
        he = chr(0x2661)  # ♡
        hunger_hearts = hf * self.hunger + he * (4 - self.hunger)
        health_hearts = hf * self.health + he * (4 - self.health)

        # Create environment - EXACTLY 20 chars per line (not 24, because of padding)
        env_lines = [
            "   o                ",  # Line 0: Sun
            "                    ",  # Line 1: Sky
            "      /\\            ",  # Line 2: Tree top
            "     /  \\           ",  # Line 3: Tree mid
            "    /____\\          ",  # Line 4: Tree base
            "      ||            ",  # Line 5: Tree trunk
        ]

        # Force exact width of 20
        env_lines = [line[:20].ljust(20) for line in env_lines]

        # Place character in the environment
        char_sprite = self.get_character()

        # Position character in one of the environment lines
        display_lines = env_lines.copy()
        char_y_pos = min(self.char_y, len(display_lines) - 3)

        for i, char_line in enumerate(char_sprite):
            line_idx = char_y_pos + i
            if line_idx < len(display_lines):
                # Convert line to list for character placement
                env_line = list(display_lines[line_idx])
                # Place each character of the sprite
                for j, c in enumerate(char_line.strip()):
                    pos = self.char_x + j
                    if 0 <= pos < 20:
                        env_line[pos] = c
                # Ensure EXACTLY 20 chars
                display_lines[line_idx] = ''.join(env_line)[:20].ljust(20)

        # Format stats
        hunger_line = f"HUNGRY: {hunger_hearts}"
        health_line = f"HEALTH: {health_hearts}"
        age_line = f"AGE: {self.age}h  WT: {self.weight}kg"

        return f"""
        .-==================-.
       /                      \\
      |  {display_lines[0]}  |
      |  {display_lines[1]}  |
      |  {display_lines[2]}  |
      |  {display_lines[3]}  |
      |  {display_lines[4]}  |
      |  {display_lines[5]}  |
      |                        |
      |------------------------|
      |  {hunger_line:20}  |
      |  {health_line:20}  |
      |  {age_line:20}  |
       \\                      /
        '-==================-'
             ___     ___
            | F |   | Q |
            |___|   |___|
            FEED    QUIT
    """


class Title(Static):
    """Title display"""
    name = reactive("Mochi")

    def render(self) -> str:
        return f"\n[bold cyan]{self.name:^28}[/bold cyan]"


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
    }

    Title {
        text-align: center;
        color: #00ffff;
        background: #000000;
        padding: 0;
        margin-bottom: 0;
    }

    TamagotchiDevice {
        width: auto;
        height: auto;
        color: #00ff00;
        background: #000000;
        padding: 1;
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
            with Vertical(id="container"):
                yield Title(id="title")
                yield TamagotchiDevice(id="device")

    def on_mount(self):
        title = self.query_one("#title", Title)
        device = self.query_one("#device", TamagotchiDevice)

        title.name = self.state["name"]
        device.hunger = self.state["hunger"]
        device.health = self.state["health"]
        device.age = self.state["age_hours"]
        device.weight = self.state["weight"]
        device.name = self.state["name"]

        self.calculate_decay()
        self.update_emotion()

        # Game loops
        self.set_interval(60.0, self.age_tick)
        self.set_interval(300.0, self.hunger_tick)
        self.set_interval(10.0, self.check_health)
        self.set_interval(10.0, self.save_game)

    def calculate_decay(self):
        """Calculate decay from time passed"""
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
