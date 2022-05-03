# -*- coding: utf-8 -*-
"""
Created on Tue May  3 11:27:09 2022

@author: renkert2
"""

import itertools

list1 = ["a", "b", "c"]
list2 = [1,2,3]
list3 = ["A","B","C"]

list = [list1, list2, list3]

combinations = [c for c in itertools.product(*list)]

print(combinations)
print(len(combinations))