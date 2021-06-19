# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 10:16:53 2018

Catbot 2.0 uses discord.py version 1.x

@author: Mei Eisenbach
"""

import sys
import os
import re
import datetime as dt
import dotenv
import pickle
from discord import utils
from discord import Embed
from discord.ext import commands
from dateutil.parser import parse
from gyms import Gyms
from pokemon import Pokemon
from catbot_log import CatbotLog
from discord.ext.commands import CommandNotFound
import traceback

BOT_PREFIX = '!'
GYMFILE = 'gyms.csv'
POKEMONFILE = 'pokedex.csv'
PARAMSFILE = 'params.pickle'
HOST_LOGFILE = 'host.log'
ERROR_LOGFILE = 'error.log'
EGG_URL_BASE = 'https://ironcreek.net/catbot/eggs/'
EGG1 = 'egg1.png'
EGG3 = 'egg3.png'
EGG_LEGENDARY = 'legendary_egg.png'
EGG_MEGA = 'mega_egg.png'

gyms = None
pokemon = None
params = {}
params['legendaries'] = []

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
    time = dt.datetime.now() + dt.timedelta(minutes=int(mins))
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
    p = re.compile(r'^(.*) (at|in) (\S*) ?(\S*)? ?(\S*)?')
    m = p.match(arg_str)
    if m:
        return m.groups()
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
        start = dt.datetime.now() + dt.timedelta(minutes=int(arguments[2]))
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


def parse_host_args(args: list):
    args = ' '.join(args)
    args = re.sub(r'[\[\](){}]', '', args)

    p = r'(.+) (hatch|end|start)\D*(\d+) ?(?:min)?(?:s|utes?)? ?(.*)'
    m = re.match(p, args, re.IGNORECASE)
    if m:
        return {'boss': m.groups()[0], 'verb': m.groups()[1],
                'mins': m.groups()[2], 'notes': m.groups()[3]}
    return {}


def parse_host_now(args: list):
    args = ' '.join(args)

    p = r'(.+) (start|hatch)\w* ?(now) ?(.*)'
    m = re.match(p, args, re.IGNORECASE)
    if m:
        return {'boss': m.groups()[0], 'verb': m.groups()[1],
                'mins': '0', 'notes': m.groups()[3]}
    return {}


def parse_host_mins_left(args: list):
    args = ' '.join(args)

    p = r'(.+) (\d+) ?(?:min)?(?:s|utes?)? ?(left) ?(.*)'
    m = re.match(p, args, re.IGNORECASE)
    if m:
        return {'boss': m.groups()[0], 'mins': m.groups()[1],
                'verb': 'end', 'notes': m.groups()[3]}

    return {}


def censor_notes(notes):
    friendcode_pat = re.compile(r'\d{4}[-\s]*\d{4}[-\s]*\d{4}')
    notes = friendcode_pat.sub('<Friend code removed>', notes)

    dm_me_pat = re.compile(r'[dp]\W*m(\s+|$)(me)?', re.IGNORECASE)
    notes = dm_me_pat.sub('...', notes)

    dm_me_pat2 = re.compile(r'(direct\s*)?me?ss?a?ge?(\s*|$)(me)?',
                            re.IGNORECASE)
    notes = dm_me_pat2.sub('...', notes)

    dm_me_pat3 = re.compile(r'te?xt me', re.IGNORECASE)
    notes = dm_me_pat3.sub('...', notes)

    return notes


def get_egg_url(level):
    if level <= 2:
        thumbnail = 'egg1.png'
    elif level <= 4:
        thumbnail = 'egg3.png'
    elif level == 5:
        thumbnail = 'legendary_egg.png'
    else:
        thumbnail = 'mega_egg.png'
    return EGG_URL_BASE+thumbnail


def save_params(paramsfile, params):
    with open(paramsfile, 'wb') as f:
        pickle.dump(params, f)


def load_params(paramsfile):
    with open(paramsfile, 'rb') as f:
        params = pickle.load(f)
    return params

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
            locations.append(gyms.get_name(gym) + " is here " + link)
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
bot = commands.Bot(command_prefix=BOT_PREFIX)


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    print('Bot Prefix: ', BOT_PREFIX)


@bot.event
async def on_message(message):
    content = ''
    if bot.user.mentioned_in(message) and message.mention_everyone is False:
        message_lowered = message.content.lower()
        if 'hello' in message_lowered or 'hi' in message_lowered:
            content = 'Hello, {}'.format(message.author.mention)
        elif 'thanks' in message_lowered:
            content = "{} You're welcome".format(message.author.mention)
        elif 'coming' in message_lowered or 'going' in message_lowered:
            content = "{} Sorry, I'm a bot and stuck in this server room."\
                .format(message.author.mention)
        await message.channel.send(content)

    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, exception):
    if isinstance(exception, CommandNotFound):
        log = open(ERROR_LOGFILE, 'a')
        log.write('{}, {}\n'.format(exception, ctx.guild))
        log.close()
        return

    print('Ignoring exception in command {}:'.format(ctx.command),
          file=sys.stderr)
    traceback.print_exception(type(exception), exception,
                              exception.__traceback__, file=sys.stderr)


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
            locations.append(gyms.get_name(gym) + " is here " + link)
        content = '\n'.join(locations)
    else:
        content = ERR_TOO_MANY_RESULTS

    await ctx.send(content)


def parse_egg(args: list):
    args = ' '.join(args)
    args = re.sub(r'[\[\](){}]', '', args)

    p = r't?([1-6]) hatches in (\d+) at (.*)'
    m = re.match(p, args, re.IGNORECASE)
    if m:
        return {'egg': m.groups()[0], 'mins': m.groups()[1],
                'gym': m.groups()[2]}
    return {}


def parse_egg_old(args: list):
    args = ' '.join(args)
    p = r'([1-6]) (\d+) (.*)'
    m = re.match(p, args, re.IGNORECASE)
    if m:
        return {'egg': m.groups()[0], 'mins': m.groups()[1],
                'gym': m.groups()[2]}
    return {}

@bot.command()
async def egg_new(ctx, *args):
    if ctx.guild is None:
        await ctx.send('This command can only be used on a server.')
        return

    report_channel = utils.get(ctx.guild.channels, name=REPORT_CHANNEL_NAME)
    if report_channel is None:
        await ctx.send(REPORT_CHANNEL_NAME + ' channel not found')
        return

    parsed = parse_egg(args)
    if not parsed:
        parsed = parse_egg_old(args)

    if not parsed:
        content = 'Usage: !egg [1-6] hatches in [mins] at [gym] \nExample: !egg 5 hatches in 10 at ICP'
        await ctx.send(content)
        return

    thumbnail = get_thumbnail(parsed['egg'])

    found = gyms.find(parsed['gym'])
    if len(found) == 0:
        await ctx.send(ERR_GYM_NOT_FOUND.format(parsed['gym']))
        return
    elif len(found) == 1:
        time = dt.datetime.now() + dt.timedelta(minutes=int(parsed['mins']))
        when = 'hatches at {} (in {} mins)'.format(time.strftime("%I:%M %p"),
                                                   parsed['mins'])
        if parsed['egg'] == 6:
            title = 'Mega Raid'
        else:
            title = 'Tier '+parsed['egg']
        embed = create_egg_raid_embed(title, ctx.author.mention,
                                      when, found[0], thumbnail)

        msg = await report_channel.send(embed=embed)
        await msg.add_reaction('👍')
        await ctx.send('Egg reported to ' + report_channel.mention)
    else:
        await ctx.send(ERR_REPORT_MULTIPLE_MATCHES.format(parsed['gym']))


@bot.command()
async def egg(ctx, egg_level, until_hatch, *args):
    report_channel = utils.get(ctx.guild.channels, name=REPORT_CHANNEL_NAME)
    if report_channel is None:
        print(REPORT_CHANNEL_NAME + ' channel not found')
        return

    legendary_role = utils.get(ctx.guild.roles, name=LEGENDARY_ROLE_NAME)
    if legendary_role is None:
        await ctx.send(ERR_LEGENDARY_ROLE_MISSING)
        return

    mega_role = utils.get(ctx.guild.roles, name='MegaRaid')

    if not egg_level.isnumeric():
        await ctx.send('"{}" is not a number. Egg levels should be 1-6'.format(egg_level))
        return
    if int(egg_level) < 1 or int(egg_level) > 6:
        await ctx.send('"{}" is not valid. Egg levels should be 1-6'.format(egg_level))
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
        content = generate_post(
            True, egg_level, until_hatch, found[0], reporter)

        if egg_level == '5':
            content = '{} {}'.format(legendary_role.mention, content)

        if egg_level == '6' and mega_role is not None:
            content = '{} {}'.format(mega_role.mention, content)

        await report_channel.send(content)
        await ctx.send('Egg reported to ' + report_channel.mention)
    else:
        await ctx.send(ERR_REPORT_MULTIPLE_MATCHES.format(gym))


def parse_raid(args: list):
    args = ' '.join(args)
    args = re.sub(r'[\[\](){}]', '', args)

    p = r'([\w\s]+) (ends|despawns) in (\d+) at (.*)'
    m = re.match(p, args, re.IGNORECASE)
    if m:
        return {'boss': m.groups()[0], 'mins': m.groups()[2],
                'gym': m.groups()[3]}
    return {}


def parse_raid_old(args: list):
    args = ' '.join(args)
    p = r'(.*) (\d+) (.*)'
    m = re.match(p, args, re.IGNORECASE)
    if m:
        return {'boss': m.groups()[0], 'mins': m.groups()[1],
                'gym': m.groups()[2]}
    return {}


def create_egg_raid_embed(title, reporter, when, gym, thumbnail=''):
    embed = Embed(title=title.title(),
                  description='React with thumbs up if interested')
    embed.add_field(name="Where", value=gyms.get_name(gym))
    embed.add_field(name="When",
                    value=when)
    embed.add_field(name="Reported by", value=reporter)
    embed.add_field(name="Location", value=gyms.get_link(gym))

    if thumbnail != '':
        embed.set_thumbnail(url=thumbnail)

    return embed


@bot.command()
async def raid_new(ctx, *args):
    if ctx.guild is None:
        await ctx.send('This command can only be used on a server.')
        return

    report_channel = utils.get(ctx.guild.channels, name=REPORT_CHANNEL_NAME)
    if report_channel is None:
        await ctx.send(REPORT_CHANNEL_NAME + ' channel not found')
        return

    parsed = parse_raid(args)
    if not parsed:
        parsed = parse_raid_old(args)

    if not parsed:
        content = 'Usage: !raid [boss] ends in [mins] at [gym] \nExample: !raid Regirock ends in 30 at ICP'
        await ctx.send(content)
        return

    found = pokemon.find(parsed["boss"])
    if found != '' and found != parsed["boss"].lower():
        parsed["boss"] = found

    thumbnail = get_thumbnail(parsed['boss'])

    found = gyms.find(parsed['gym'])
    if len(found) == 0:
        await ctx.send(ERR_GYM_NOT_FOUND.format(parsed['gym']))
        return
    elif len(found) == 1:
        time = dt.datetime.now() + dt.timedelta(minutes=int(parsed['mins']))
        when = 'despawns at {} (in {} mins)'.format(time.strftime("%I:%M %p"),
                                           parsed['mins'])
        embed = create_egg_raid_embed(parsed['boss'], ctx.author.mention,
                                      when, found[0], thumbnail)

        msg = await report_channel.send(embed=embed)
        await msg.add_reaction('👍')
        await ctx.send('Raid reported to ' + report_channel.mention)
    else:
        await ctx.send(ERR_REPORT_MULTIPLE_MATCHES.format(parsed['gym']))


@bot.command()
async def raid(ctx, boss, time_left, *args):
    mention = ['shinx']
    report_channel = utils.get(ctx.guild.channels, name=REPORT_CHANNEL_NAME)
    if report_channel is None:
        await ctx.send(REPORT_CHANNEL_NAME + ' channel not found')
        return

    legendary_role = utils.get(ctx.guild.roles, name=LEGENDARY_ROLE_NAME)
    if legendary_role is None:
        await ctx.send(ERR_LEGENDARY_ROLE_MISSING)
        return

    if boss.isnumeric():
        await ctx.send('"{}" is not a raid boss.'.format(boss))
        return

    if not time_left.isnumeric():
        await ctx.send('"{}" is not a number. \
                       Minutes remaining should be a number'.format(time_left))
        return

    if boss.lower() in mention:
        boss_role = utils.get(ctx.guild.roles, name=boss)
        if boss_role is not None:
            boss = boss_role

    gym = ' '.join(args)
    found = gyms.find(gym)
    if len(found) == 0:
        await ctx.send(ERR_GYM_NOT_FOUND.format(gym))
    elif len(found) == 1:
        reporter = ctx.message.author.mention
        content = generate_post(False, boss, time_left, found[0], reporter)

        if is_legendary(boss):
            content = '{} {}'.format(legendary_role.mention, content)

        await report_channel.send(content)
        await ctx.send('Raid reported to ' + report_channel.mention)
    else:
        await ctx.send(ERR_REPORT_MULTIPLE_MATCHES.format(gym))


@bot.command()
@commands.has_any_role('Developer', 'Admin', 'mod')
async def set_legendaries(ctx, *args):
    if len(args) == 0:
        await ctx.send('Usage: !set_legendaries leg1 leg2 ...')
        return

    params['legendaries'] = list(map(str.lower, args))
    await ctx.message.add_reaction('👍')
    save_params(PARAMSFILE, params)


@bot.command()
@commands.has_any_role('Developer', 'Admin', 'mod')
async def get_legendaries(ctx):
    legendaries = params.get('legendaries', [])
    msg = ', '.join([el.title() for el in legendaries])
    if msg == '':
        msg = 'No legendaries set.'
    await ctx.send(msg)


@bot.command()
@commands.has_any_role('Developer')
async def reload_gyms(ctx):
    gyms.read_csv(GYMFILE)
    await ctx.message.add_reaction('👍')


@bot.command()
@commands.has_any_role('Developer')
async def reload_pokemon(ctx):
    pokemon.read_csv(POKEMONFILE)
    await ctx.message.add_reaction('👍')


@bot.command(pass_context=True)
async def get_invite(ctx):
    if ctx.message.guild is None:
        msg = 'Please use this command from a server channel.'
        await ctx.message.author.send(msg)
        return

    if ctx.message.guild.name == "(Official) Pokémon GO: Fremont":
        link = await ctx.channel.create_invite(
            max_age=3600*24, max_use=1, unique=True)
        if link is not None:
            await ctx.message.author.send(
                'Here is your invite {}'.format(link))
            await ctx.send('Invite sent via dm')
        else:
            await ctx.send('Unable to create invite')
    else:
        await ctx.send('Sorry, this command is not allowed on this server.')


# Eventually add: 'Pin', 'UC Agent', 'FMT Agent', 'SF Agent', 'HWD Agent'
@commands.has_any_role('Developer', 'TR Scientist')
@bot.command()
async def do(ctx, *args):
    message = process_do(' '.join(args))
    await ctx.send(message)


@commands.has_any_role('TR Scientist', 'Admin', 'mod')
@bot.command()
async def purge_fc(ctx, limit=None):
    def check_msg(msg):
        if msg.pinned:
            return False
        if msg.id == ctx.message.id:
            return True
        if re.search(r'(^|\D)\d{4}[-\s]*\d{4}[-\s]*\d{4}($|\D)', msg.content)\
                is None:
            return False
        return True

    # limit is the number of messages to search through
    if limit is not None:
        limit = int(limit)
    deleted = await ctx.channel.purge(limit=limit, check=check_msg)

    # debug
    for msg in deleted:
        print(msg.content)

    await ctx.send('Deleted {} message(s)'.format(len(deleted)-1),
                   delete_after=5)


def get_reporting_channels(ctx):
    channel_names = {'mega': 'active-mega-raids',
                     'legendary': 'active-t5-raids',
                     'other': 'active-t1-t3-raids'}

    reporting_channels = {}

    if ctx.guild is not None:
        for key, name in channel_names.items():
            reporting_channels[key] = utils.get(ctx.guild.channels, name=name)

    return reporting_channels


def is_mega(boss):
    if re.search(r'mega(\s|$)', boss, re.IGNORECASE) is None:
        return False
    return True


def is_legendary(boss):
    if 'legendaries' in params and boss.lower() in params['legendaries']:
        return True
    return False


def get_thumbnail(boss):
    thumbnail = ''

    m = re.match('t?([123456])', boss, re.IGNORECASE)
    if m is not None:
        thumbnail = get_egg_url(int(m.groups()[0]))
        return thumbnail

    thumbnail = pokemon.get_boss_url(boss)
    if thumbnail != '':
        return thumbnail

    if is_mega(boss):
        thumbnail = EGG_URL_BASE + EGG_MEGA

    return thumbnail


def create_embed(title, host, when, notes='', thumbnail=''):
    embed = Embed(title=title.title(),
                  description='React with team emoji for invite')
    embed.add_field(name="Host", value=host)
    embed.add_field(name="When", value=when)

    if notes != '':
        embed.add_field(name="Notes", value=notes)

    if thumbnail != '':
        embed.set_thumbnail(url=thumbnail)

    return embed


def get_raid_tier(boss):
    if is_mega(boss):
        return 'mega'

    if is_legendary(boss) or\
            re.match('t5', boss, re.IGNORECASE) is not None:
        return 'legendary'

    return 'other'


@bot.command(aliases=["Host"])
async def host(ctx, *args):
    if ctx.guild is None:
        CatbotLog.write('Error', 'Host command sent via DM')
        await ctx.send('This command can only be used on a server.')
        return

    if ctx.channel.name != '💥-hosting-commands':
        await ctx.send('This command can only be used from #💥-hosting-commands.')
        return

    reporting_channels = get_reporting_channels(ctx)

    for key, channel in reporting_channels.items():
        if channel is None:
            await ctx.send('Reporting channels not found')
            return

    parsed = parse_host_now(args)
    if not parsed:
        parsed = parse_host_args(args)
    if not parsed:
        parsed = parse_host_mins_left(args)

    if not parsed:
        content = \
        'Usage: !host [T1-5 or boss] [hatches|starts|ends] in mins (optional notes)\nExample: !host heatran ends in 30 mins'
        await ctx.send(content)

        CatbotLog.write('Parse Error', 'host ' + ' '.join(args), ctx.guild)
        return

    when = '{}ing in {} mins'.format(parsed["verb"], parsed["mins"])

    if parsed["notes"] != '':
        parsed["notes"] = censor_notes(parsed["notes"])

    found = pokemon.find(parsed["boss"])
    if found != '' and found != parsed["boss"].lower():
        CatbotLog.write('Correction', '{} to {}'.format(parsed["boss"], found),
                        ctx.guild)
        parsed["boss"] = found

    thumbnail = get_thumbnail(parsed['boss'])

    embed = create_embed(parsed['boss'], ctx.author, when, parsed['notes'],
                         thumbnail)

    tier = get_raid_tier(parsed['boss'])

    msg = await reporting_channels[tier].send(embed=embed,
                                              delete_after=2*60*60)

    CatbotLog.write('Success', 'host ' + ' '.join(args), ctx.guild)

    for team_logo in ['instinctlogo', 'mysticlogo', 'valorlogo']:
        emoji = utils.get(ctx.guild.emojis, name=team_logo)
        if emoji is not None:
            await msg.add_reaction(emoji)

    await ctx.send('Raid reported to ' + reporting_channels[tier].mention,
                   delete_after=5)

    await ctx.message.delete()


def is_n_minutes_old(timestamp, minutes):
    return (dt.datetime.utcnow() - timestamp) > dt.timedelta(minutes=minutes)


@commands.has_any_role('TR Scientist', 'Admin', 'mod', 'Mod')
@bot.command(aliases=["purge_old"])
async def purge_old_messages(ctx, age_in_minutes=2*60):
    deleted = await ctx.channel.purge(limit=100,
                                      check=lambda m: is_n_minutes_old(m.created_at,
                                                                       age_in_minutes)
                                      and not m.pinned)
    await ctx.send('Deleted {} message(s)'.format(len(deleted)),
                   delete_after=10)
    await ctx.message.delete()


@commands.has_any_role('TR Scientist', 'Developer')
@bot.command()
async def shutdown(ctx):
    await bot.logout()


# =============================================================================
# Main
# =============================================================================

try:
    gyms = Gyms(GYMFILE)
    print('Gyms loaded')
except IOError:
    print('ERROR: Unable to load gyms from', GYMFILE)
    sys.exit()

try:
    pokemon = Pokemon(POKEMONFILE)
    print('Pokemon loaded')
except IOError:
    print('ERROR: Unable to load pokemon from', GYMFILE)
    sys.exit()

try:
    params = load_params(PARAMSFILE)
    print('Parameters loaded')
    if 'legendaries' not in params:
        print('WARNING: Legendaries not set')
except IOError:
    pass

CatbotLog.init(HOST_LOGFILE)

if __name__ == "__main__":
    dotenv.load_dotenv()
    key = os.getenv('DISCORD_TOKEN')
    if key is None:
        print('ERROR: Discord Key not found in the environment variables')
        sys.exit()
    bot.run(key)
