# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 21:36:35 2020

@author: Mei
"""

import unittest
import catbot as cb


class CatbotTests(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
