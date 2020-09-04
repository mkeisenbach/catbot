# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 13:25:13 2020

@author: Mei
"""
import csv
from levenshtein_distance import levenshtein


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
        filename = ''

        filename = self.pokedex.get(boss.lower(), '')

        if filename != '':
            return URL_BASE + filename + '.png'
        return filename

    def find(self, boss):
        boss = boss.lower()
        max_distance = len(boss) // 3

        if boss in self.pokedex:
            return boss

        candidate = ''
        best_d = max_distance + 1
        is_multiple = False

        for pokemon in self.pokedex:
            if abs(len(boss) - len(pokemon)) <= best_d:
                d = levenshtein(boss, pokemon)
                if d == best_d:
                    is_multiple = True
                if d < best_d:
                    is_multiple = False
                    best_d = d
                    candidate = pokemon

        if best_d <= max_distance and not is_multiple:
            return candidate

        return ''
