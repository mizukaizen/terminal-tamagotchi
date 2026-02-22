# 🍡 Mochi - Terminal Tamagotchi

A living, breathing virtual pet in your terminal! Watch Mochi explore a dynamic world with day/night cycles, weather changes, and authentic Tamagotchi gameplay.

![Mochi Screenshot](screenshot.txt)

## 🎮 Screenshot

```
< MOCHI >                                      Feed: F  |  Clean: C  |  Quit: Q

  ☀️
                              ☁️
                                                              ☁️
                 ☁️                                    ☁️



                                    .-.
                                   (o.o)
                                    > ^


   🌸      🌳        🌸         🌳              🌳
================================================================================

           HUNGRY: ♥♥♥♥  |  HEALTH: ♥♥♥♥  |  AGE: 12h  |  WT: 8kg
```

## ✨ Features

### 🌍 Living World
- **Day/Night Cycle** - Sun ☀️ during day, Moon 🌙 and stars ✦★ at night
- **Dynamic Weather** - Clear ☁️, Rain 🌧️, or Snow ❄️ that changes every few minutes
- **Drifting Clouds** - Clouds slowly move across the sky
- **Sleeping** - Mochi sleeps at night (10pm-6am) with peaceful Z's

### 🐾 Mochi Behaviors
- **Walking Animation** - Mochi walks left and right exploring
- **Emotions** - Happy (^.^), Normal (o.o), Hungry (O.O), Sick (;.;)
- **Automatic Sleeping** - Falls asleep at bedtime with closed eyes

### 💩 Classic Tamagotchi Mechanics
- **Hunger System** - 4-heart hunger meter, feed every 5 minutes
- **Health System** - Health drops when starving or dirty, regenerates when well-cared-for
- **Poop Mechanic** - Mochi poops when well-fed (up to 3 💩)
- **Cleaning Required** - Must clean poop or health drops!
- **Weight Tracking** - Mochi gains weight when fed

### 🏆 Progression
- **Age Tracking** - Age resets each session, lifetime hours persist
- **Milestones** - Achievements at 1 day, 3 days, 1 week
- **Lifetime Stats** - Tracks total hours lived across all sessions

## 🎯 Installation

```bash
# Clone the repository
git clone https://github.com/mizukaizen/terminal-tamagotchi.git
cd terminal-tamagotchi

# Install dependencies
pip3 install textual

# Run Mochi!
./tamagotchi.py
```

Or with Python directly:
```bash
python3 tamagotchi.py
```

## 🎮 How to Play

### Controls
- **F** or **Space** - Feed Mochi
- **C** - Clean up poop 💩
- **Q** - Quit and save

### Gameplay Loop

1. **Feed Mochi** every 5 minutes to keep hunger at ♥♥♥♥
2. **Clean poop** when it appears (press C)
3. **Watch health** - it regenerates when Mochi is well-fed and clean
4. **Enjoy** - Watch Mochi walk around, clouds drift, weather change!

### Game Mechanics

**Hunger (♥♥♥♥):**
- Drops 1 heart every 5 minutes
- Feed to restore hearts
- At ♡♡♡♡ (empty), Mochi is starving!

**Health (♥♥♥♥):**
- **Decreases when:**
  - Starving (hunger = ♡♡♡♡)
  - Too much poop (2+ 💩)
- **Increases when:**
  - Well-fed (hunger >= ♥♥♥)
  - Clean (no poop)
  - Slowly regenerates over time

**Poop (💩):**
- Appears every 10 minutes when well-fed
- Up to 3 can accumulate
- Press **C** to clean
- Dirty Mochi gets sick!

**Weight:**
- Starts at 5kg
- Gains 1kg every time you feed
- Tracks how much you've fed Mochi

**Age:**
- **Session Age:** Resets to 0h each time you start
- **Lifetime:** Tracks total hours across all sessions
- Milestones unlock at 24h, 72h, 168h

## 🌈 Special Features

### Day/Night Cycle
- **Daytime (6am-8pm):** ☀️ Sun shines, ☁️ clouds drift
- **Nighttime (8pm-6am):** 🌙 Moon appears, ✦★✧⋆ stars twinkle
- **Sleep Time (10pm-6am):** Mochi sleeps peacefully

### Weather System
- **Clear:** Normal clouds ☁️
- **Rainy:** Rain clouds 🌧️ with water drops 💧
- **Snowy:** Snowflakes ❄️ falling
- Changes randomly every 2 minutes

### Milestones
- **1 Day Old (24h):** ★ Achievement notification
- **3 Days Old (72h):** ★ Achievement notification
- **1 Week Old (168h):** ★★ Special achievement!

## 💾 Save System

- Auto-saves every 10 seconds
- Save file: `~/.tamagotchi_save.json`
- Persists: hunger, health, weight, lifetime hours, milestones
- Age resets each session (fresh start)

## 🎨 Visual Styles

**Mochi's Emotions:**
```
Happy:    \o/        Hungry:   .-.
         (^.^)                (O.O)
          > <                  ~~~

Sick:     .-.        Sleeping:  .-.
         (;.;)                 (- -)
          ...                 z z z
```

**Weather:**
```
Clear:  ☁️  ☁️  ☁️
Rain:   🌧️  💧  🌧️
Snow:   ❄️  ❄️  ❄️
```

## 🌟 Tips

1. **Check often** - Hunger drops every 5 minutes!
2. **Clean regularly** - Poop buildup makes Mochi sick
3. **Keep well-fed** - Health regenerates when hunger >= 3 hearts
4. **Watch at night** - See Mochi sleep peacefully
5. **Catch weather** - Rain and snow are rare events!
6. **Reach milestones** - Keep Mochi alive to unlock achievements

## 🐛 Troubleshooting

**Mochi looks sick (;.;):**
- Feed if hungry
- Clean if there's poop
- Health will regenerate when well-cared-for

**No movement:**
- Mochi walks every 2 seconds
- Clouds drift every 3 seconds
- Just wait and watch!

**Old save data:**
```bash
rm ~/.tamagotchi_save.json
```

## 📊 Stats Explained

- **HUNGRY:** Feed meter - keep at ♥♥♥♥
- **HEALTH:** Regenerates when well-fed and clean
- **AGE:** Hours in current session (resets on restart)
- **WT:** Weight in kg (increases when fed)
- **Life:** Total lifetime hours (in parentheses)

## 🎯 Requirements

- Python 3.8+
- Textual library
- Terminal with emoji support
- Recommended: 80x24 minimum terminal size

## 🚀 Quick Start

```bash
./tamagotchi.py
```

That's it! Keep Mochi fed, clean, and happy! 🍡

## 📝 License

MIT - Made with ❤️ for virtual pet lovers

---

**Pro tip:** Run Mochi in a tmux/screen session so it keeps running even when you disconnect! Your pet will age in real-time.

```bash
tmux new -s mochi
./tamagotchi.py
# Detach: Ctrl+B, then D
# Reattach: tmux attach -s mochi
```

Enjoy your new digital companion! 🌟
