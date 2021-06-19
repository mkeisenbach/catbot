# -*- coding: utf-8 -*-
"""
Created on Sun Aug 30 11:04:35 2020

@author: Mei
"""

import unittest
from gyms import Gyms


class GymTests(unittest.TestCase):
    def setUp(self):
        self.gyms = Gyms('gyms.csv')

    def test_gym_not_found(self):
        self.assertEqual(len(self.gyms.find('asdf')), 0)

    def test_find_by_alias(self):
        self.assertEqual(self.gyms.find('VMP'),
                         ['veteransmemorialparkfremontvmp'])
        self.assertEqual(self.gyms.find('VMPUC'),
                         ['veteransmemorialparkunioncityvmpuc'])
        self.assertEqual(self.gyms.find('Veterans Memorial Park Fremont'),
                         ['veteransmemorialparkfremontvmp'])


if __name__ == '__main__':
    unittest.main()
