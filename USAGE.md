# Terminal Tamagotchi - Usage Guide

## Quick Start

```bash
# Install dependencies
pip install textual

# Run the game
./tamagotchi.py
```

## Understanding the UI

```
╔════════════════════════════════════════════════════════════╗
║ Terminal Tamagotchi                            [Help] [Quit]║
╠════════════════════════════════════════════════════════════╣
║ ┌────────────────────────────────────────┐ ┌──────────────┐ ║
║ │  🐲 Lofty (Level 12)                   │ │📊 Stats:     │ ║
║ │  ████████░░░  XP: 2450/3000            │ │  Commits: 47 │ ║
║ │        ╭───╮                            │ │  Commands: 132│║
║ │        │👀 │ ← your pet walks around    │ │  Files: 245  │ ║
║ │        ╰───╯                            │ │              │ ║
║ │  Hunger: █████░░░░░ 50%                │ │🏆 Achievements│║
║ │  Happy:  ████████░░ 80%                │ │  ⭐ First    │ ║
║ │  Energy: ██████░░░░ 60%                │ │     Commit   │ ║
║ └────────────────────────────────────────┘ │  ⭐ Rising   │ ║
║ ┌────────────────────────────────────────┐ │     Star     │ ║
║ │ Activity Log                            │ └──────────────┘ ║
║ │ 10:30:15 SHIPPED! +500 XP 🎉            │                 ║
║ │ 10:28:42 +15 XP - Fun time!             │                 ║
║ │ 10:27:19 🍔 Nom nom nom! Thanks!        │                 ║
║ └────────────────────────────────────────┘                 ║
╠════════════════════════════════════════════════════════════╣
║ F:Feed P:Play S:Sleep C:Code! Q:Quit                        ║
╚════════════════════════════════════════════════════════════╝
```

## Stat Management

### Hunger 🍔
- **Decay Rate**: -0.6/min (medium)
- **Restore**: Press `F` to feed (+30%)
- **Warning**: < 20% pet complains
- **Effects**:
  - Decreases faster when coding
  - Increases when feeding
  - Slight increase when playing

### Happiness 😊
- **Decay Rate**: -0.48/min (slow)
- **Restore**: Press `P` to play (+25%)
- **Warning**: < 20% pet gets sad
- **Effects**:
  - Boosts from playing and coding
  - Required for random bonus events
  - Affects pet's emotion display

### Energy ⚡
- **Decay Rate**: -0.3/min (slowest)
- **Restore**: Press `S` to sleep (+40%)
- **Warning**: < 20% pet gets tired
- **Effects**:
  - Consumed by playing (-10%) and coding (-15%)
  - Required for activities
  - Restored by sleeping

## XP System

### XP Sources

| Action | XP Gain | Notes |
|--------|---------|-------|
| Feed | +10 | Basic care |
| Play | +15 | Social interaction |
| Sleep | +8 | Rest and recovery |
| **Code** | **+100-500** | 🚀 MASSIVE rewards! |
| Random Event | +30-50 | When stats > 50% |

### Level Progression

```
Level  | XP Required | Total XP
-------|-------------|----------
1      | 1,000       | 0
2      | 2,000       | 1,000
3      | 3,000       | 3,000
10     | 10,000      | 45,000
25     | 25,000      | 300,000
50     | 50,000      | 1,225,000
100    | 100,000     | 4,950,000
```

### Level-Up Bonuses

When you level up:
- ✨ +20% Hunger restored
- 🎉 +30% Happiness restored
- ⚡ +25% Energy restored
- 🏆 Possible achievement unlock

## Achievements

### Activity-Based
- **First Meal**: Feed your pet for the first time
- **Social Butterfly**: Play with your pet
- **First Commit**: Press C for the first time
- **Committed**: 10 code sessions
- **Git Master**: 50 code sessions
- **Bug Squasher**: 100 code sessions

### Level Milestones
- **Rising Star**: Reach level 10
- **Veteran Coder**: Reach level 25
- **Master Developer**: Reach level 50
- **LEGENDARY**: Reach level 100

## Character Emotions

Your pet's face changes based on stats:

```
👀 Normal      - Default (all stats OK)
😊 Happy       - Happiness > 80%
😢 Sad         - Happiness < 40%
🍔 Hungry      - Hunger < 30%
💤 Sleeping    - Energy < 30%
```

