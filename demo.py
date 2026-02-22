#!/usr/bin/env python3
"""Quick demo of Terminal Tamagotchi features"""

import json
from pathlib import Path

# Create a demo save file
demo_save = {
    "name": "Lofty",
    "level": 12,
    "xp": 2450,
    "hunger": 50,
    "happiness": 80,
    "energy": 60,
    "total_commits": 47,
    "total_commands": 132,
    "total_files": 245,
    "achievements": [
        "First Commit",
        "Committed",
        "Rising Star",
        "Social Butterfly",
        "First Meal"
    ],
    "last_save": "2026-02-22T10:30:00",
    "birth_date": "2026-02-15T08:00:00",
}

print("🎮 Terminal Tamagotchi - Demo")
print("=" * 50)
print()

# Show stats display
print("📊 Game State:")
print(f"  Name: {demo_save['name']}")
print(f"  Level: {demo_save['level']}")
print(f"  XP: {demo_save['xp']}/3000")
print(f"  Hunger: {demo_save['hunger']}%")
print(f"  Happiness: {demo_save['happiness']}%")
print(f"  Energy: {demo_save['energy']}%")
print()

# Show stats
print("📈 Activity Stats:")
print(f"  Total Commits: {demo_save['total_commits']}")
print(f"  Commands Run: {demo_save['total_commands']}")
print(f"  Files Created: {demo_save['total_files']}")
print()

# Show achievements
print("🏆 Achievements Unlocked:")
for ach in demo_save['achievements']:
    print(f"  ⭐ {ach}")
print()

# Show ASCII art
print("🐲 Your Pet:")
print("  " + "█" * 8 + "░" * 2 + "  XP: 2450/3000")
print()
print("    🐲")
print("   (👀)")
print("    ||")
print()

# Show stat bars
hunger_filled = int((demo_save['hunger'] / 100) * 10)
happiness_filled = int((demo_save['happiness'] / 100) * 10)
energy_filled = int((demo_save['energy'] / 100) * 10)

print(f"  Hunger: {'█' * hunger_filled}{'░' * (10 - hunger_filled)} {demo_save['hunger']}%")
print(f"  Happy:  {'█' * happiness_filled}{'░' * (10 - happiness_filled)} {demo_save['happiness']}%")
print(f"  Energy: {'█' * energy_filled}{'░' * (10 - energy_filled)} {demo_save['energy']}%")
print()

# Show example messages
print("💬 Recent Activity:")
print("  10:30:15 SHIPPED! +500 XP 🎉")
print("  10:28:42 +15 XP - Fun time!")
print("  10:27:19 🍔 Nom nom nom! Thanks!")
print()

print("🎮 Press F to feed, P to play, S to sleep, C to code, Q to quit")
print()
print("To start the real game, run:")
print("  ./tamagotchi.py")
print("  or: python tamagotchi.py")
print()
