# -*- coding: utf-8 -*-
"""
Created on Fri May 25 13:16:32 2018

@author: Mei
"""

import sched
import time
import datetime

def print_event(name):
    print("It's:", datetime.datetime.now(), name)

def do_event(when, action, actionargs=()):
    action(*actionargs)
    when = when + 10
    scheduler.enterabs(when, 1, do_event, (when, action, actionargs))
    
scheduler = sched.scheduler(time.time, time.sleep)

#print("START:", time.time())
#scheduler.enter(1, 1, print_event, ('first',))
#scheduler.run()

start_time = time.mktime(time.strptime('05/25/2018 8:03PM', '%m/%d/%Y %I:%M%p'))

scheduler.enterabs(start_time, 1, do_event, (start_time, print_event, ("Mei",)))
scheduler.run(blocking=True)