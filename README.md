# catbot
Discord bot for Pokemon Go users. It's written in Python 3.6 and uses the discord.py library.

Catbot has the following commands:

- whereis - returns matching Pokemon Go gym locations when given a gym name
- egg - to report a Raid egg
- raid - to report a Raid
- wild - to report a rare Pokemon 

The gyms are read in from gyms.csv which has the following fields (at minimum):
- name: the name of the gym (must be unique)
- alias: an alias for the gym (can be blank but must be unique if present; you cannot have the same alias for two different gyms)
- latitude
- longitude

Name matching is case, space, and punctuation insensitive and will do partial matches. When searching for a gym, both the name and alias fields are searched.

Criteria for rare Pokemon are read from rare_mons.csv.
