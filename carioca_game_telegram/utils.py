# -*- coding: utf8 -*-

from xml.etree import cElementTree

import requests

cards_dict = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 20, 'C': 30 }

def parse_new_game_names(n):
    names = n.split(',')
    items = []
    i=1
    for name in names:
        item = {}
        item['number'] = i
        item['name'] = name
        i+=1
        items.append(item)
    
    return items

def parse_add_result(score):

    cards = list(score)
    total = 0
    for card in cards:
        try:
            total+= cards_dict[card]
        except KeyError:
            return -1
    return total
