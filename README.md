# catbot
Discord bot for Pokemon Go users. It's written in Python 3.6 and uses the discord.py library.

## Installation
Requires discord.py v1.3.4 which can be found at https://discordpy.readthedocs.io/en/latest/intro.html#installing

Information on how to deploy your discord app can be found at https://discordapp.com/developers/docs/intro

The Catbot app expects the bot key to be stored in an environment variable named "DiscordKey".

## Usage
Catbot has the following commands:

- whereis - returns matching Pokemon Go gym locations when given a gym name
- egg - to report a Raid egg
- raid - to report a Raid

The gyms are read in from gyms.csv which has the following fields (at minimum):
- name: the name of the gym (must be unique)
- alias: an alias for the gym (can be blank but must be unique if present; you cannot have the same alias for two different gyms)
- latitude
- longitude

Name matching is case, space, and punctuation insensitive and will do partial matches. When searching for a gym, both the name and alias fields are searched.
