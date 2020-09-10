# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 12:01:56 2020

@author: Mei
"""

from datetime import datetime


class CatbotLog():
    logfile = None

    @staticmethod
    def init(logfile):
        CatbotLog.logfile = logfile

    @staticmethod
    def write(tag, msg, server=''):
        assert CatbotLog.logfile is not None
        log = open(CatbotLog.logfile, 'a')
        log.write('{},{},{},{}\n'.format(datetime.now(), server, tag, msg))
        log.close()
