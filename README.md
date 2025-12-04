# UC FT Twitter Bot

A Twitter bot that provides automated updates on the University of Cincinnati Bearcats' free throw shooting performance throughout the basketball season.

## Features

- 🏀 **Daily Updates**: Automatically tweets after each game with updated season stats
- 📊 **Smart Tracking**: Only tweets when there's new game data
- 🎯 **75% Goal**: Tracks consecutive makes needed to reach 75% season percentage
- 🎉 **Celebration Mode**: Special message formatting when UC shoots over 75% in a game
- 📈 **Historical Data**: Maintains CSV records of season progress

## How It Works

The bot runs daily at noon EST via GitHub Actions:

1. Scrapes current season stats from sports-reference.com
2. Compares with previous data stored in `data/season_stats_2026.csv`
3. If data changed (new game played):
   - Posts tweet with game and season stats
   - Updates CSV with new data
   - Creates and auto-merges PR to keep repo in sync

## Tweet Format

**Standard game:**
```
UC shot 17/26 (65.4%) from the charity stripe vs Georgia State on Nov 7.
The Bearcats are now 37/56 (66.1%) on the season and need 20 consecutive makes to reach 75%.
```

**When shooting over 75%:**
```
UC shot 11/14 (78.6%) from the charity stripe vs Eastern Michigan on Nov 26, great job guys!
But the Bearcats are still 113/174 (64.9%) on the season and need 70 consecutive makes to reach 75%.
```

## Setup

See [SETUP.md](SETUP.md) for detailed instructions on configuring GitHub Actions secrets and running the bot.

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with credentials
cp .env.example .env

# Run script
python main.py
```

## Files

- `main.py` - Main script that fetches data and posts tweets
- `data/season_stats_2026.csv` - Current season tracking data
- `catchup.md` - Archive of tweets from inactive period
- `.github/workflows/daily-tweet.yml` - Automated daily workflow

## Follow the Bot

[@UC_FreeThrowBot](https://twitter.com/UC_FreeThrowBot)