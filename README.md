# 🐲 Terminal Tamagotchi

A virtual pet that lives in your terminal and reacts to your coding activity!

## Features

- **Animated Character**: Watch your pet walk around and react with emotions
- **Real-time Stats**: Manage hunger, happiness, and energy levels
- **Level System**: Earn XP and level up from 1 to 100
- **Achievements**: Unlock milestones as you code
- **Activity Tracking**: Tracks commits, commands, and file creation
- **Persistent State**: Your pet remembers you between sessions
- **Interactive Commands**: Feed, play, sleep, and code with your pet

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Make executable
chmod +x tamagotchi.py
```

## Usage

```bash
# Run the game
./tamagotchi.py

# Or with Python
python tamagotchi.py
```

## Controls

- **F** - Feed your pet (restores hunger)
- **P** - Play with your pet (increases happiness)
- **S** - Put pet to sleep (restores energy)
- **C** - Code! (earn big XP rewards)
- **Q** - Quit and save

## Gameplay

### Stats
- **Hunger**: Decreases over time, restore by feeding
- **Happiness**: Decreases slowly, boost by playing or coding
- **Energy**: Consumed by activities, restore with sleep

### Earning XP
- **Feed**: +10 XP
- **Play**: +15 XP
- **Sleep**: +8 XP
- **Code**: +100-500 XP (MASSIVE rewards!)
- **Random Events**: +30-50 XP

### Leveling
- Each level requires `level * 1000` XP
- Level up restores stats and unlocks achievements
- 100 levels total

### Achievements
- **First Meal**: Feed your pet for the first time
- **First Commit**: Make your first code commit
- **Social Butterfly**: Play with your pet
- **Committed**: 10 commits
- **Git Master**: 50 commits
- **Bug Squasher**: 100 commits
- **Rising Star**: Reach level 10
- **Veteran Coder**: Reach level 25
- **Master Developer**: Reach level 50
- **LEGENDARY**: Reach level 100

## Save File

Game state is saved to `~/.tamagotchi_save.json` automatically every 5 seconds and when you quit.

## Character Emotions

Your pet reacts to its stats:
- 😊 **Happy**: When happiness > 80%
- 😢 **Sad**: When happiness < 40%
- 🍔 **Hungry**: When hunger < 30%
- 💤 **Sleeping**: When energy < 30%
- 👀 **Normal**: Default walking animation

## Tips

- Keep all stats balanced for optimal XP gain
- Code regularly for massive XP boosts
- Random events trigger when energy and happiness are high
- Don't let stats drop too low or your pet will complain!
- The pet ages in real-time even when the game is closed

## Example Session

```
╭──────────────────────────────────╮
│  🐲 Lofty (Level 12)             │
│  ████████░░░  XP: 2450/3000     │
│        ╭───╮                     │
│        │👀 │ ← walking around     │
│        ╰───╯                     │
│  Hunger: █████░░░ 50%             │
│  Happy:  ████████░ 80%            │
│  Energy: ██████░░░ 60%            │
│  > SHIPPED! +500 XP 🎉            │
╰──────────────────────────────────╯
```

## License

MIT - Have fun! 🎮
