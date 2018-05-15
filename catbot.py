# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 20:43:38 2018
@author: Mei Eisenbach
"""

import os
import csv
from discord.ext import commands
import discord.utils
import string
import datetime

MSG_GYM_NOT_FOUND = '"{}" not found. Please check your spelling or use fewer words.'
MSG_TOO_MANY_RESULTS = 'Too many matches. Please be more specific.'
MSG_REPORT_MULTIPLE_MATCHES = 'More than one gym matches "{}"'
MSG_LEGENDARY_ROLE_MISSING = 'Legendary Raid role not found'

MSG_HELP = "!whereis [gym] will return a location pin for the gym.\n\
Examples:\n\
    !whereis Irvington Community Park\n\
    !whereis icp\n\
    !whereis irvington\n\
will all return\n\
Irvington Community Park (ICP) is here http://maps.google.com/maps?q=37.522771,-121.963727"

REPORT_CHANNEL_NAME = 'raid_alerts_only'
LEGENDARY_ROLE_NAME = 'LegendaryRaid'

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
        reponse = MSG_GYM_NOT_FOUND.format(name)
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
    msg = "{} at {}\n{}\nuntil {} ({} mins remaining)".format(boss.title(), gyms[gym]['name'], 
           link,
           until.strftime("%I:%M %p"), 
           time_left)
    return msg

def generate_egg_post(egg_level, until_hatch,  gym):
    hatch = datetime.datetime.now() + datetime.timedelta(minutes = int(until_hatch))
    link = create_link(gym)
    msg = "Level {} 🥚 at {}\n{}\nhatches at {} (in {} mins)".format(egg_level, gyms[gym]['name'], 
                 link,
                 hatch.strftime("%I:%M %p"), 
                 until_hatch)
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

'''
Bot code
'''
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    
    print('Report channel name: {}'.format(REPORT_CHANNEL_NAME))
    print('Legendary Role: {}'.format(LEGENDARY_ROLE_NAME))
    
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

@bot.command(pass_context=True)
async def raid(ctx, *, arg: str):
    report_channel = discord.utils.get(ctx.message.server.channels, name=REPORT_CHANNEL_NAME)
    if report_channel == None:
        print(REPORT_CHANNEL_NAME + ' channel not found')
        return
    
    legendary_role = discord.utils.get(ctx.message.server.roles, name=LEGENDARY_ROLE_NAME)
    if legendary_role == None:
        print(MSG_LEGENDARY_ROLE_MISSING)
    
    (boss, time_left, gym) = parse_report(arg)
    if boss.isnumeric():
        await bot.say('"{}" is not a raid boss.'.format(boss))
        return
    
    if not time_left.isnumeric():
        await bot.say('"{}" is not a number. Minutes remaining should be a number'.format(time_left))        
        return

    found = find_gyms(gym)
    if len(found) == 0:
        await bot.say(MSG_GYM_NOT_FOUND.format(gym))        
    elif len(found) == 1:
        reporter = ctx.message.author
        msg = generate_raid_post(boss, time_left, found[0])
        msg = '{}\nreported by {}'.format(msg, reporter.mention)
        if boss == 'latias':
            msg = '{} {}'.format(legendary_role.mention, msg)
        await bot.send_message(report_channel, content = msg)
        await bot.say('Raid reported to ' + report_channel.mention)
    else:
        await bot.say(MSG_REPORT_MULTIPLE_MATCHES.format(gym))


@bot.command(pass_context=True)
async def egg(ctx, *, arg: str):
    report_channel = discord.utils.get(ctx.message.server.channels, name=REPORT_CHANNEL_NAME)
    if report_channel == None:
        print(REPORT_CHANNEL_NAME + ' channel not found')
        return
        
    legendary_role = discord.utils.get(ctx.message.server.roles, name=LEGENDARY_ROLE_NAME)
    if legendary_role == None:
        print(MSG_LEGENDARY_ROLE_MISSING)

    (egg_level, until_hatch, gym) = parse_report(arg)
    if not egg_level.isnumeric():
        await bot.say('"{}" is not a number. Egg levels should be 1-5'.format(egg_level))        
        return
    if int(egg_level) < 1 or int(egg_level) > 5:
        await bot.say('"{}" is not valid. Egg levels should be 1-5'.format(egg_level))        
        return        
    
    if not until_hatch.isnumeric():
        await bot.say('"{}" is not a number. Minutes until hatch should be a number'.format(until_hatch))        
        return
    
    found = find_gyms(gym)
    if len(found) == 0:
        await bot.say(MSG_GYM_NOT_FOUND.format(gym))        
    elif len(found) == 1:
        reporter = ctx.message.author
        msg = generate_egg_post(egg_level, until_hatch, found[0])
        msg = '{}\nreported by {}'.format(msg, reporter.mention)
        if egg_level == '5':
            msg = '{} {}'.format(legendary_role.mention, msg)            
        await bot.send_message(report_channel, content = msg)
        await bot.say('Egg reported to '+ report_channel.mention)
    else:
        await bot.say(MSG_REPORT_MULTIPLE_MATCHES.format(gym))
    
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
