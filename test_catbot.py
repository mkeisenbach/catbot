# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 21:36:35 2020

@author: Mei
"""

import unittest
import catbot as cb


class CatbotTests(unittest.TestCase):
    def setUp(self):
        cb.params['legendaries'] = ['heatran']

    def test_parse_host_args_pos(self):
        test_strings = [
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
            't5 hatches in 15 team valor preferred',
            't4 hatches in 15 team valor preferred',
            't3 hatches in 15 team valor preferred',
            't2 hatches in 15 team valor preferred',
            't1 hatches in 15 1234 1234 1344 add me then dm me'
            ]
        for args in test_strings:
            parsed = cb.parse_host_args(args.split())
            self.assertTrue(parsed, 'FAILED ON: ' + args)

    def test_parse_host_args_neg(self):
        test_strings = [
            'genesect in 15 team valor preferred',
            'starting in 15'
            ]
        for args in test_strings:
            self.assertFalse(cb.parse_host_args(args.split()),
                             'FAILED ON: ' + args)

    def test_parse_host_now_pos(self):
        test_strings = [
            'genesect starting now team valor preferred'
            'genesect starting now',
            'galarian wheezing starting now',
            ]
        for args in test_strings:
            self.assertTrue(cb.parse_host_now(args.split()),
                            'FAILED ON: ' + args)

    def test_parse_host_mins_left_pos(self):
        test_strings = [
            'genesect 15 min left team valor preferred',
            'genesect 15 mins left',
            'galarian wheezing 15 minutes left',
            ]
        for args in test_strings:
            self.assertTrue(cb.parse_host_mins_left(args.split()),
                            'FAILED ON: ' + args)

    def test_get_thumbnail(self):
        self.assertEqual(cb.get_thumbnail('T5'),
                         cb.EGG_URL_BASE + cb.EGG_LEGENDARY)
        self.assertEqual(cb.get_thumbnail('T4'),
                         cb.EGG_URL_BASE + cb.EGG3)
        self.assertEqual(cb.get_thumbnail('T3'),
                         cb.EGG_URL_BASE + cb.EGG3)
        self.assertEqual(cb.get_thumbnail('T2'),
                         cb.EGG_URL_BASE + cb.EGG1)
        self.assertEqual(cb.get_thumbnail('T1'),
                         cb.EGG_URL_BASE + cb.EGG1)
        self.assertEqual(cb.get_thumbnail('6'),
                         cb.EGG_URL_BASE + cb.EGG_MEGA)
        self.assertEqual(cb.get_thumbnail('MEGA'),
                         cb.EGG_URL_BASE + cb.EGG_MEGA)

        self.assertNotEqual(cb.get_thumbnail('heatran'), '')
        self.assertNotEqual(cb.get_thumbnail('Mega Charizard X'), '')
        self.assertNotEqual(cb.get_thumbnail('Mega'), '')

    def test_get_raid_tier(self):
        self.assertEqual(cb.get_raid_tier('mega'), 'mega')
        self.assertEqual(cb.get_raid_tier('Mega Venusaur'), 'mega')
        self.assertEqual(cb.get_raid_tier('Meganium'), 'other')

        self.assertEqual(cb.get_raid_tier('t5'), 'legendary')
        self.assertEqual(cb.get_raid_tier('heatran'), 'legendary')
        self.assertEqual(cb.get_raid_tier('golem'), 'other')
        self.assertEqual(cb.get_raid_tier('T5 heatran'), 'legendary')

        self.assertEqual(cb.get_raid_tier('T3'), 'other')
        self.assertEqual(cb.get_raid_tier('t1'), 'other')

    def test_create_embed(self):
        self.assertNotEqual(cb.create_embed('title', 'host', 'when', '', ''),
                            None)
        self.assertNotEqual(cb.create_embed('title', 'host', 'when', 'notes',
                                            ''), None)
        self.assertNotEqual(cb.create_embed('title', 'host', 'when', 'notes',
                                            'thumbnail'), None)

    def test_censor_notes(self):
        self.assertEqual(cb.censor_notes('prefer instinct'), 'prefer instinct')
        self.assertEqual(cb.censor_notes('dm'), '...')
        self.assertEqual(cb.censor_notes('pm'), '...')
        self.assertEqual(cb.censor_notes('dm for code'), '...for code')
        self.assertEqual(cb.censor_notes('DM'), '...')
        self.assertEqual(cb.censor_notes('dm me'), '...')
        self.assertEqual(cb.censor_notes('d.m'), '...')
        self.assertEqual(cb.censor_notes('d//m'), '...')
        self.assertEqual(cb.censor_notes('direct message'), '...')
        self.assertEqual(cb.censor_notes('direct msg'), '...')
        self.assertEqual(cb.censor_notes('direct message me'), '...')
        self.assertEqual(cb.censor_notes('direct message for code'),
                         '...for code')
        self.assertEqual(cb.censor_notes('message me for code'),
                         '... for code')
        self.assertEqual(cb.censor_notes('message for code'),
                         '...for code')
        self.assertEqual(cb.censor_notes('text me'), '...')
        self.assertEqual(cb.censor_notes('txt me'), '...')
        self.assertEqual(cb.censor_notes('text me for'), '... for')

    def test_parse_raid_pos(self):
        test_strings = [
            'Mega Slowpoke ends in 45 at Irvington Community Park',
            'Mega Slowpoke despawns in 45 at Irvington Community Park'
            ]
        for args in test_strings:
            self.assertTrue(cb.parse_raid(args.split()),
                            'FAILED ON: ' + args)

    def test_parse_raid_old_pos(self):
        test_strings = [
            'Mega Slowpoke 45 Irvington Community Park'
            ]
        for args in test_strings:
            self.assertTrue(cb.parse_raid_old(args.split()),
                            'FAILED ON: ' + args)

    def test_parse_egg_pos(self):
        test_strings = [
            '1 hatches in 45 at Irvington Community Park',
            '5 hatches in 45 at Irvington Community Park',
            '6 hatches in 45 at Irvington Community Park'
            ]
        for args in test_strings:
            self.assertTrue(cb.parse_egg(args.split()),
                            'FAILED ON: ' + args)

    def test_parse_egg_old_pos(self):
        test_strings = [
            '1 45 Irvington Community Park',
            '5 45 Irvington Community Park',
            '6 45 Irvington Community Park'
            ]
        for args in test_strings:
            self.assertTrue(cb.parse_egg_old(args.split()),
                            'FAILED ON: ' + args)


if __name__ == '__main__':
    unittest.main()
