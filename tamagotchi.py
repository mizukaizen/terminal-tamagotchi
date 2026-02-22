#!/usr/bin/env python3
"""
Terminal Tamagotchi - Mochi Edition
Full feature set: day/night, weather, poop, milestones, sleep
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
            "poops": 0,
            "lifetime_hours": 0,
            "milestones": [],
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
    age = reactive(0)

    def on_mount(self):
        self.set_interval(0.5, self.animate)
        self.set_interval(2.0, self.move)
        self.set_interval(3.0, self.drift_clouds)
        self.set_interval(120.0, self.change_weather)

    def animate(self):
        self.char_frame = (self.char_frame + 1) % 2

    def move(self):
        if random.random() < 0.6:
            self.x_offset = max(-15, min(15, self.x_offset + random.choice([-2, -1, 0, 1, 2])))

    def drift_clouds(self):
        """Drift clouds across sky"""
        self.cloud1_x = (self.cloud1_x + 1) % 80
        self.cloud2_x = (self.cloud2_x + 1) % 80
        self.cloud3_x = (self.cloud3_x + 2) % 80
        self.cloud4_x = (self.cloud4_x + 1) % 80

    def change_weather(self):
        """Occasionally change weather"""
        if random.random() < 0.3:
            self.weather = random.choice(["clear", "rain", "snow"])

    def is_night(self) -> bool:
        """Check if it's nighttime (8pm - 6am)"""
        hour = datetime.now().hour
        return hour >= 20 or hour < 6

    def is_sleeping_time(self) -> bool:
        """Check if Mochi should be sleeping"""
        hour = datetime.now().hour
        return hour >= 22 or hour < 6

    def get_sprite(self) -> str:
        """Get character sprite"""
        # Sleep at night
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
        """Render complete scene"""
        sprite = self.get_sprite()
        char_lines = sprite.split('\n')
        scene_lines = []

        # SKY - day or night
        if self.is_night():
            # NIGHT SKY
            scene_lines.append("  🌙")
            scene_lines.append(" " * self.cloud1_x + "✦")
            scene_lines.append(" " * self.cloud2_x + "★")
            scene_lines.append(" " * self.cloud3_x + "✧" + " " * abs(self.cloud4_x - self.cloud3_x - 10) + "⋆")
        else:
            # DAY SKY
            scene_lines.append("  ☀️")

            # Weather-based clouds
            if self.weather == "rain":
                scene_lines.append(" " * self.cloud1_x + "🌧️")
                scene_lines.append(" " * self.cloud2_x + "🌧️")
                scene_lines.append(" " * self.cloud3_x + "💧")
            elif self.weather == "snow":
                scene_lines.append(" " * self.cloud1_x + "❄️")
                scene_lines.append(" " * self.cloud2_x + "❄️")
                scene_lines.append(" " * self.cloud3_x + "❄️")
            else:
                # Clear sky with clouds
                scene_lines.append(" " * self.cloud1_x + "☁️")
                scene_lines.append(" " * self.cloud2_x + "☁️")
                scene_lines.append(" " * self.cloud3_x + "☁️" + " " * max(5, abs(self.cloud4_x - self.cloud3_x)) + "☁️")

        # Space between sky and ground
        scene_lines.append("")
        scene_lines.append("")

        # CHARACTER (Mochi) - walks left/right
        base_position = 38
        for line in char_lines:
            actual_pos = base_position + self.x_offset
            scene_lines.append(' ' * max(0, actual_pos) + line)

        # Small gap
        scene_lines.append("")

        # POOP - show if present
        poop_line = ""
        if self.poops > 0:
            poop_line = " " * (base_position + self.x_offset + 8) + "💩" * min(self.poops, 3)
        scene_lines.append(poop_line)

        # GROUND ELEMENTS - flowers and trees
        scene_lines.append("   🌸      🌳        🌸         🌳              🌳")

        # GROUND LINE
        scene_lines.append("=" * 200)

        return '\n'.join(scene_lines)


class TopBar(Static):
    """Top HUD bar"""
    name = reactive("Mochi")
    milestone = reactive("")

    def render(self) -> str:
        title = f"[bold cyan]< {self.name.upper()} >[/bold cyan]"
        controls = "[dim]Feed: [cyan]F[/cyan]  |  Clean: [cyan]C[/cyan]  |  Quit: [cyan]Q[/cyan][/dim]"

        # Show milestone if present
        if self.milestone:
            return f"{title}  [yellow]{self.milestone}[/yellow]{' ' * 20}{controls}"
        return f"{title:<40}{controls:>40}"


