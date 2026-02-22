#!/usr/bin/env python3
"""
Terminal Tamagotchi - Mochi Edition
Now with death, quotes, and 1 hour = 1 year!
"""

import json
import random
import sys
from datetime import datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Center, Vertical
from textual.widgets import Static
from textual.reactive import reactive


# Mochi's cute quotes
MOCHI_QUOTES = [
    "I love you! ^.^",
    "Feed me plz! o.o",
    "This is nice~",
    "Happy happy!",
    "Exploring! :D",
    "La la la~",
    "So cozy here!",
    "Best day ever!",
    "nom nom nom",
    "Wheee! >.<",
]


class GameData:
    """Manages game state persistence"""

    def __init__(self, save_file: Path = Path.home() / ".tamagotchi_save.json"):
        self.save_file = save_file

    def load(self) -> dict:
        defaults = {
            "name": "Mochi",
            "age_years": 0,
            "hunger": 4,
            "health": 4,
            "poops": 0,
            "lifetime_years": 0,
            "milestones": [],
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

    def reset(self):
        """Reset to newborn state"""
        return {
            "name": "Mochi",
            "age_years": 0,
            "hunger": 4,
            "health": 4,
            "poops": 0,
            "lifetime_years": 0,
            "milestones": [],
            "last_save": datetime.now().isoformat(),
        }


class Character(Static):
    """Character with full environment"""

    emotion = reactive("normal")
    char_frame = reactive(0)
    x_offset = reactive(0)
    cloud1_x = reactive(20)
    cloud2_x = reactive(50)
    cloud3_x = reactive(10)
    cloud4_x = reactive(65)
    weather = reactive("clear")
    poops = reactive(0)
    quote = reactive("")
    is_dead = reactive(False)

    def on_mount(self):
        self.set_interval(0.5, self.animate)
        self.set_interval(2.0, self.move)
        self.set_interval(3.0, self.drift_clouds)
        self.set_interval(120.0, self.change_weather)
        self.set_interval(20.0, self.show_quote)

    def animate(self):
        self.char_frame = (self.char_frame + 1) % 2

    def move(self):
        if not self.is_dead and random.random() < 0.6:
            self.x_offset = max(-15, min(15, self.x_offset + random.choice([-2, -1, 0, 1, 2])))

    def drift_clouds(self):
        self.cloud1_x = (self.cloud1_x + 1) % 80
        self.cloud2_x = (self.cloud2_x + 1) % 80
        self.cloud3_x = (self.cloud3_x + 2) % 80
        self.cloud4_x = (self.cloud4_x + 1) % 80

    def change_weather(self):
        if random.random() < 0.3:
            self.weather = random.choice(["clear", "rain", "snow"])

    def show_quote(self):
        """Show random Mochi quote"""
        if not self.is_dead and random.random() < 0.4:
            self.quote = random.choice(MOCHI_QUOTES)
            # Clear quote after 3 seconds
            # Note: can't use self.set_timer in Static widget, will clear on next cycle

    def is_night(self) -> bool:
        hour = datetime.now().hour
        return hour >= 20 or hour < 6

    def is_sleeping_time(self) -> bool:
        hour = datetime.now().hour
        return hour >= 22 or hour < 6

    def get_sprite(self) -> str:
        if self.is_dead:
            return "  .-.\n (X.X)\n  RIP"

        if self.is_sleeping_time():
            return "  .-.\n (- -)\n z z z"

        if self.emotion == "happy":
            return "  \\o/\n (^.^)\n  > <" if self.char_frame == 0 else "  \\o/\n (^o^)\n  < >"
        elif self.emotion == "hungry":
            return "  .-.\n (O.O)\n  ~~~"
        elif self.emotion == "sick":
            return "  .-.\n (;.;)\n  ..." if self.char_frame == 0 else "  .-.\n (~.~)\n  ..."
        else:
            return "  .-.\n (o.o)\n  > ^" if self.char_frame == 0 else "  .-.\n (o.o)\n  ^ <"

    def render(self) -> str:
        sprite = self.get_sprite()
        char_lines = sprite.split('\n')
        scene_lines = []

        # DEATH SCREEN
        if self.is_dead:
            scene_lines.extend([""] * 8)
            scene_lines.append("                         .-.                          ")
            scene_lines.append("                        (X.X)                         ")
            scene_lines.append("                         RIP                          ")
            scene_lines.append("")
            scene_lines.append("              Mochi is dead. How could you?           ")
            scene_lines.append("")
            scene_lines.append("                 Press R to restart...                ")
            scene_lines.extend([""] * 3)
            return '\n'.join(scene_lines)

        # SKY
        if self.is_night():
            scene_lines.append("  🌙")
            scene_lines.append(" " * self.cloud1_x + "✦")
            scene_lines.append(" " * self.cloud2_x + "★")
            scene_lines.append(" " * self.cloud3_x + "✧" + " " * max(5, abs(self.cloud4_x - self.cloud3_x)) + "⋆")
        else:
            scene_lines.append("  ☀️")
            if self.weather == "rain":
                scene_lines.append(" " * self.cloud1_x + "🌧️")
                scene_lines.append(" " * self.cloud2_x + "🌧️")
                scene_lines.append(" " * self.cloud3_x + "💧")
            elif self.weather == "snow":
                scene_lines.append(" " * self.cloud1_x + "❄️")
                scene_lines.append(" " * self.cloud2_x + "❄️")
                scene_lines.append(" " * self.cloud3_x + "❄️")
            else:
                scene_lines.append(" " * self.cloud1_x + "☁️")
                scene_lines.append(" " * self.cloud2_x + "☁️")
                scene_lines.append(" " * self.cloud3_x + "☁️" + " " * max(5, abs(self.cloud4_x - self.cloud3_x)) + "☁️")

        scene_lines.append("")
        scene_lines.append("")

        # QUOTE (if present)
        if self.quote:
            quote_line = f'"{self.quote}"'
            scene_lines.append(f"{quote_line:^80}")
        else:
            scene_lines.append("")

        # CHARACTER
        base_position = 38
        for line in char_lines:
            actual_pos = base_position + self.x_offset
            scene_lines.append(' ' * max(0, actual_pos) + line)

        scene_lines.append("")

        # POOP
        if self.poops > 0:
            poop_line = " " * (base_position + self.x_offset + 8) + "💩" * min(self.poops, 3)
            scene_lines.append(poop_line)
        else:
            scene_lines.append("")

        # GROUND
        scene_lines.append("   🌸      🌳        🌸         🌳              🌳")
        scene_lines.append("=" * 200)

        return '\n'.join(scene_lines)


class TopBar(Static):
    """Top HUD"""
    name = reactive("Mochi")
    milestone = reactive("")

    def render(self) -> str:
        title = f"[bold cyan]< {self.name.upper()} >[/bold cyan]"
        controls = "[dim yellow]⚠ Feed every 5min! ⚠  |  F: Feed  |  C: Clean  |  Q: Quit[/dim yellow]"

        if self.milestone:
            return f"{title}  [yellow bold]{self.milestone}[/yellow bold]  {controls}"
        return f"{title}    {controls}"


class BottomBar(Static):
    """Bottom stats HUD"""

    hunger = reactive(4)
    health = reactive(4)
    age_years = reactive(0)

    def render(self) -> str:
        hf, he = chr(0x2665), chr(0x2661)
        h_hearts = hf * self.hunger + he * (4 - self.hunger)
        hp_hearts = hf * self.health + he * (4 - self.health)

        return f"[cyan]HUNGRY:[/cyan] {h_hearts}  [cyan]|[/cyan]  [cyan]HEALTH:[/cyan] {hp_hearts}  [cyan]|[/cyan]  [cyan]AGE:[/cyan] {self.age_years} years old"


class TamagotchiApp(App):
    """Main app"""

    CSS = """
    Screen {
        align: center middle;
        background: #000000;
    }

    TopBar {
        dock: top;
        height: 1;
        width: 100%;
        background: #000000;
        color: #00ff00;
        padding: 0 1;
    }

    Character {
        width: 100%;
        height: auto;
        background: #000000;
        color: #00ff00;
        content-align: center middle;
    }

    BottomBar {
        dock: bottom;
        height: 1;
        width: 100%;
        background: #000000;
        color: #00ff00;
        text-align: center;
        padding: 0 2;
    }
    """

    BINDINGS = [
        ("f", "feed", "Feed"),
        ("space", "feed", "Feed"),
        ("c", "clean", "Clean"),
        ("r", "restart", "Restart"),
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
        self.sync_state()
        self.calculate_decay()
        self.update_emotion()

        self.set_interval(60.0, self.age_tick)
        self.set_interval(300.0, self.hunger_tick)
        self.set_interval(10.0, self.check_health)
        self.set_interval(10.0, self.save_game)
        self.set_interval(600.0, self.poop_check)

    def sync_state(self):
        """Sync state to UI"""
        top = self.query_one("#top", TopBar)
        char = self.query_one("#character", Character)
        bottom = self.query_one("#bottom", BottomBar)

        top.name = self.state["name"]
        char.poops = self.state["poops"]
        bottom.hunger = self.state["hunger"]
        bottom.health = self.state["health"]
        bottom.age_years = self.state["age_years"]

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
        """Age 1 year per hour"""
        bottom = self.query_one("#bottom", BottomBar)
        top = self.query_one("#top", TopBar)

        bottom.age_years += 1
        self.state["age_years"] += 1
        self.state["lifetime_years"] = self.state.get("lifetime_years", 0) + 1

        # Milestones (in years)
        if bottom.age_years == 24 and "day1" not in self.state["milestones"]:
            self.state["milestones"].append("day1")
            top.milestone = "★ 1 Day Old! ★"
            self.set_timer(5.0, lambda: setattr(top, "milestone", ""))
        elif bottom.age_years == 72 and "day3" not in self.state["milestones"]:
            self.state["milestones"].append("day3")
            top.milestone = "★ 3 Days Old! ★"
            self.set_timer(5.0, lambda: setattr(top, "milestone", ""))

    def hunger_tick(self):
        """Hunger drops every 5 minutes"""
        bottom = self.query_one("#bottom", BottomBar)
        if bottom.hunger > 0:
            bottom.hunger -= 1
            self.state["hunger"] = bottom.hunger
            self.update_emotion()

    def poop_check(self):
        bottom = self.query_one("#bottom", BottomBar)
        char = self.query_one("#character", Character)
        if bottom.hunger >= 3 and char.poops < 3 and random.random() < 0.6:
            char.poops += 1
            self.state["poops"] = char.poops

    def check_health(self):
        """Health and death check"""
        bottom = self.query_one("#bottom", BottomBar)
        char = self.query_one("#character", Character)

        # DEATH CHECK
        if bottom.health == 0:
            char.is_dead = True
            return

        # Lose health
        if bottom.hunger == 0 and random.random() < 0.4:
            bottom.health = max(0, bottom.health - 1)
            self.state["health"] = bottom.health
            self.update_emotion()
        elif char.poops >= 2 and random.random() < 0.3:
            bottom.health = max(0, bottom.health - 1)
            self.state["health"] = bottom.health
            self.update_emotion()

        # Regain health
        elif bottom.hunger >= 3 and char.poops == 0 and bottom.health < 4 and random.random() < 0.3:
            bottom.health = min(4, bottom.health + 1)
            self.state["health"] = bottom.health
            self.update_emotion()

    def update_emotion(self):
        char = self.query_one("#character", Character)
        bottom = self.query_one("#bottom", BottomBar)

        if bottom.health == 0:
            char.is_dead = True
        elif bottom.health <= 1:
            char.emotion = "sick"
        elif bottom.hunger == 0:
            char.emotion = "hungry"
        elif bottom.hunger >= 3 and bottom.health >= 3:
            char.emotion = "happy"
        else:
            char.emotion = "normal"

    def save_game(self):
        bottom = self.query_one("#bottom", BottomBar)
        char = self.query_one("#character", Character)
        self.state["hunger"] = bottom.hunger
        self.state["health"] = bottom.health
        self.state["age_years"] = bottom.age_years
        self.state["poops"] = char.poops
        self.game_data.save(self.state)

    def action_feed(self):
        char = self.query_one("#character", Character)
        if char.is_dead:
            return

        bottom = self.query_one("#bottom", BottomBar)

        if bottom.hunger >= 4:
            char.emotion = "happy"
            self.set_timer(1.0, lambda: self.update_emotion())
        else:
            bottom.hunger = min(4, bottom.hunger + 1)
            self.state["hunger"] = bottom.hunger
            char.emotion = "happy"
            char.quote = "Yummy! ^.^"
            self.set_timer(2.0, lambda: setattr(char, "quote", ""))
            self.set_timer(1.5, lambda: self.update_emotion())

    def action_clean(self):
        char = self.query_one("#character", Character)
        if char.is_dead:
            return

        if char.poops > 0:
            char.poops = 0
            self.state["poops"] = 0
            char.quote = "Thanks! :D"
            self.set_timer(2.0, lambda: setattr(char, "quote", ""))

    def action_restart(self):
        """Restart after death"""
        char = self.query_one("#character", Character)
        if char.is_dead:
            # Reset game
            self.state = self.game_data.reset()
            self.game_data.save(self.state)
            char.is_dead = False
            char.quote = ""
            self.sync_state()
            self.update_emotion()


class Character(Static):
    """The character with environment"""

    emotion = reactive("normal")
    char_frame = reactive(0)
    x_offset = reactive(0)
    cloud1_x = reactive(20)
    cloud2_x = reactive(50)
    cloud3_x = reactive(10)
    cloud4_x = reactive(65)
    weather = reactive("clear")
    poops = reactive(0)
    quote = reactive("")
    is_dead = reactive(False)

    def on_mount(self):
        self.set_interval(0.5, self.animate)
        self.set_interval(2.0, self.move)
        self.set_interval(3.0, self.drift_clouds)
        self.set_interval(120.0, self.change_weather)
        self.set_interval(20.0, self.show_quote)

    def animate(self):
        self.char_frame = (self.char_frame + 1) % 2

    def move(self):
        if not self.is_dead and random.random() < 0.6:
            self.x_offset = max(-15, min(15, self.x_offset + random.choice([-2, -1, 0, 1, 2])))

    def drift_clouds(self):
        self.cloud1_x = (self.cloud1_x + 1) % 80
        self.cloud2_x = (self.cloud2_x + 1) % 80
        self.cloud3_x = (self.cloud3_x + 2) % 80
        self.cloud4_x = (self.cloud4_x + 1) % 80

    def change_weather(self):
        if random.random() < 0.3:
            self.weather = random.choice(["clear", "rain", "snow"])

    def show_quote(self):
        if not self.is_dead and random.random() < 0.4:
            self.quote = random.choice(MOCHI_QUOTES)

    def is_night(self) -> bool:
        hour = datetime.now().hour
        return hour >= 20 or hour < 6

    def is_sleeping_time(self) -> bool:
        hour = datetime.now().hour
        return hour >= 22 or hour < 6

    def get_sprite(self) -> str:
        if self.is_dead:
            return "  .-.\n (X.X)\n  RIP"

        if self.is_sleeping_time():
            return "  .-.\n (- -)\n z z z"

        if self.emotion == "happy":
            return "  \\o/\n (^.^)\n  > <" if self.char_frame == 0 else "  \\o/\n (^o^)\n  < >"
        elif self.emotion == "hungry":
            return "  .-.\n (O.O)\n  ~~~"
        elif self.emotion == "sick":
            return "  .-.\n (;.;)\n  ..." if self.char_frame == 0 else "  .-.\n (~.~)\n  ..."
        else:
            return "  .-.\n (o.o)\n  > ^" if self.char_frame == 0 else "  .-.\n (o.o)\n  ^ <"

    def render(self) -> str:
        sprite = self.get_sprite()
        char_lines = sprite.split('\n')
        scene_lines = []

        if self.is_dead:
            scene_lines.extend([""] * 8)
            scene_lines.append("                         .-.                          ")
            scene_lines.append("                        (X.X)                         ")
            scene_lines.append("                         RIP                          ")
            scene_lines.append("")
            scene_lines.append("              Mochi is dead. How could you?           ")
            scene_lines.append("")
            scene_lines.append("                 Press R to restart...                ")
            scene_lines.extend([""] * 3)
            return '\n'.join(scene_lines)

        # SKY
        if self.is_night():
            scene_lines.append("  🌙")
            scene_lines.append(" " * self.cloud1_x + "✦")
            scene_lines.append(" " * self.cloud2_x + "★")
            scene_lines.append(" " * self.cloud3_x + "✧" + " " * max(5, abs(self.cloud4_x - self.cloud3_x)) + "⋆")
        else:
            scene_lines.append("  ☀️")
            if self.weather == "rain":
                scene_lines.append(" " * self.cloud1_x + "🌧️")
                scene_lines.append(" " * self.cloud2_x + "🌧️")
                scene_lines.append(" " * self.cloud3_x + "💧")
            elif self.weather == "snow":
                scene_lines.append(" " * self.cloud1_x + "❄️")
                scene_lines.append(" " * self.cloud2_x + "❄️")
                scene_lines.append(" " * self.cloud3_x + "❄️")
            else:
                scene_lines.append(" " * self.cloud1_x + "☁️")
                scene_lines.append(" " * self.cloud2_x + "☁️")
                scene_lines.append(" " * self.cloud3_x + "☁️" + " " * max(5, abs(self.cloud4_x - self.cloud3_x)) + "☁️")

        scene_lines.append("")
        scene_lines.append("")

        # QUOTE
        if self.quote:
            quote_line = f'"{self.quote}"'
            scene_lines.append(f"{quote_line:^80}")
        else:
            scene_lines.append("")

        # CHARACTER
        base_position = 38
        for line in char_lines:
            actual_pos = base_position + self.x_offset
            scene_lines.append(' ' * max(0, actual_pos) + line)

        scene_lines.append("")

        # POOP
        if self.poops > 0:
            poop_line = " " * (base_position + self.x_offset + 8) + "💩" * min(self.poops, 3)
            scene_lines.append(poop_line)
        else:
            scene_lines.append("")

        # GROUND
        scene_lines.append("   🌸      🌳        🌸         🌳              🌳")
        scene_lines.append("=" * 200)

        return '\n'.join(scene_lines)


if __name__ == "__main__":
    app = TamagotchiApp()
    app.run()
