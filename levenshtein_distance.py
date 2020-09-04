# -*- coding: utf-8 -*-
"""
Created on Tue Sep  1 14:54:14 2020

@author: Mei
"""


def memoize(func):
    mem = {}

    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in mem:
            mem[key] = func(*args, **kwargs)
        return mem[key]

    return memoizer


@memoize
def levenshtein(s, t):
    if s == "":
        return len(t)

    if t == "":
        return len(s)

    if s[-1] == t[-1]:
        cost = 0
    else:
        cost = 1

    res = min([levenshtein(s[:-1], t) + 1,           # char is inserted
               levenshtein(s, t[:-1]) + 1,           # char is deleted
               levenshtein(s[:-1], t[:-1]) + cost])  # char is substituted

    return res
