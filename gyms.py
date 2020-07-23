# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 10:15:51 2018

@author: Mei
"""
import csv
import string

'''

Exceptions:
    raises IOError if the gym file cannot be opened 
'''
class Gyms:
    gyms = {}
    aliases = {}
    
    def __init__(self, gym_fname):
        self.read_csv(gym_fname)
            
        
    def process_name(self, name):
        new_name = name.lower()
    
        new_name = new_name.replace('’', "'")
    
        table = str.maketrans({key: None for key in string.punctuation})
        new_name = new_name.translate(table) 
    
        new_name = new_name.replace(' ', '')
        return new_name
    
    def read_csv(self, gym_fname):       
        with open(gym_fname) as gymfile:
            gymreader = csv.DictReader(gymfile, delimiter=',', quotechar='"')
            for row in gymreader:
                namekey = self.process_name(row['name']) 
                self.gyms[namekey] = row
                if len(row['alias']) > 0:
                        self.aliases[self.process_name(row['alias'])] = namekey

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
       
        new_name = self.process_name(name) 
        if new_name in self.gyms.keys():
            found = [new_name]
        else:
            found = self.search_names(new_name)
            if len(found) == 0:
                found = self.search_aliases(new_name)
                
        return found
        
    def get_link(self, gym):
        LINK_BASE = 'http://maps.google.com/maps?q='
        return LINK_BASE + self.gyms[gym]['latitude'] + ',' + self.gyms[gym]['longitude']
    
    def get_name(self, gym):
        return self.gyms[gym]['name']

    def is_ex(self, gym):
        if self.gyms[gym]['ex'] == '1':
            return True
        return False
