#!/bin/bash

PYTHON=python
RESTART_DELAY_S=10

while true;
do
   echo "[Re-]starting catbot ..."
   $PYTHON catbot.py
   sleep $RESTART_DELAY_S
done
