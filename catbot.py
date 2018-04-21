# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 20:43:38 2018
Modified 3/28/2018
@author: Mei Eisenbach
"""

import os
import csv
from discord.ext import commands
import datetime, string

MSG_GYM_NOT_FOUND = " not found. Please check your spelling or use fewer words."
MSG_TOO_MANY_RESULTS = 'Too many matches. Please be more specific.'
MSG_HELP = "!whereis [gym] will return a location pin for the gym.\n\
Examples:\n\
    !whereis Irvington Community Park\n\
    !whereis icp\n\
    !whereis irvington\n\
will all return\n\
Irvington Community Park (ICP) is here http://maps.google.com/maps?q=37.522771,-121.963727"

gyms = {}
aliases = {}

def process_name(name):
    new_name = name.lower()

    table = str.maketrans({key: None for key in string.punctuation})
    new_name = new_name.translate(table) 

    new_name = new_name.replace(' ', '')
    return new_name

def load_gyms():
    global gyms
    global aliases
    gyms = {}
    aliases = {}
    
    with open('fremont_gym_addresses.csv') as gymfile:
        gymreader = csv.DictReader(gymfile, delimiter=',', quotechar='"')
        for row in gymreader:
            namekey = process_name(row['name']) 
            gyms[namekey] = row
            if len(row['alias']) > 0:
                aliases[process_name(row['alias'])] = namekey

def search_names(name):
    global gyms
    found = []
    for namekey in gyms:
        if name in namekey:
            found.append(namekey)
    return found

def search_aliases(name):
    global aliases
    found = []

    for alias in aliases:
        if name in alias:
            found.append(aliases[alias])
    return found

def find_gyms(name):
    global gyms
    found = []
   
    new_name = process_name(name) 
    if new_name in gyms.keys():
        found = [new_name]
    else:
        found = search_names(new_name)
        if len(found) == 0:
            found = search_aliases(new_name)
            
    return found

def create_link(gym):
    LINK_BASE = 'http://maps.google.com/maps?q='
    return LINK_BASE + gyms[gym]['latitude'] + ',' + gyms[gym]['longitude'] 

def get_response(name):
    found = find_gyms(name)
    num_found = len(found)

    if num_found == 0:
        reponse = '"' + name + '"' + MSG_GYM_NOT_FOUND
        print(reponse)
    elif num_found <= 3:
        locations = []
        for gym in found:
            link = create_link(gym)
            locations.append(gyms[gym]['name'] + " is here " + link )
        reponse = '\n'.join(locations)
    else:
        reponse = MSG_TOO_MANY_RESULTS

    return reponse

'''
Functions for testing locally
'''    
def test_whereis(name):
    if name == 'help':
        response = MSG_HELP
    else:
        response = get_response(name)
    print(response)

def run_tests():
    test_whereis('Children Playing')
    test_whereis('icp')
    test_whereis('starbucks')
    test_whereis('st. edward')
    test_whereis('unknown gym')

'''
Bot code
'''
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)

@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message) and message.mention_everyone is False:
        if 'thanks' in message.content.lower():
            msg =  "{} You're welcome".format(message.author.mention)
            await bot.send_message(message.channel, content = msg)
    await bot.process_commands(message)
    
@bot.command(pass_context=True)
async def hello(ctx):
    await bot.say('Hello, {}'.format(ctx.message.author.mention))

@bot.command()
async def echo(*, arg: str):
    await bot.say(arg)

@bot.command()
async def whereis(*, arg: str):
    if arg == 'help':
        response = MSG_HELP
    else:
        response = get_response(arg)
    await bot.say(response)

@bot.command()
@commands.has_any_role('Mods', 'Developer')
async def reload_gyms():
    load_gyms()
    await bot.say('Gyms reloaded')

if __name__ == "__main__":
    load_gyms()
    key = os.getenv('DiscordKey')
    if key != None:
        bot.run(key)
    else:
        print('ERROR: Discord Key not found in the environment variables')
    print(datetime.datetime.now())
