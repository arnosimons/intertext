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

from __future__ import division

import re
import ftfy
import collections
import itertools
import types
import textract
import textacy
import unicodedata
import subprocess
from bs4 import BeautifulSoup
from intertext.constants import * 




########################## Other functions #####################################################
def words_in_context(docs, words, ignore_case=True, window_width=50, print_only=True):
	# https://radimrehurek.com/gensim/models/word2vec.html
	# http://textminingonline.com/getting-started-with-word2vec-and-glove-in-python
	# https://rare-technologies.com/word2vec-tutorial/
	result = ((doc.metadata[u'text'].label, textacy.text_utils.keyword_in_context(doc.text, words, 
		ignore_case=ignore_case, window_width=window_width, print_only=False)) 
		for doc in docs)
	if print_only:
		for label_context in result:
			print u'\n{0}\n{1}\n{0}'.format(79*u'#',label_context[0])
			for line in label_context[1]:
				print line

def sliding_window(seq, n=2):
	return zip(*(collections.deque(itertools.islice(it, i), 0) or it
		for i, it in enumerate(itertools.tee(seq, n))))

def clean_originals(which):
	deadrefs = [i for i in which._originals if i() is None]
	map(which._originals.discard, deadrefs)

def write_list_to_lines(somelist, filename):
	with open(filename, u'w') as file:
		for i in somelist:
			file.write(u''.join([i, u'\n']))

def part_of_seq(idx, seq, n=4):
	'''
	Divides a sequence in n parts and returns the part where element is in.
	Relies on float division!
	'''
	if idx > len(seq):
		raise ValueError(u'Index cannot be greater than length of sequence')
	mark = len(seq) / n
	markers = [(i+1, mark * (i+1)) for i in range(n)]
	for i, m in markers:
		if idx <= m:
			return i


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

def read_text(path, read_method=u'textract'):
	# Hier noch Formate unterscheiden! Slate zB nur PDF!!! 
	if read_method == u'textract':
		text = unicode(textract.process(path)) # http://textract.readthedocs.io/en/latest/python_package.html
	elif read_method == u'slate':
		with open(path) as f:
			text = unicode(slate.PDF(f))
	else:
		print u'Provide accepted read_method ("textract", "slate")'
		return u''
	return text

def read_txt(path):
	with open(path) as text:
		return text.read()

def clean_string(string):
	string = re.sub(RE_QUOTATIONS_SINGLE, u"'", string)
	string = re.sub(RE_QUOTATIONS_DOUBLE, u'"', string)
	string = re.sub(RE_DASHES, u'-', string)
	return ' '.join(string.split()).lower().replace(u'"',"'")