class BottomBar(Static):
    """Bottom HUD bar with stats"""

    hunger = reactive(4)
    health = reactive(4)
    age = reactive(0)
    weight = reactive(5)
    lifetime_hours = reactive(0)

    def render(self) -> str:
        hf, he = chr(0x2665), chr(0x2661)
        h_hearts = hf * self.hunger + he * (4 - self.hunger)
        hp_hearts = hf * self.health + he * (4 - self.health)

        age_display = f"{self.age}h"
        if self.lifetime_hours > 0:
            age_display += f" (Life: {self.lifetime_hours}h)"

        return f"[cyan]HUNGRY:[/cyan] {h_hearts}  [cyan]|[/cyan]  [cyan]HEALTH:[/cyan] {hp_hearts}  [cyan]|[/cyan]  [cyan]AGE:[/cyan] {age_display}  [cyan]|[/cyan]  [cyan]WT:[/cyan] {self.weight}kg"


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
        padding: 0 2;
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
        char.poops = self.state["poops"]
        char.age = self.state["lifetime_hours"]
        bottom.hunger = self.state["hunger"]
        bottom.health = self.state["health"]
        bottom.age = self.state["age_hours"]
        bottom.weight = self.state["weight"]
        bottom.lifetime_hours = self.state["lifetime_hours"]

        self.calculate_decay()
        self.update_emotion()

        # Game loops
        self.set_interval(60.0, self.age_tick)
        self.set_interval(300.0, self.hunger_tick)
        self.set_interval(10.0, self.check_health)
        self.set_interval(10.0, self.save_game)
        self.set_interval(600.0, self.poop_check)  # Poop every 10 min if well-fed

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
        """Age the pet and check milestones"""
        bottom = self.query_one("#bottom", BottomBar)
        top = self.query_one("#top", TopBar)
        char = self.query_one("#character", Character)

        bottom.age += 1
        bottom.lifetime_hours += 1
        char.age = bottom.lifetime_hours

        self.state["age_hours"] = bottom.age
        self.state["lifetime_hours"] = bottom.lifetime_hours

        # Check milestones
        if bottom.lifetime_hours == 24 and "day1" not in self.state["milestones"]:
            self.state["milestones"].append("day1")
            top.milestone = "★ 1 Day Old! ★"
            self.set_timer(5.0, lambda: setattr(top, "milestone", ""))

        elif bottom.lifetime_hours == 72 and "day3" not in self.state["milestones"]:
            self.state["milestones"].append("day3")
            top.milestone = "★ 3 Days Old! ★"
            self.set_timer(5.0, lambda: setattr(top, "milestone", ""))

        elif bottom.lifetime_hours == 168 and "week1" not in self.state["milestones"]:
            self.state["milestones"].append("week1")
            top.milestone = "★★ 1 Week! ★★"
            self.set_timer(5.0, lambda: setattr(top, "milestone", ""))

    def hunger_tick(self):
        bottom = self.query_one("#bottom", BottomBar)
        if bottom.hunger > 0:
            bottom.hunger -= 1
            self.state["hunger"] = bottom.hunger
            self.update_emotion()

    def poop_check(self):
        """Random poop generation when well-fed"""
        bottom = self.query_one("#bottom", BottomBar)
        char = self.query_one("#character", Character)

        if bottom.hunger >= 3 and char.poops < 3 and random.random() < 0.6:
            char.poops += 1
            self.state["poops"] = char.poops

    def check_health(self):
        """Health mechanics"""
        bottom = self.query_one("#bottom", BottomBar)
        char = self.query_one("#character", Character)

        # Lose health when starving
        if bottom.hunger == 0 and random.random() < 0.4:
            bottom.health = max(0, bottom.health - 1)
            self.state["health"] = bottom.health
            self.update_emotion()

        # Lose health from poop buildup
        elif char.poops >= 2 and random.random() < 0.3:
            bottom.health = max(0, bottom.health - 1)
            self.state["health"] = bottom.health
            self.update_emotion()

        # Regain health when well-fed and clean
        elif bottom.hunger >= 3 and char.poops == 0 and bottom.health < 4 and random.random() < 0.3:
            bottom.health = min(4, bottom.health + 1)
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
        char = self.query_one("#character", Character)

        self.state["hunger"] = bottom.hunger
        self.state["health"] = bottom.health
        self.state["age_hours"] = bottom.age
        self.state["weight"] = bottom.weight
        self.state["lifetime_hours"] = bottom.lifetime_hours
        self.state["poops"] = char.poops
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

    def action_clean(self):
        """Clean up poops"""
        char = self.query_one("#character", Character)
        if char.poops > 0:
            char.poops = 0
            self.state["poops"] = 0


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
    age = reactive(0)

    def on_mount(self):
        self.set_interval(0.5, self.animate)
        self.set_interval(2.0, self.move)
        self.set_interval(3.0, self.drift_clouds)
        self.set_interval(120.0, self.change_weather)

    def animate(self):
        self.char_frame = (self.char_frame + 1) % 2

    def move(self):
        if random.random() < 0.6:
            self.x_offset = max(-15, min(15, self.x_offset + random.choice([-2, -1, 0, 1, 2])))

    def drift_clouds(self):
        self.cloud1_x = (self.cloud1_x + 1) % 80
        self.cloud2_x = (self.cloud2_x + 1) % 80
        self.cloud3_x = (self.cloud3_x + 2) % 80
        self.cloud4_x = (self.cloud4_x + 1) % 80

    def change_weather(self):
        if random.random() < 0.3:
            self.weather = random.choice(["clear", "rain", "snow"])

    def is_night(self) -> bool:
        hour = datetime.now().hour
        return hour >= 20 or hour < 6

    def is_sleeping_time(self) -> bool:
        hour = datetime.now().hour
        return hour >= 22 or hour < 6

    def get_sprite(self) -> str:
        # Sleep at night
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
        padding: 0 2;
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
        char.poops = self.state["poops"]
        char.age = self.state["lifetime_hours"]
        bottom.hunger = self.state["hunger"]
        bottom.health = self.state["health"]
        bottom.age = self.state["age_hours"]
        bottom.weight = self.state["weight"]
        bottom.lifetime_hours = self.state["lifetime_hours"]

        self.calculate_decay()
        self.update_emotion()

        self.set_interval(60.0, self.age_tick)
        self.set_interval(300.0, self.hunger_tick)
        self.set_interval(10.0, self.check_health)
        self.set_interval(10.0, self.save_game)
        self.set_interval(600.0, self.poop_check)

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
        top = self.query_one("#top", TopBar)
        char = self.query_one("#character", Character)

        bottom.age += 1
        bottom.lifetime_hours += 1
        char.age = bottom.lifetime_hours
        self.state["age_hours"] = bottom.age
        self.state["lifetime_hours"] = bottom.lifetime_hours

        # Milestones
        if bottom.lifetime_hours == 24 and "day1" not in self.state["milestones"]:
            self.state["milestones"].append("day1")
            top.milestone = "★ 1 Day Old! ★"
            self.set_timer(5.0, lambda: setattr(top, "milestone", ""))
        elif bottom.lifetime_hours == 72 and "day3" not in self.state["milestones"]:
            self.state["milestones"].append("day3")
            top.milestone = "★ 3 Days Old! ★"
            self.set_timer(5.0, lambda: setattr(top, "milestone", ""))
        elif bottom.lifetime_hours == 168 and "week1" not in self.state["milestones"]:
            self.state["milestones"].append("week1")
            top.milestone = "★★ 1 Week! ★★"
            self.set_timer(5.0, lambda: setattr(top, "milestone", ""))

    def hunger_tick(self):
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
        bottom = self.query_one("#bottom", BottomBar)
        char = self.query_one("#character", Character)

        if bottom.hunger == 0 and random.random() < 0.4:
            bottom.health = max(0, bottom.health - 1)
            self.state["health"] = bottom.health
            self.update_emotion()
        elif char.poops >= 2 and random.random() < 0.3:
            bottom.health = max(0, bottom.health - 1)
            self.state["health"] = bottom.health
            self.update_emotion()
        elif bottom.hunger >= 3 and char.poops == 0 and bottom.health < 4 and random.random() < 0.3:
            bottom.health = min(4, bottom.health + 1)
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
        char = self.query_one("#character", Character)
        self.state["hunger"] = bottom.hunger
        self.state["health"] = bottom.health
        self.state["age_hours"] = bottom.age
        self.state["weight"] = bottom.weight
        self.state["lifetime_hours"] = bottom.lifetime_hours
        self.state["poops"] = char.poops
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

    def action_clean(self):
        char = self.query_one("#character", Character)
        if char.poops > 0:
            char.poops = 0
            self.state["poops"] = 0


if __name__ == "__main__":
    app = TamagotchiApp()
    app.run()
