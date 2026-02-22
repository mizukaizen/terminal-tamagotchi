#!/usr/bin/env python3
"""
Terminal Tamagotchi - A virtual pet that lives in your terminal and reacts to your coding activity
"""

import json
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Label, Header, Footer
from textual.reactive import reactive
from textual import work
from textual.timer import Timer


class GameData:
    """Manages game state persistence"""

    def __init__(self, save_file: Path = Path.home() / ".tamagotchi_save.json"):
        self.save_file = save_file
        self.data = self.load()

    def load(self) -> dict:
        """Load game state from disk"""
        if self.save_file.exists():
            try:
                with open(self.save_file) as f:
                    return json.load(f)
            except Exception:
                pass

        # Default state
        return {
            "name": "Lofty",
            "level": 1,
            "xp": 0,
            "hunger": 100,
            "happiness": 100,
            "energy": 100,
            "total_commits": 0,
            "total_commands": 0,
            "total_files": 0,
            "achievements": [],
            "last_save": datetime.now().isoformat(),
            "birth_date": datetime.now().isoformat(),
        }

    def save(self, data: dict):
        """Save game state to disk"""
        data["last_save"] = datetime.now().isoformat()
        try:
            with open(self.save_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            pass

    def calculate_decay(self, data: dict) -> dict:
        """Calculate stat decay based on time passed"""
        try:
            last_save = datetime.fromisoformat(data["last_save"])
            now = datetime.now()
            minutes_passed = (now - last_save).total_seconds() / 60

            # Decay rates per minute
            hunger_decay = min(minutes_passed * 0.5, 50)  # Max 50 decay
            happiness_decay = min(minutes_passed * 0.3, 40)
            energy_decay = min(minutes_passed * 0.4, 45)

            data["hunger"] = max(0, data["hunger"] - hunger_decay)
            data["happiness"] = max(0, data["happiness"] - happiness_decay)
            data["energy"] = max(0, data["energy"] - energy_decay)
        except Exception:
            pass

        return data


class Character(Static):
    """Animated character widget"""

    # Animation frames
    FRAMES = [
        "  🐲\n (👀)\n  ||",
        "  🐲\n (👀)\n  /\\",
        "  🐲\n (👀)\n  ||",
        "  🐲\n (👀)\n  \\/",
    ]

    SLEEPING = "  🐲\n (💤)\n  ||"
    HAPPY = "  🐲\n (😊)\n  ||"
    SAD = "  🐲\n (😢)\n  ||"
    HUNGRY = "  🐲\n (🍔)\n  ||"

    position = reactive(0)
    frame = reactive(0)
    emotion = reactive("normal")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.walking = True

    def on_mount(self) -> None:
        self.set_interval(0.3, self.animate)
        self.set_interval(1.0, self.move)

    def animate(self):
        """Cycle through animation frames"""
        if self.walking:
            self.frame = (self.frame + 1) % len(self.FRAMES)

    def move(self):
        """Move character position"""
        if self.walking:
            self.position = (self.position + 1) % 30

    def render(self) -> str:
        """Render character with current emotion"""
        if self.emotion == "sleeping":
            char = self.SLEEPING
        elif self.emotion == "happy":
            char = self.HAPPY
        elif self.emotion == "sad":
            char = self.SAD
        elif self.emotion == "hungry":
            char = self.HUNGRY
        else:
            char = self.FRAMES[self.frame]

        # Add padding for position
        padding = " " * self.position
        lines = char.split("\n")
        return "\n".join(padding + line for line in lines)


class StatBar(Static):
    """Progress bar for stats"""

    value = reactive(100)

    def __init__(self, label: str, max_val: int = 100, color: str = "green", **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.max_val = max_val
        self.color = color

    def render(self) -> str:
        """Render stat bar"""
        filled = int((self.value / self.max_val) * 10)
        bar = "█" * filled + "░" * (10 - filled)

        # Color based on value
        if self.value < 30:
            color = "red"
        elif self.value < 60:
            color = "yellow"
        else:
            color = self.color

        return f"[{color}]{self.label}: {bar} {int(self.value)}%[/{color}]"


class XPBar(Static):
    """XP progress bar with level"""

    xp = reactive(0)
    level = reactive(1)

    def get_xp_for_level(self, level: int) -> int:
        """Calculate XP needed for level"""
        return level * 1000

    def render(self) -> str:
        """Render XP bar"""
        xp_needed = self.get_xp_for_level(self.level)
        xp_progress = self.xp % xp_needed
        filled = int((xp_progress / xp_needed) * 20)
        bar = "█" * filled + "░" * (20 - filled)

        return f"[cyan]{bar} XP: {xp_progress}/{xp_needed}[/cyan]"


class MessageLog(Static):
    """Scrolling message log"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.messages = []
        self.max_messages = 5

    def add_message(self, msg: str, style: str = ""):
        """Add a message to the log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if style:
            formatted = f"[dim]{timestamp}[/dim] [{style}]{msg}[/{style}]"
        else:
            formatted = f"[dim]{timestamp}[/dim] {msg}"

        self.messages.append(formatted)
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
        self.update("\n".join(self.messages))


class StatsDisplay(Static):
    """Display for game statistics"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stats = {
            "commits": 0,
            "commands": 0,
            "files": 0,
        }

    def render(self) -> str:
        return (
            f"[dim]📊 Stats:[/dim]\n"
            f"  Commits: {self.stats['commits']}\n"
            f"  Commands: {self.stats['commands']}\n"
            f"  Files: {self.stats['files']}"
        )


class AchievementDisplay(Static):
    """Display recent achievements"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.achievements = []

    def add_achievement(self, achievement: str):
        """Add new achievement"""
        self.achievements.insert(0, achievement)
        if len(self.achievements) > 3:
            self.achievements.pop()
        self.refresh()

    def render(self) -> str:
        if not self.achievements:
            return "[dim]🏆 No achievements yet[/dim]"

        display = "[yellow bold]🏆 Achievements:[/yellow bold]\n"
        for ach in self.achievements:
            display += f"  ⭐ {ach}\n"
        return display.rstrip()


class TamagotchiApp(App):
    """Main Tamagotchi application"""

    CSS = """
    Screen {
        background: $surface;
    }

    #main_container {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }

    #pet_area {
        border: heavy white;
        height: 12;
        padding: 1 2;
        background: $panel;
    }

    #stats_area {
        height: 8;
        padding: 1;
        margin-top: 1;
    }

    #message_area {
        border: solid cyan;
        height: 8;
        padding: 1;
        margin-top: 1;
        background: $panel;
    }

    #side_panel {
        width: 30;
        margin-left: 1;
    }

    Character {
        height: 5;
        content-align: center middle;
    }

    .title {
        text-align: center;
        text-style: bold;
    }
    """

    BINDINGS = [
        ("f", "feed", "Feed (F)"),
        ("p", "play", "Play (P)"),
        ("s", "sleep", "Sleep (S)"),
        ("c", "code", "Code! (C)"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.game_data = GameData()
        self.state = self.game_data.load()
        self.state = self.game_data.calculate_decay(self.state)

    def compose(self) -> ComposeResult:
        """Create UI layout"""
        yield Header()

        with Container(id="main_container"):
            with Horizontal():
                with Vertical():
                    # Pet display area
                    with Container(id="pet_area"):
                        yield Label(
                            f"🐲 {self.state['name']} (Level {self.state['level']})",
                            classes="title"
                        )
                        yield XPBar(id="xp_bar")
                        yield Character(id="character")

                    # Stats area
                    with Container(id="stats_area"):
                        yield StatBar("Hunger", color="red", id="hunger_bar")
                        yield StatBar("Happy", color="yellow", id="happiness_bar")
                        yield StatBar("Energy", color="blue", id="energy_bar")

                    # Message log
                    with Container(id="message_area"):
                        yield Label("[bold cyan]Activity Log[/bold cyan]")
                        yield MessageLog(id="messages")

                # Side panel
                with Vertical(id="side_panel"):
                    yield StatsDisplay(id="stats_display")
                    yield Static("")  # Spacer
                    yield AchievementDisplay(id="achievements")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize app state"""
        # Check for level up from loaded XP
        self.check_level_up()

        # Update UI with loaded state
        self.update_ui()

        # Start game loops
        self.set_interval(1.0, self.update_stats)
        self.set_interval(5.0, self.save_game)
        self.set_interval(30.0, self.random_event)

        # Monitor activity
        self.monitor_activity()

        # Welcome message
        messages = self.query_one("#messages", MessageLog)
        messages.add_message(f"👋 Welcome back! {self.state['name']} missed you!", "green")

    def update_ui(self):
        """Update all UI elements with current state"""
        # Update stat bars
        self.query_one("#hunger_bar", StatBar).value = self.state["hunger"]
        self.query_one("#happiness_bar", StatBar).value = self.state["happiness"]
        self.query_one("#energy_bar", StatBar).value = self.state["energy"]

        # Update XP bar
        xp_bar = self.query_one("#xp_bar", XPBar)
        xp_bar.xp = self.state["xp"]
        xp_bar.level = self.state["level"]

        # Update stats display
        stats = self.query_one("#stats_display", StatsDisplay)
        stats.stats["commits"] = self.state["total_commits"]
        stats.stats["commands"] = self.state["total_commands"]
        stats.stats["files"] = self.state["total_files"]
        stats.refresh()

        # Update character emotion
        char = self.query_one("#character", Character)
        if self.state["energy"] < 30:
            char.emotion = "sleeping"
        elif self.state["hunger"] < 30:
            char.emotion = "hungry"
        elif self.state["happiness"] < 40:
            char.emotion = "sad"
        elif self.state["happiness"] > 80:
            char.emotion = "happy"
        else:
            char.emotion = "normal"

    def update_stats(self):
        """Decay stats over time"""
        # Decay rates per second
        self.state["hunger"] = max(0, self.state["hunger"] - 0.01)
        self.state["happiness"] = max(0, self.state["happiness"] - 0.008)
        self.state["energy"] = max(0, self.state["energy"] - 0.005)

        # Check for warnings
        if self.state["hunger"] < 20 and random.random() < 0.1:
            self.add_message("😿 I'm starving! Feed me!", "red bold")

        if self.state["happiness"] < 20 and random.random() < 0.1:
            self.add_message("😢 I'm so lonely... Play with me?", "yellow")

        if self.state["energy"] < 20 and random.random() < 0.1:
            self.add_message("😴 So tired... Need sleep...", "blue")

        self.update_ui()

    def add_xp(self, amount: int, reason: str = ""):
        """Add XP and check for level up"""
        self.state["xp"] += amount

        msg = f"+{amount} XP"
        if reason:
            msg += f" - {reason}"

        self.add_message(msg, "cyan bold")

        self.check_level_up()
        self.update_ui()

    def check_level_up(self):
        """Check if pet leveled up"""
        xp_bar = self.query_one("#xp_bar", XPBar)
        xp_needed = xp_bar.get_xp_for_level(self.state["level"])

        while self.state["xp"] >= xp_needed:
            self.state["level"] += 1
            self.add_message(f"🎉 LEVEL UP! Now level {self.state['level']}!", "green bold")

            # Restore some stats on level up
            self.state["hunger"] = min(100, self.state["hunger"] + 20)
            self.state["happiness"] = min(100, self.state["happiness"] + 30)
            self.state["energy"] = min(100, self.state["energy"] + 25)

            # Check for milestone achievements
            if self.state["level"] == 10:
                self.unlock_achievement("Rising Star")
            elif self.state["level"] == 25:
                self.unlock_achievement("Veteran Coder")
            elif self.state["level"] == 50:
                self.unlock_achievement("Master Developer")
            elif self.state["level"] == 100:
                self.unlock_achievement("LEGENDARY")

            xp_needed = xp_bar.get_xp_for_level(self.state["level"])

    def unlock_achievement(self, name: str):
        """Unlock a new achievement"""
        if name not in self.state["achievements"]:
            self.state["achievements"].append(name)
            self.add_message(f"🏆 Achievement Unlocked: {name}!", "yellow bold")
            ach_display = self.query_one("#achievements", AchievementDisplay)
            ach_display.add_achievement(name)

    def add_message(self, msg: str, style: str = ""):
        """Add message to log"""
        messages = self.query_one("#messages", MessageLog)
        messages.add_message(msg, style)

    def save_game(self):
        """Save current game state"""
        self.game_data.save(self.state)

    def random_event(self):
        """Trigger random events"""
        if random.random() < 0.3:
            events = [
                ("✨ Found a shiny bug!", 50),
                ("🌟 Feeling inspired!", 30),
                ("💡 Great idea!", 40),
                ("🎨 Code looks beautiful!", 35),
            ]

            if self.state["energy"] > 50 and self.state["happiness"] > 50:
                event, xp = random.choice(events)
                self.add_xp(xp, event)

    @work(thread=True)
    def monitor_activity(self):
        """Monitor git activity and file changes"""
        # This would normally watch for git commits, file changes, etc.
        # For demo purposes, we'll just track basic activity
        pass

    def action_feed(self):
        """Feed the pet"""
        if self.state["hunger"] >= 95:
            self.add_message("😋 I'm already full!", "yellow")
            return

        self.state["hunger"] = min(100, self.state["hunger"] + 30)
        self.state["happiness"] = min(100, self.state["happiness"] + 5)
        self.add_xp(10, "Yummy!")
        self.add_message("🍔 Nom nom nom! Thanks!", "green")

        # Check achievement
        if self.state["total_commands"] == 0:
            self.unlock_achievement("First Meal")

        self.state["total_commands"] += 1
        self.update_ui()

    def action_play(self):
        """Play with the pet"""
        if self.state["energy"] < 20:
            self.add_message("😴 Too tired to play... Need sleep.", "red")
            return

        self.state["happiness"] = min(100, self.state["happiness"] + 25)
        self.state["energy"] = max(0, self.state["energy"] - 10)
        self.add_xp(15, "Fun time!")

        play_messages = [
            "🎮 Wheee! That was fun!",
            "🎯 You got me! Hehe!",
            "🏃 Catch me if you can!",
            "⚽ Great play!",
        ]
        self.add_message(random.choice(play_messages), "yellow")

        if "Social Butterfly" not in self.state["achievements"] and random.random() < 0.2:
            self.unlock_achievement("Social Butterfly")

        self.state["total_commands"] += 1
        self.update_ui()

    def action_sleep(self):
        """Put pet to sleep"""
        if self.state["energy"] >= 95:
            self.add_message("😊 I'm not tired yet!", "cyan")
            return

        self.state["energy"] = min(100, self.state["energy"] + 40)
        self.state["hunger"] = max(0, self.state["hunger"] - 5)
        self.add_xp(8, "Good rest")
        self.add_message("😴 Zzz... *yawn* Refreshed!", "blue")

        self.state["total_commands"] += 1
        self.update_ui()

    def action_code(self):
        """Simulate coding activity"""
        if self.state["energy"] < 15:
            self.add_message("😫 Too exhausted to code! Need rest.", "red")
            return

        # Big rewards for coding!
        xp_gain = random.randint(100, 500)
        self.state["energy"] = max(0, self.state["energy"] - 15)
        self.state["happiness"] = min(100, self.state["happiness"] + 20)
        self.state["hunger"] = max(0, self.state["hunger"] - 10)

        code_events = [
            (f"SHIPPED! +{xp_gain} XP 🎉", xp_gain),
            (f"MERGED PR! +{xp_gain} XP 🚀", xp_gain),
            (f"FIXED BUG! +{xp_gain} XP 🐛", xp_gain),
            (f"REFACTORED! +{xp_gain} XP ✨", xp_gain),
        ]

        event, xp = random.choice(code_events)
        self.add_xp(xp, "")
        self.add_message(event, "green bold")

        # Update stats
        self.state["total_commits"] += 1
        self.state["total_files"] += random.randint(1, 5)

        # Achievement checks
        if self.state["total_commits"] == 1:
            self.unlock_achievement("First Commit")
        elif self.state["total_commits"] == 10:
            self.unlock_achievement("Committed")
        elif self.state["total_commits"] == 50:
            self.unlock_achievement("Git Master")
        elif self.state["total_commits"] == 100:
            self.unlock_achievement("Bug Squasher")

        self.state["total_commands"] += 1
        self.update_ui()


if __name__ == "__main__":
    app = TamagotchiApp()
    app.run()
