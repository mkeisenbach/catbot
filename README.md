# catbot
Discord bot for Pokemon Go users. It's written in Python 3.6 and uses the discord.py library.

Currently, catbot has only one main purpose - to return Pokemon Go gym locations when given the name of the gym.

The gyms are read in from a CSV file with the fields:
- name: the name of the gym (must be unique)
- alias: an alias for the gym (also must be unique; you cannot have the same alias for two different gyms)
- latitude
- longitude

Name matching is case, space, and punctuation insensitive and will do partial matches.

