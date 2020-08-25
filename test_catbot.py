# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 21:36:35 2020

@author: Mei
"""

import catbot as cb

parse_host_args_matches = [
    'genesect starting in 15 team valor preferred',
    'genesect starting in 15 min team valor preferred',
    'genesect starting in 15 mins team valor preferred',
    'genesect starting in 15 minutes team valor preferred',
    'genesect starting in 15 minute team valor preferred',
    'genesect starting in 15 team valor preferred',
    'genesect starting in 15 1234 1234 1234',
    'genesect starting in 15 1234-1234-1234',
    'genesect starting in 15 123412341234',
    'genesect starting in 15',
    'genesect hatches in 10',
    'genesect ends in 5',
    'genesect ending in 5',
    'galarian wheezing ending in 30',
    'genesect starting now team valor preferred'
    'genesect starting now',
    'galarian wheezing starting now',
    't5 hatches in 15 team valor preferred',
    't4 hatches in 15 team valor preferred',
    't3 hatches in 15 team valor preferred',
    't2 hatches in 15 team valor preferred',
    't1 hatches in 15 1234 1234 1344 add me then dm me'
    ]

parse_host_args_no_matches = [
    'genesect in 15 team valor preferred',
    'starting in 15'
    ]


def test_parse_host_args_pos():
    for args in parse_host_args_matches:
        parsed = cb.parse_host_args(args.split())
        if len(parsed) == 0:
            print('FAILED ON: ' + args)
            return False
    return True


def test_parse_host_args_neg():
    for args in parse_host_args_no_matches:
        parsed = cb.parse_host_args(args.split())
        if len(parsed) > 0:
            print('FAILED ON: ' + args)
            return False
    return True


test_parse_host_args_pos()
test_parse_host_args_neg()