## Advanced Strategies

### Optimal Gameplay Loop

```
1. Start session → Feed to 100%
2. Code 2-3 times → Earn 300-1500 XP
3. Play once → Restore happiness
4. Sleep → Restore energy
5. Repeat
```

### XP Maximization

- **Focus on coding**: 10-50x more XP than other actions
- **Maintain high stats**: Enables random bonus events (+30-50 XP)
- **Level up strategically**: Plan to level when stats are low (free restore)
- **Don't over-maintain**: Feeding at 95% hunger wastes potential

### Idle Management

Stats decay in real-time even when the game is closed:

| Duration | Hunger Loss | Happy Loss | Energy Loss |
|----------|-------------|------------|-------------|
| 1 hour   | -30%        | -18%       | -24%        |
| 8 hours  | ⚠️ -100%    | -100%      | -100%       |
| 1 day    | ⚠️ -100%    | -100%      | -100%       |

**Tip**: Before closing, max out all stats!

## Random Events

When both Energy > 50% AND Happiness > 50%:
- 30% chance every 30 seconds
- Grants bonus XP
- Examples:
  - "✨ Found a shiny bug! +50 XP"
  - "💡 Great idea! +40 XP"
  - "🎨 Code looks beautiful! +35 XP"

## Save System

### Auto-Save
- Saves every 5 seconds while running
- Saves on quit
- Location: `~/.tamagotchi_save.json`

### Manual Save
The game saves automatically. Press `Q` to quit and ensure save.

### Backup Save
```bash
# Backup your save
cp ~/.tamagotchi_save.json ~/.tamagotchi_backup.json

# Restore from backup
cp ~/.tamagotchi_backup.json ~/.tamagotchi_save.json
```

### Reset Progress
```bash
# Delete save file to start fresh
rm ~/.tamagotchi_save.json
```

## Keyboard Controls

| Key | Action | Effect |
|-----|--------|--------|
| `F` | Feed | +30% hunger, +5% happiness, +10 XP |
| `P` | Play | +25% happiness, -10% energy, +15 XP |
| `S` | Sleep | +40% energy, -5% hunger, +8 XP |
| `C` | Code! | +100-500 XP, +20% happiness, -15% energy, -10% hunger |
| `Q` | Quit | Save and exit |

## Tips & Tricks

1. **Coding is King**: The C key gives 10-50x more XP than other actions
2. **Energy Management**: Keep energy > 20% to enable coding
3. **Happiness Multiplier**: High happiness enables bonus random events
4. **Decay Awareness**: Stats decay slower when game is closed vs running
5. **Level Planning**: Let stats drop before leveling (free restore!)
6. **Achievement Hunting**: Do 1 of each action early for quick unlocks
7. **Late Game**: At high levels, focus purely on coding for max XP/min

## Troubleshooting

### Pet Won't Accept Action
- **"Too tired to code"**: Sleep first (energy < 15%)
- **"I'm already full"**: Hunger already at 95%+
- **"Too tired to play"**: Energy < 20%

### Save File Issues
```bash
# Check save exists
ls -la ~/.tamagotchi_save.json

# View save contents
cat ~/.tamagotchi_save.json | python3 -m json.tool

# Fix corrupted save (resets progress!)
rm ~/.tamagotchi_save.json
```

### Display Issues
- Ensure terminal supports Unicode and emojis
- Minimum terminal size: 80x24
- Use modern terminal (iTerm2, Windows Terminal, etc.)

## Example Session

```
Session Start (11:00 AM):
- Hunger: 40%, Happy: 35%, Energy: 50%

Actions:
1. Feed (F) → Hunger: 70%, +10 XP
2. Play (P) → Happy: 60%, Energy: 40%, +15 XP
3. Code (C) → +350 XP! Happy: 80%, Energy: 25%
4. Sleep (S) → Energy: 65%, +8 XP
5. Code (C) → +420 XP! Level up! 🎉
6. Code (C) → +500 XP! Happy: 100%!
7. Random Event → "💡 Great idea! +40 XP"

Total XP Earned: 1,343
Time Spent: 5 minutes
Result: Level 12 → Level 13
```

## Community

Share your progress:
- Screenshot your highest level
- Share achievement screenshots
- Post funny pet reactions
- Compare XP farming strategies

Happy coding with your virtual pet! 🐲✨
