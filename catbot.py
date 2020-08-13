# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 10:16:53 2018

Catbot 2.0 uses discord.py version 1.x

@author: Mei Eisenbach
"""

import os
import re
import datetime as dt
from discord import utils
from discord.ext import commands
from dateutil.parser import parse
from gyms import Gyms

gyms = None
gymfile = 'gyms.csv'
legendaries = []

# =============================================================================
# String constants
# =============================================================================
MSG_HELP = "!whereis [gym] will return a location pin for the gym.\n\
Examples:\n\
    !whereis Irvington Community Park\n\
    !whereis icp\n\
    !whereis irvington\n\
will all return\n\
Irvington Community Park (ICP) is here http://maps.google.com/maps?q=37.522771,-121.963727"

REPORT_CHANNEL_NAME = 'raid_alerts_only'
LEGENDARY_ROLE_NAME = 'LegendaryRaid'

ERR_GYM_NOT_FOUND = '"{}" not found. Please check your spelling or use fewer words.'
ERR_TOO_MANY_RESULTS = 'Too many matches. Please be more specific.'
ERR_REPORT_MULTIPLE_MATCHES = 'More than one gym matches "{}"'

ERR_LEGENDARY_ROLE_MISSING = 'Legendary Raid role not found'

ERR_RAID_NOT_FOUND = 'Raid not found'
ERR_INVALID_DATETIME = "Invalid date or time"
   
# =============================================================================
# Helper and test functions
# =============================================================================
def generate_post(is_egg, identifier, mins, gym, reporter):
    time = dt.datetime.now() + dt.timedelta(minutes = int(mins))
    link = gyms.get_link(gym)
    gym_name = gyms.get_name(gym)
    if gyms.is_ex(gym):
        gym_name = gym_name + ' 🎫'
    if is_egg:
        content = "Level {} 🥚 at {}\n{}\nhatches at {} (in {} mins)\nreported by {}"\
            .format(identifier,
                    gym_name, 
                    link,
                    time.strftime("%I:%M %p"), 
                    mins,
                    reporter)
    else:
        content = "{} at {}\n{}\nuntil {} ({} mins remaining)\nreported by {}"\
        .format(identifier.title(),
                gym_name, 
                link,
                time.strftime("%I:%M %p"), 
                mins,
                reporter)
    return content

def parse_args(arg_str):
    p = re.compile( r'^(.*) (at|in) (\S*) ?(\S*)? ?(\S*)?')
    m = p.match(arg_str)
    if m:
        return m.groups()
    else:
        return []

def format_do(gym, start, despawn, boss):
    link = gyms.get_link(gym)
    gym_name = gyms.get_name(gym)
    content = '-new "{}" {} {} {} {}'\
    .format(boss.title(),
            link,
            start.strftime("%I:%M%p"), 
            despawn.strftime("%I:%M%p"),
            gym_name)
    return content

def process_do(arg_str):    
    arguments = parse_args(arg_str)

    if len(arguments) == 0:
        return 'Usage: !do gym_name at/in start_time/min [despawn_time] [boss_name]'

    gym_name = arguments[0]

    # minutes given, calculate start time
    if arguments[1] == 'in':
        start = dt.datetime.now() + dt.timedelta(minutes = int(arguments[2]))
    else:        
        try:
            start = parse(arguments[2])
        except:
            return 'Invalid start time. Valid formats: 00:00 or 0:00pm'
            
    # assign rest of arguments            
    if arguments[3] == '':
        despawn = start + dt.timedelta(minutes=1)
        boss = "egg"
    elif arguments[4] == '':
        despawn = start + dt.timedelta(minutes=1)
        boss = arguments[3]
    else:
        try:
            despawn = parse(arguments[3])
        except:
            return 'Invalid despawn time. Valid formats: 00:00 or 0:00pm'
        boss = arguments[4]
    
    found = gyms.find(gym_name)
    if len(found) == 0:
        content = ERR_GYM_NOT_FOUND.format(gym_name)
    elif len(found) == 1:
        content = format_do(found[0], start, despawn, boss)
    else:
        content = ERR_REPORT_MULTIPLE_MATCHES.format(gym_name)

    return content


# =============================================================================
# Test functions
# =============================================================================
def test_whereis(name):
    found = gyms.find(name)
    num_found = len(found)

    if num_found == 0:
        content = ERR_GYM_NOT_FOUND.format(name)
    elif num_found <= 3:
        locations = []
        for gym in found:
            link = gyms.get_link(gym)
            locations.append(gyms.get_name(gym) + " is here " + link )
        content = '\n'.join(locations)
    print(content)

def test_do():
    # absolute start time
    assert process_do('Rings Arch at 8:30pm 9:15pm Kyurem') ==\
        '-new "Kyurem" http://maps.google.com/maps?q=37.584377,-122.068447 08:30PM 09:15PM Rings Arch'
    assert process_do('Rings Arch at 20:30 Kyurem') ==\
        '-new "Kyurem" http://maps.google.com/maps?q=37.584377,-122.068447 08:30PM 08:31PM Rings Arch'
    assert process_do('Rings Arch at 8:30pm') ==\
        '-new "Egg" http://maps.google.com/maps?q=37.584377,-122.068447 08:30PM 08:31PM Rings Arch'

    # errors
    assert process_do('Rings Arch 8:30pm 9:15pm Kyurem') ==\
        'Usage: !do gym_name at/in start_time/min [despawn_time] [boss_name]'
    assert process_do('Ring Arch at 8:30pm 9:15pm Kyurem') ==\
        '"Ring Arch" not found. Please check your spelling or use fewer words.'
    assert process_do('Rings Arch at 20:30pm 9:15pm Kyurem') ==\
        'Invalid start time. Valid formats: 00:00 or 0:00pm'
    assert process_do('Rings Arch at 8:30pm 21:15pm Kyurem') ==\
        'Invalid despawn time. Valid formats: 00:00 or 0:00pm'
    print('All asserts passed.')
    
    # relative start time
    print('Check output from relative times...')
    print(process_do('Rings Arch in 30 9:15pm Kyurem'))
    print(process_do('Rings Arch in 30 Kyurem'))
    print(process_do('Rings Arch in 30'))
    

# =============================================================================
# Bot code
# =============================================================================
bot_prefix = '!'
bot = commands.Bot(command_prefix=bot_prefix)

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    print('Bot Prefix: ', bot_prefix)

@bot.event
async def on_message(message):
    content = ''
    if bot.user.mentioned_in(message) and message.mention_everyone is False:
        message_lowered = message.content.lower()
        if 'hello' in message_lowered or 'hi' in message_lowered:
            content = 'Hello, {}'.format(message.author.mention)
        elif 'thanks' in message_lowered:
            content =  "{} You're welcome".format(message.author.mention)
        elif 'coming' in message_lowered or 'going' in message_lowered:
            content = "{} Sorry, I'm a bot and stuck in this server room.".format(message.author.mention)    
        await message.channel.send(content)

    await bot.process_commands(message)


@bot.command()
async def whereis(ctx, *args):
    name = ' '.join(args)

    found = gyms.find(name)
    num_found = len(found)

    if num_found == 0:
        content = ERR_GYM_NOT_FOUND.format(name)
    elif num_found <= 3:
        locations = []
        for gym in found:
            link = gyms.get_link(gym)
            locations.append(gyms.get_name(gym) + " is here " + link )
        content = '\n'.join(locations)
    else:
        content = ERR_TOO_MANY_RESULTS

    await ctx.send(content)


@bot.command()
async def egg(ctx, egg_level, until_hatch, *args):
    report_channel = utils.get(ctx.guild.channels, name=REPORT_CHANNEL_NAME)
    if report_channel == None:
        print(REPORT_CHANNEL_NAME + ' channel not found')
        return

    legendary_role = utils.get(ctx.guild.roles, name=LEGENDARY_ROLE_NAME)
    if legendary_role == None:
        await ctx.send(ERR_LEGENDARY_ROLE_MISSING)
        return

    if not egg_level.isnumeric():
        await ctx.send('"{}" is not a number. Egg levels should be 1-5'.format(egg_level))        
        return
    if int(egg_level) < 1 or int(egg_level) > 5:
        await ctx.send('"{}" is not valid. Egg levels should be 1-5'.format(egg_level))        
        return        
    
    if not until_hatch.isnumeric():
        await ctx.send('"{}" is not a number. Minutes until hatch should be a number'.format(until_hatch))        
        return
            
    gym = ' '.join(args)
    found = gyms.find(gym)
    if len(found) == 0:
        await ctx.send(ERR_GYM_NOT_FOUND.format(gym))        
    elif len(found) == 1:
        reporter = ctx.message.author.mention
        content = generate_post(True, egg_level, until_hatch, found[0], reporter)

        if egg_level == '5':
            content = '{} {}'.format(legendary_role.mention, content)            

        await report_channel.send(content)
        await ctx.send('Egg reported to '+ report_channel.mention)
    else:
        await ctx.send(ERR_REPORT_MULTIPLE_MATCHES.format(gym))


@bot.command()
async def raid(ctx, boss, time_left, *args):    
    mention = ['shinx']
    report_channel = utils.get(ctx.guild.channels, name=REPORT_CHANNEL_NAME)
    if report_channel == None:
        await ctx.send(REPORT_CHANNEL_NAME + ' channel not found')
        return

    legendary_role = utils.get(ctx.guild.roles, name=LEGENDARY_ROLE_NAME)
    if legendary_role == None:
        await ctx.send(ERR_LEGENDARY_ROLE_MISSING)
        return
        
    if boss.isnumeric():
        await ctx.send('"{}" is not a raid boss.'.format(boss))
        return
    
    if not time_left.isnumeric():
        await ctx.send('"{}" is not a number. Minutes remaining should be a number'.format(time_left))        
        return

    if boss.lower() in mention:
        boss_role = utils.get(ctx.guild.roles, name=boss)
        if boss_role != None:
            boss = boss_role

    gym = ' '.join(args)
    found = gyms.find(gym)
    if len(found) == 0:
        await ctx.send(ERR_GYM_NOT_FOUND.format(gym))        
    elif len(found) == 1:
        reporter = ctx.message.author.mention
        content = generate_post(False, boss, time_left, found[0], reporter)

        if boss in legendaries:
            content = '{} {}'.format(legendary_role.mention, content)

        await report_channel.send(content)
        await ctx.send('Raid reported to '+ report_channel.mention)
    else:
        await ctx.send(ERR_REPORT_MULTIPLE_MATCHES.format(gym))


@bot.command()
@commands.has_any_role('Developer')
async def set_legendaries(ctx, *args):
    global legendaries
    if len(args) > 0:
        legendaries = list(map(str.lower, args))
    await ctx.message.add_reaction('👍')

@bot.command()
@commands.has_any_role('Developer')
async def get_legendaries(ctx, *args):
    global legendaries
    msg = ', '.join([el.title() for el in legendaries])
    if msg == '':
        msg = 'No legendaries set.'
    await ctx.send(msg)

@bot.command()
@commands.has_any_role('Mods', 'Developer')
async def reload_gyms(ctx):
    gyms.read_csv(gymfile)
    await ctx.message.add_reaction('👍')

# Eventually add: 'Pin', 'UC Agent', 'FMT Agent', 'SF Agent', 'HWD Agent'
@commands.has_any_role('Developer', 'TR Scientist')
@bot.command()
async def do(ctx, *args):
    message = process_do(' '.join(args))
    await ctx.send(message)

@commands.has_any_role('TR Scientist')
@bot.command()
async def purge(ctx, limit=10, matches):
    def check_msg(msg):
        if matches is not None:
            pat = r'\d{4}\s*\d{4}\s*\d{4}\s*'
            if re.search(pat, msg.content) is None:            
                return False
        return True
    
    deleted = await ctx.channel.purge(limit=limit, check=check_msg)
    msg = await ctx.send('Deleted {} message(s)'.format(len(deleted))
    
# =============================================================================
# Main
# =============================================================================

try:
    gyms = Gyms(gymfile)
    print('Gyms loaded')    
except IOError:
    print('ERROR: Unable to load gyms from', gymfile)
    exit()

if __name__ == "__main__":    
    key = os.getenv('DiscordKey')
    if key == None:
        print('ERROR: Discord Key not found in the environment variables')
        exit()
    bot.run(key)
