# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 10:15:51 2018

@author: Mei
"""
import csv
import string


def process_name(name):
    new_name = name.lower()

    new_name = new_name.replace('’', "'")

    table = str.maketrans({key: None for key in string.punctuation})
    new_name = new_name.translate(table)

    new_name = new_name.replace(' ', '')
    return new_name


class Gyms:
    '''
    A class for a list of Pokemon Go gyms

    Methods:

    Exceptions:
        raises IOError if the gym file cannot be opened
    '''

    gyms = {}
    aliases = {}

    def __init__(self, gym_fname):
        self.read_csv(gym_fname)

    def read_csv(self, gym_fname):
        with open(gym_fname) as gymfile:
            gymreader = csv.DictReader(gymfile, delimiter=',', quotechar='"')
            for row in gymreader:
                namekey = process_name(row['name'])
                self.gyms[namekey] = row
                if len(row['alias']) > 0:
                    self.aliases[process_name(row['alias'])] = namekey

    def search_names(self, name):
        found = []
        for namekey in self.gyms:
            if name in namekey:
                found.append(namekey)
        return found

    def search_aliases(self, name):
        found = []

        for alias in self.aliases:
            if name in alias:
                found.append(self.aliases[alias])
        return found

    def find(self, name):
        found = []

        processed_name = process_name(name)

        if processed_name in self.aliases.keys():
            found = [self.aliases[processed_name]]

        if not found:
            if processed_name in self.gyms.keys():
                found = [processed_name]

        if not found:
            found = self.search_names(processed_name)

        return found

    def get_link(self, gym):
        LINK_BASE = 'http://maps.google.com/maps?q='
        return LINK_BASE + self.gyms[gym]['latitude'] + ',' \
            + self.gyms[gym]['longitude']

    def get_name(self, gym):
        return self.gyms[gym]['name']

    def is_ex(self, gym):
        if self.gyms[gym]['ex'] == '1':
            return True
        return False
