# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 13:25:13 2020

@author: Mei
"""
import csv


class Pokemon:
    def __init__(self, pokemon_fname):
        self.read_csv(pokemon_fname)

    def read_csv(self, pokemon_fname):
        self.pokedex = {}
        with open(pokemon_fname) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                self.pokedex[row[1].lower()] = row[2]

    def get_boss_url(self, boss):
        URL_BASE = 'https://ironcreek.net/catbot/pokemon/'
        filename = self.pokedex.get(boss.lower(), '')
        if filename != '':
            return URL_BASE + filename + '.png'
        return filename
