# -*- coding: utf-8 -*-

# functions.py
###############################################################################
# Written by Arno Simons

# Released under GNU General Public License, version 3.0

# Copyright (c) 2017 Arno Simons

# This file is part of Intertext.

# Intertext is free software: you can redistribute it and/or modify it under 
# the terms of the GNU General Public License as published by the Free 
# Software Foundation, either version 3 of the License, or (at your option) any
 # later version.

# Intertext is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with 
# Intertext. If not, see <http://www.gnu.org/licenses/>.
###############################################################################

import collections
import itertools
import types
from intertext.constants import * 

def set_match_hierarchy(hierarchy):
	if not isinstance(hierarchy, list) and not all(isinstance(i, int) for i in hierarchy):
		raise ValueError
	MATCH_HIERARCHY = hierarchy

def reset_match_hierarchy():
	MATCH_HIERARCHY = [1,2,3,4,5]

def co_occurrences(edgelist, focus=u'target'):
	''' 
	returns a defaultdict, which maps each co_occurrence (key) to a set of 
	connectors (value)
	'''
	if not isinstance(edgelist,(list,types.GeneratorType)):
		raise ValueError(u'edgelist must be list or generator ' \
			'and can only contain 2-tuples')
	nbrs = collections.defaultdict(set)
	co_occurrences = collections.defaultdict(set)
	for e in edgelist: # if I dropped raising Errors here, I could do: for s,t in edgelist
		if not (isinstance(e,tuple) and len(e) == 2):
			raise ValueError(u'edgelist must be list or generator ' \
			'and can only contain 2-tuples')
		k,v = e[0], e[1]
		if focus == u'source':
			k,v = v,k
		nbrs[k].add(v)
	for k,v in nbrs.iteritems():
		for pair in itertools.combinations(v,2):
			co_occurrences[pair].add(k)
	return co_occurrences

# L = [('a','b'),('a','c'),('b','c'),('b','d'),('b','p'),('a','d')]
# gen = (i for i in L)
# print co_occurrences(gen, focus=u'target')
# fgh