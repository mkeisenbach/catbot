#!/bin/bash

DISCORD_KEY_FILE=./discord_key.sh

PYTHON=python
RESTART_DELAY_S=10

if [[ ! -f "$DISCORD_KEY_FILE" ]];
then
   echo "Error: $DISCORD_KEY_FILE doesn't exist";
   exit 1;
else
   . $DISCORD_KEY_FILE
fi

if [[ -z "$DiscordKey" ]];
then
   echo "Error: 'DiscordKey' variable must be exported from $DISCORD_KEY_FILE";
   exit 2;
fi

while true;
do
   echo "[Re-]starting catbot ..."
   $PYTHON catbot.py
   sleep $RESTART_DELAY_S
done