def parse_authors(authors, a_grammar): # here or outside method/class?
	outlist = []
	parsed_authors = re.sub(r'\b[Ee][Tt] [Aa][Ll]\.* *,*;*', r'', authors)
	if ';' in a_grammar:
		parsed_authors = re.sub(
			r'[, ]+and |[, ]+And |[, ]+AND |[, ]*&', r'; ', parsed_authors)
		parsed_authors = re.sub(
			r';[ \t]*;',r'; ',parsed_authors) # kill double commas
		parsed_authors = parsed_authors.rstrip(u';')
	else:
		parsed_authors = re.sub(
			r'[, ]+and |[, ]+And |[, ]+AND |[, ]*&', r', ', parsed_authors)
		parsed_authors = re.sub(
			r',[ \t]*,', r', ', parsed_authors) # kill double commas
		parsed_authors = parsed_authors.rstrip(',')		
	if a_grammar  ==u'ln,fn;':
		for a in parsed_authors.split(u';'):
			a_split = a.strip().split(u',')
			lastname = a_split[0].strip()
			if len(a_split) > 1:
				firstname = a_split[1].strip()
			else:
				firstname = u''
			# outlist.append((lastname, firstname))
			outlist.append({u'lastname':clean_string(lastname), u'firstname':clean_string(firstname)})
	elif a_grammar==u'ln,fn,':
		parsed_authors=parsed_authors.split(',')
		if not len(parsed_authors) & 1:
			parsed_authors = [','.join(parsed_authors[i:i+2]) 
				for i in range(0, len(parsed_authors), 2)]
			for a in parsed_authors:
				a_split = a.strip().split(u',')
				lastname = a.split(u',')[0].strip()
				if len(a_split) > 1:
					firstname = a_split[1].strip()
				else:
					firstname = u''
				# outlist.append((lastname, firstname))
				outlist.append({u'lastname':clean_string(lastname), u'firstname':clean_string(firstname)})
		elif len(parsed_authors) == 1:
			lastname = parsed_authors[0].strip()
			firstname = u''
			# outlist.append((lastname, firstname))
			outlist.append({u'lastname':clean_string(lastname), u'firstname':firstname})
		else:
			lastname = u'xxx'
			firstname = u'xxx'
			# outlist.append((u'xxx', u'xxx')) # Does this eveer happen? Construct test case!
			# outlist.append((lastname, firstname))
			outlist.append({u'lastname':lastname, u'firstname':firstname})
	elif a_grammar == u'fn ln,':
		for a in parsed_authors.split(u','):
			a_split = a.strip().rsplit(u' ',1)
			if len(a_split) > 1:
				lastname =  a_split[1]
				firstname = a_split[0]
				# outlist.append((lastname, firstname))
				outlist.append({u'lastname':clean_string(lastname), u'firstname':clean_string(firstname)})
			else:
				lastname = a_split[0]
				firstname = u''
				# outlist.append((lastname, firstname))
				outlist.append({u'lastname':clean_string(lastname), u'firstname':firstname})
	elif a_grammar == u'fn ln;':
		for a in parsed_authors.split(u';'):
			a_split = a.strip().rsplit(u' ',1)
			if len(a_split) > 1:
				lastname = a_split[1]
				firstname = a_split[0]
				# outlist.append((lastname, firstname))
				outlist.append({u'lastname':clean_string(lastname), u'firstname':clean_string(firstname)})
			else:
				lastname = a_split[0]
				firstname = u''
				# outlist.append((lastname, firstname))
				outlist.append({u'lastname':clean_string(lastname), u'firstname':firstname})
	return outlist


def parse_citlist(citlist):

	parsed = []

	c_grammar = DEFAULT_C_GRAMMAR
	a_grammar = DEFAULT_A_GRAMMAR

	citlist = unicodedata.normalize("NFKC", citlist) # nennt z.B. "&"" Zeichen um...(in "&amp;"" oder so)				
	citlist = RE_P_TAGS.sub('', citlist) # kill stuff (html tags and repeated blanks)
	citlist = RE_AMP.sub('&', citlist) # make real "&" symbols
	citlist = RE_QUOTATIONS_SINGLE.sub("'", citlist) # normalize single quotation marks to "'"
	citlist = RE_QUOTATIONS_DOUBLE.sub('"', citlist) # normalize double quotation marks to '"'
	citlist = RE_CIT_LINEBREAKS.sub('\n', citlist) # make stuff to linebreaks
	citlist = RE_CLEAN_DOUBLELINEBREAK.sub('\n\n', citlist)  # Kill arbitrary \n and blanks between item blocks
	citlist = RE_EMPTY_END_OF_STRING.sub('', citlist) # Kill arbitrary \n and blanks at the end of the note
	citlist = RE_EMPTY_END_OF_LINE.sub('\n', citlist) # Kill arbitrary blanks and tabs before a linebreak
	citlist = citlist.split('\n\n') # split into blocks

	# Process citlist block by block
	for block in citlist:
		block = block.strip()
		if u'\n' in block:
			cit = block.split('\n')

			if len(cit) in range(3,5):
				parsed.append({
					u'date': unicode(cit[c_grammar.lower().split(r'/').index(u'y')]).strip(u' |(|)|.|,'),
					u'authors': parse_authors(cit[c_grammar.lower().split(r'/').index(u'a')],a_grammar),
					u'title': clean_string(unicode(cit[c_grammar.lower().split(r'/').index(u't')])).strip(u',').strip(u"'").strip(u'.')
					})
			else:
				print u'\t\t...citations must have 3-4 lines -> ignoring: "{}"'.format(cit)

		elif u'A_GRAMMAR' in block:
			a_grammar_match = re.match(
				r'^A_GRAMMAR=(?P<new_a_grammar>.*)$', block)
			if a_grammar_match:
				new_a_grammar = re.sub(
					r', *', r',', a_grammar_match.group('new_a_grammar'))
				if new_a_grammar in A_GRAMMARS.iterkeys():
					print u'\t\t...author grammar changed to: "{}"'.format(A_GRAMMARS[new_a_grammar])
					a_grammar = new_a_grammar
				else:
					print u'\t\t..."{}" is not an allowed author grammar'.format(new_a_grammar)
		
		elif u'C_GRAMMAR' in block:
			c_grammar_match = re.match(
				r'^C_GRAMMAR=(?P<new_c_grammar>.*)$', block)
			if c_grammar_match:
				new_c_grammar = re.sub(
					r'/ *',r'/', c_grammar_match.group(u'new_c_grammar'))
				if new_c_grammar in C_GRAMMARS.iterkeys():
					c_grammar = new_c_grammar
					print u'\t\t...citation grammar changed to: "{}"'.format(C_GRAMMARS[new_c_grammar])
				else:
					print u'\t\t..."{}" is not an allowed citation grammar'.format(new_c_grammar)
		else:
			print u'\t\t...cannot interpret this line: "{}"'.format(block)
	return parsed

