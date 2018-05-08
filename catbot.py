# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 20:43:38 2018
@author: Mei Eisenbach
"""

import os
import csv
#import discord
from discord.ext import commands
import string
import datetime

MSG_GYM_NOT_FOUND = " not found. Please check your spelling or use fewer words."
MSG_TOO_MANY_RESULTS = 'Too many matches. Please be more specific.'
MSG_HELP = "!whereis [gym] will return a location pin for the gym.\n\
Examples:\n\
    !whereis Irvington Community Park\n\
    !whereis icp\n\
    !whereis irvington\n\
will all return\n\
Irvington Community Park (ICP) is here http://maps.google.com/maps?q=37.522771,-121.963727"

TARGET_CHANNEL_ID = '328216542095474700'
TARGET_CHANNEL_NAME = 'raid_alerts_only'

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
    
    try:
        with open('gyms.csv') as gymfile:
            gymreader = csv.DictReader(gymfile, delimiter=',', quotechar='"')
            for row in gymreader:
                namekey = process_name(row['name']) 
                gyms[namekey] = row
                if len(row['alias']) > 0:
                    aliases[process_name(row['alias'])] = namekey
            return True
    except:
        return False

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

def parse_report(arg):
    arg = arg.lower()
    arg = arg.replace('  ', ' ')
    return arg.split(' ', 2)

def generate_raid_post(boss, time_left, gym):
    until = datetime.datetime.now() + datetime.timedelta(minutes = int(time_left))
    link = create_link(gym)
    msg = "{} at {}\nuntil {} ({} mins remaining) \n{}".format(boss.title(), \
           gyms[gym]['name'], until.strftime("%I:%M %p"), time_left, link)
    return msg

def generate_egg_post(egg_level, until_hatch,  gym):
    hatch = datetime.datetime.now() + datetime.timedelta(minutes = int(until_hatch))
    link = create_link(gym)
    msg = "Level {} 🥚 at {}\nhatches at {} (in {} mins)\n{}".format(egg_level, \
                 gyms[gym]['name'], hatch.strftime("%I:%M %p"), until_hatch, link)
    return msg

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

def test_egg(arg):
    (egg_level, until_hatch, gym) = parse_report(arg)
    if not egg_level.isnumeric():
        print('{} is not a number'.format(egg_level))
        return
    if not until_hatch.isnumeric():
        print('{} is not a number'.format(until_hatch))
        return
    
    found = find_gyms(gym)
    if len(found) == 0:
        print('Gym not found')        
    elif len(found) == 1:
        msg = generate_egg_post(egg_level, until_hatch, found[0])
        print(msg)
    else:
        print('More than one gym matches the reported gym')


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
    msg = ''
    if bot.user.mentioned_in(message) and message.mention_everyone is False:
        message_lowered = message.content.lower()
        if 'hello' in message_lowered or 'hi' in message_lowered:
            msg = 'Hello, {}'.format(message.author.mention)
        elif 'thanks' in message_lowered:
            msg =  "{} You're welcome".format(message.author.mention)
        elif 'coming' in message_lowered or 'going' in message_lowered:
            msg = "{} Sorry, I'm a bot and stuck in this server room.".format(message.author.mention)    
        await bot.send_message(message.channel, content = msg)
    await bot.process_commands(message)
    
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

ROLE_LEGENDARY = '341323216012181504'

@bot.command()
async def test_raid(*, arg: str):
    TARGET_CHANNEL_ID = '340536001766227968'
    
    (boss, time_left, gym) = parse_report(arg)
    if not time_left.isnumeric():
        await bot.say('{} is not a number'.format(time_left))        
        return

    found = find_gyms(gym)
    if len(found) == 0:
        await bot.say('Gym not found')        
    elif len(found) == 1:
        msg = generate_raid_post(boss, time_left, found[0])
        if boss == 'latios' or boss == 'latias':
            msg = '{}\n<@& {}>'.format(msg, ROLE_LEGENDARY)
        await bot.send_message(bot.get_channel(TARGET_CHANNEL_ID), content = msg)
        await bot.say('Raid reported to #code_testing')
    else:
        await bot.say('More than one gym matches the reported gym')

@bot.command()
async def raid(*, arg: str):
    (boss, time_left, gym) = parse_report(arg)
    if not time_left.isnumeric():
        await bot.say('{} is not a number'.format(time_left))        
        return

    found = find_gyms(gym)
    if len(found) == 0:
        await bot.say('Gym not found')        
    elif len(found) == 1:
        msg = generate_raid_post(boss, time_left, found[0])
        if boss == 'latios' or boss == 'latias':
            msg = '{}\n<@&{}>'.format(msg, ROLE_LEGENDARY)
        await bot.send_message(bot.get_channel(TARGET_CHANNEL_ID), content = msg)
        await bot.say('Raid reported to #' + TARGET_CHANNEL_NAME)
    else:
        await bot.say('More than one gym matches the reported gym')

@bot.command()
async def egg(*, arg: str):        
    (egg_level, until_hatch, gym) = parse_report(arg)
#    if not egg_level.isnumeric():
#        await bot.say('{} is not a number'.format(egg_level))        
#        return
    if not until_hatch.isnumeric():
        await bot.say('{} is not a number'.format(until_hatch))        
        return
    
    found = find_gyms(gym)
    if len(found) == 0:
        print('Gym not found')        
    elif len(found) == 1:
        msg = generate_egg_post(egg_level, until_hatch, found[0])
        if egg_level == '5':
            msg = '{}\n<@&{}>'.format(msg, ROLE_LEGENDARY)            
        await bot.send_message(bot.get_channel(TARGET_CHANNEL_ID), content = msg)
        await bot.say('Egg reported to #' + TARGET_CHANNEL_NAME)
    else:
        await bot.say('More than one gym matches the reported gym')

'''
Main
'''
if __name__ == "__main__":
    if load_gyms():
        key = os.getenv('DiscordKey')
        if key != None:
            bot.run(key)
        else:
            print('ERROR: Discord Key not found in the environment variables')
    else:
        print('ERROR: Unable to load gyms')