def clean_text(text, run_test=False, #special=False,
	fix_unicode=False, transliterate=False, no_linebreaks=False, 
	no_accents=False, no_contractions=False, no_urls=False, 
	no_emails=False, no_phone_numbers=False, no_citations=False, 
	no_doi=False, no_date=False, no_currency_symbols=False, 
	no_numbers=False, no_punct=False, lowercase=False, 
	no_lonelychars=False):
	""" Cleans text, building on textacy preprocess functionality
	"""
	if run_test:
		print u'\n\n RAW:\n{}\n{}\n\n{}\n'.format(
			u'>'*25, repr(text[:1000]), repr(text[-1000:]))
	# Basic stuff
	# if special:
	# 	text = re.sub(r'\xc2\xa0', u'', text)
	# 	text = re.sub(r'\t|\u', u'', text)
	if fix_unicode is True:
		text = ftfy.fix_text(text, normalization=u'NFC')
		""" 'NFC' combines characters and diacritics written using separate code points,
        e.g. converting "e" plus an acute accent modifier into "é"; unicode
        can be converted to NFC form without any change in its meaning!
        if 'NFKC', additional normalizations are applied that can change
        the meanings of characters, e.g. ellipsis characters will be replaced
        with three periods. 
        (source: http://textacy.readthedocs.io/en/latest/_modules/textacy/preprocess.html#fix_bad_unicode)
		"""
		if run_test:
			print u'\n\n CLEAN --> {}:\n{}\n{}\n\n{}\n'.format(
				u'fix_unicode', u'>'*25, repr(text[:1000]), repr(text[-1000:]))
	if no_linebreaks is True:
		text = RE_LINEBREAKS.sub(' ',text)
		if run_test:
			print u'\n\n CLEAN --> {}:\n{}\n{}\n\n{}\n'.format(
				u'no_linebreaks', u'>'*25, repr(text[:1000]), repr(text[-1000:]))
	if transliterate is True:
		text = textacy.preprocess.transliterate_unicode(text)
		if run_test:
			print u'\n\n CLEAN --> {}:\n{}\n{}\n\n{}\n'.format(
				u'transliterate', u'>'*25, repr(text[:1000]), repr(text[-1000:]))
	if no_accents is True: # Redundant if transliterate: http://textacy.readthedocs.io/en/latest/api_reference.html#module-textacy.preprocess
		text = textacy.preprocess.remove_accents(text, method='unicode')
		if run_test:
			print u'\n\n CLEAN --> {}:\n{}\n{}\n\n{}\n'.format(
				u'no_accents', u'>'*25, repr(text[:1000]), repr(text[-1000:]))
	if no_contractions is True:
		text = textacy.preprocess.unpack_contractions(text)
		if run_test:
			print u'\n\n CLEAN --> {}:\n{}\n{}\n\n{}\n'.format(
				u'no_contractions', u'>'*25, repr(text[:1000]), repr(text[-1000:]))
	# Replace urls, emails, citations, etc.
	if no_doi:
		text = RE_DOI.sub(u'*DOI*', text)
		if run_test:
			print u'\n\n CLEAN --> {}:\n{}\n{}\n\n{}\n'.format(
				u'no_doi', u'>'*25, repr(text[:1000]), repr(text[-1000:]))
	if no_urls is True:
		text = textacy.preprocess.replace_urls(text)
		if run_test:
			print u'\n\n CLEAN --> {}:\n{}\n{}\n\n{}\n'.format(
				u'no_urls', u'>'*25, repr(text[:1000]), repr(text[-1000:]))
	if no_emails is True:
		text = textacy.preprocess.replace_emails(text)
		if run_test:
			print u'\n\n CLEAN --> {}:\n{}\n{}\n\n{}\n'.format(
				u'no_emails', u'>'*25, repr(text[:1000]), repr(text[-1000:]))
	if no_phone_numbers is True:
		text = textacy.preprocess.replace_phone_numbers(text)
		if run_test:
			print u'\n\n CLEAN --> {}:\n{}\n{}\n\n{}\n'.format(
				u'no_phone_numbers', u'>'*25, repr(text[:1000]), repr(text[-1000:]))
	# if no_doi:
	# 	text=RE_DOI.sub('*DOI*', text)
	# 	if run_test:
	# 		print u'\n\n CLEAN --> {}:\n{}\n{}\n\n{}\n'.format(u'no_doi', u'>'*25, repr(text[:1000]), repr(text[-1000:]))
	if no_citations is True:
		text = RE_INTEXT_CITATION_CANDIDATE.sub(u'*CITATION*',text)
		if run_test:
			print u'\n\n CLEAN --> {}:\n{}\n{}\n\n{}\n'.format(
				u'no_citations', u'>'*25, repr(text[:1000]), repr(text[-1000:]))
	if no_date is True:
		text = RE_DATE_ALL.sub(u'*DATE*', text)
		if run_test:
			print u'\n\n CLEAN --> {}:\n{}\n{}\n\n{}\n'.format(
				u'no_date', u'>'*25, repr(text[:1000]), repr(text[-1000:]))
	if no_currency_symbols is True:
		text = textacy.preprocess.replace_currency_symbols(text)
		if run_test:
			print u'\n\n CLEAN --> {}:\n{}\n{}\n\n{}\n'.format(
				u'no_currency_symbols', u'>'*25, repr(text[:1000]), repr(text[-1000:]))

	# More fundamental stuff, but must come at the end, so not to corrupt above cleaning methods
	if no_numbers is True:
		text = textacy.preprocess.replace_numbers(text)
		if run_test:
			print u'\n\n CLEAN --> {}:\n{}\n{}\n\n{}\n'.format(
				u'no_numbers', u'>'*25, repr(text[:1000]), repr(text[-1000:]))
	if no_punct is True:
		text = textacy.preprocess.remove_punct(text)
		if run_test:
			print u'\n\n CLEAN --> {}:\n{}\n{}\n\n{}\n'.format(
				u'no_punct', u'>'*25, repr(text[:1000]), repr(text[-1000:]))
	if lowercase is True:
		text = text.lower()
		if run_test:
			print u'\n\n CLEAN --> {}:\n{}\n{}\n\n{}\n'.format(
				u'lowercase', u'>'*25, repr(text[:1000]), repr(text[-1000:]))
	if no_lonelychars:
		text = RE_LONELY_CHAR.sub(u'', text)
	text = re.sub(u'\*', u'', text)
	text = textacy.preprocess.normalize_whitespace(text)
	if run_test:
		print u'\n\n CLEAN --> {}:\n{}\n{}\n\n{}\n{}\n'.format(
			u'whitespace', u'>'*25, repr(text[:1000]), repr(text[-1000:]), u'-'*100)
	return text