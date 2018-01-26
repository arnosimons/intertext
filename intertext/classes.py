# -*- coding: utf-8 -*-

# classes.py
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

# https://stackoverflow.com/questions/21129020/how-to-fix-unicodedecodeerror-ascii-codec-cant-decode-byte
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')

import os
import spacy
import types
import distance
import weakref
import textacy
import textacy.keyterms
import collections
import networkx as nx
from pyzotero import zotero

from intertext.constants import * 
from intertext.functions import * 


### initiate spacy lang
# lang = spacy.load('en_core_web_sm')



### Actor Class
###############################################################################
class Actor(object):
	"""
	Create an ``Actor``::

		>>> a = intertext.Actor(name=u'Foucault, Michel')

	"""
	_universe = set()
	_originals = set()

	def __init__(self, **attr):
		if u'name' in attr.iterkeys():
			self.name = attr.pop(u'name')
		elif u'lastname' in attr.iterkeys():
			if u'firstname' in attr.iterkeys() and RE_FIRSTNAME.match(attr[u'firstname']):
				self.name = u', '.join(
					[attr.pop(u'lastname'), attr.pop(u'firstname').strip()])
			else:
				self.name = attr.pop(u'lastname')
		else:
			raise ValueError(u'Provide name or lastname'.format(attr))
		self.attr = attr # or {}
		label = self.name
		while label in [a().label for a in Actor._universe if a()]: # 'if a()' to exclude dead refs!
			label += u'*'
		self._label = label
		self._is_copy = any(self.is_like(a()) for a in Actor._universe if a())

		Actor._originals.add(weakref.ref(self._original))
		Actor._universe.add(weakref.ref(self))

	def __repr__(self):
		return self.label

	def call_label(self):
		return self._label

	@property
	def label(self):
		return self._label

	@property
	def name(self):
		return self._name

	@name.setter
	def name(self, name):
		if not isinstance(name, basestring):
			raise ValueError(u'Name must be unicode or string')
		if not RE_NAME.match(name):
			print name
			raise ValueError(u'Ill formatting: "{}"'.format(name))
		self._name = name
		splitname = [n for n in name.split(u', ')]
		self.lastname = splitname[0]
		if len(splitname) == 2:
			self.firstname = splitname[1]
		else:
			self.firstname = u''

	@property
	def lastname(self):
		return self._lastname

	@lastname.setter
	def lastname(self, lastname):
		if not isinstance(lastname, basestring):
			raise ValueError(u'Lastname must be unicode or string')
		if not RE_LASTNAME.match(lastname):
			raise ValueError(u'Ill formatting: "{}"'.format(lastname))
		self._lastname = lastname

	@property
	def firstname(self):
		return self._firstname

	@firstname.setter
	def firstname(self, firstname):
		if not isinstance(firstname, basestring):
			raise ValueError(u'firstname must be unicode or string')
		if not firstname:
			self._firstname = firstname
			return
		if not RE_FIRSTNAME.match(firstname):
			raise ValueError(u'Ill formatting: "{}"'.format(firstname))
		self._firstname = firstname

	@property
	def _original(self):
		for a in Actor._originals:
			if a() and self.is_like(a()):
				return a()
		return self
	
	@property
	def is_copy(self):
		return self._is_copy

	def is_like(self, other):
		if not isinstance(other, Actor):
			raise ValueError(u'Compare to another Actor!')
		return (
			self.name == other.name
			and self.attr.viewitems() <= other.attr.viewitems()
			)

	def is_in(self, others):
		return any(self.is_like(i) for i in others)

	def compares_to(self, other):
		if not isinstance(other, Actor):
			raise ValueError(u'Compare to another Actor!')
		# e.g. for abbreviated firstname or missing second firstname


### Text Class
###############################################################################
class Text(object):
	"""
	Create a ``Text``::

		>>> t = intertext.Text(title=u"L'Archéologie du savoir", date=u'1969')

	To Do:
	- rename cleantext/cleantext_path into 1) content, 2) path
	- think of getting rid of rawtext altogether...maybe leave rawtext_path so that if no cleantext_path exists, content can be generated from rawtext?

	"""
	_universe = set()
	_originals = set()

	def __init__(self, **attr):
		if not all(k in attr.iterkeys() for k in [u'title', u'date']):
			raise ValueError(u'Provide title and date!')
		self.title = attr.pop(u'title')
		self.date = attr.pop(u'date')
		self.authors = attr.pop(u'authors', [])
		self.editors = attr.pop(u'editors', [])
		self.cites = attr.pop(u'cites', [])

		# build properties/setters for all these:
		self.type = attr.pop(u'type', u'text')
		self.publisher = attr.pop(u'publisher', u'')
		self.publication = attr.pop(u'publicationTitle', u'')
		self.volume = attr.pop(u'volume', u'')
		self.issue = attr.pop(u'issue', u'')
		self.bookTitle = attr.pop(u'bookTitle', u'')
		self.edition = attr.pop(u'edition', u'')
		self.place = attr.pop(u'place', u'')
		self.pages = attr.pop(u'pages', u'')
		self.DOI = attr.pop(u'DOI', u'')
		self.ISBN = attr.pop(u'ISBN', u'')
		self.ISSN = attr.pop(u'ISSN', u'')

		self.abstract = attr.pop(u'abstract', u'')

		# Hieraus noch ordentliche setter machen...
		self.rawtext_path = attr.pop(u'rawtext_path', u'')
		self.cleantext_path = attr.pop(u'cleantext_path', u'')
		
		self.attr = attr # conainer for all other attributes
		self._year = (None, None)
		label = self.short
		while label in [t().label for t in Text._universe if t()]:
			label += u'*'
		self._label = label
		self._is_copy = any(self.is_like(t()) for t in Text._universe if t())
		Text._originals.add(weakref.ref(self._original))
		Text._universe.add(weakref.ref(self))

		# Textacy doc
		self._doc = None
		if self.cleantext_path:
			self.refresh_doc(content=self.cleantext)
			print u'-> textacy.Doc created for: {}'.format(self.label)

	def __repr__(self):
		return self.label

	@property
	def _original(self):
		for t in Text._originals: # narrow selection?
			if t() and self.is_like(t()):
				return t()
		return self

	@property
	def is_copy(self):
		return self._is_copy

	def is_like(self, other):
		if not isinstance(other, Text):
			raise ValueError(u'Compare to another Text')
		return (
			self.title == other.title
			and self.year == other.year
			and self.attr.viewitems() <= other.attr.viewitems() # https://stackoverflow.com/questions/9323749/python-check-if-one-dictionary-is-a-subset-of-another-larger-dictionary/35416899
			)

	def is_in(self, others):
		return any(self.is_like(i) for i in others)

	def compares_to(self, other, nlev=0.1, date_span=(4,4)):
		if not isinstance(other, Text):
			raise ValueError(u'Compare to another Text')		
		return 1 if (
			self.is_like(other)
			) else 2 if (
			self.year == other.year
			and distance.nlevenshtein(
				self.title, other.title, method=2) <= nlev
			) else 3 if (
			self.title == other.title
			and int(self.year) + date_span[1]
			>= int(other.year)
			>= int(self.year) - date_span[0]
			) else 4 if (
			distance.nlevenshtein(
				self.title, other.title, method=2) <= nlev
			and int(self.year) + date_span[1]
			>= int(other.year)
			>= int(self.year) - date_span[0]
			) else 99

	def best_matches_in(self, population, match_hierarchy=MATCH_HIERARCHY, min_percent_titlelength=80, same_firstletter=True):
		if not isinstance(population, list) and not all(isinstance(i, Text) for i in population):
			raise ValueError(u'Population must be list of Texts')
		matches = collections.defaultdict(list)
		if same_firstletter and min_percent_titlelength:
			selection = ((self.compares_to(t), t) for t in population 
				if t.title[0].lower() == self.title[0].lower()
				and min(len(t.title),len(self.title)) * 100 / max(len(t.title),len(self.title)) >= min_percent_titlelength)
		elif same_firstletter:
			selection = ((self.compares_to(t), t) for t in population 
				if t.title[0].lower() == self.title[0].lower())
		elif min_percent_titlelength:
			selection = ((self.compares_to(t), t) for t in population 
				if min(len(t.title),len(self.title)) * 100 / max(len(t.title),len(self.title)) >= min_percent_titlelength)
		else:
			selection = ((self.compares_to(t), t) for t in population)
		# for k,v in ((self.compares_to(t), t) for t in population if t.title[0].lower() == self.title[0].lower()):
		# 	matches[k].append(v)
		for k,v in selection:
			matches[k].append(v)
		for i in match_hierarchy:
			if matches[i]:
				return (matches[i], i)
		return (None, None)

	def call_label(self):
		return self._label

	@property
	def label(self):
		return self._label

	@property
	def short(self):
		year = self.year
		title = u'_'.join(self.title[:15].split())
		short = u'_'.join([year, title]) 
		return short

	@property
	def title(self):
		return self._title

	@title.setter
	def title(self, title):
		if not isinstance(title, basestring):
			raise ValueError(u'Title must be unicode or string')
		self._title = title

	@property
	def date(self):
		return self._date

	@date.setter
	def date(self, date):
		if not isinstance(date, basestring):
			raise ValueError(u'Date must be unicode or string')
		# test if date satisfies regex
		if not RE_VALID_DATE.match(date):
			raise ValueError(
				u'Ill formatting: "{}"'.format(date))
		self._date = date

	@property
	def year(self):
		# return re.findall(YEAR, self.date)[0]
		if self._year[1] == self.date:
			return self._year[0]
		year = re.findall(YEAR_abc, self.date)
		if len(year) > 1:
			print u'=> More than one year found in "{}". Will take: "{}"'.format(self.date, year[0][:4])
		self._year = (year[0][:4] or u'0000', self.date)
		return self._year[0]
		# return year[0][:4] or u'0000'

	@property
	def authors(self):
		return self._authors

	@property
	def firstauthor(self):
		return self._authors[0] if self._authors else None

	@authors.setter
	def authors(self, authors):
		self._authors = []
		self.add_authors(authors)

	def add_authors(self, authors):
		if isinstance(authors, list):
			for i in authors:
				if isinstance(i, Actor):
					if not i._original in self._authors:
						self._authors.append(i._original)
				elif isinstance(i, dict):
					candidate = Actor(**i)
					if not candidate._original in self._authors:
						self._authors.append(candidate._original)
				else:
					raise ValueError(u'Authors in list must be Actor or dict')
		elif isinstance(authors, Actor):
			if not authors._original in self._authors:
				self._authors.append(authors._original)
		elif isinstance(authors, dict):
			candidate = Actor(**i)
			if not candidate._original in self._authors:
				self._authors.append(candidate._original)
		else:
			raise ValueError(u'Authors must be list, Actor, or dict')

	@property
	def editors(self):
		return self._editors

	@editors.setter
	def editors(self, editors):
		self._editors = []
		self.add_editors(editors)

	def add_editors(self, editors):
		if isinstance(editors, list):
			for i in editors:
				if isinstance(i, Actor): 
					if not i._original in self._editors:
						self._editors.append(i._original)
				elif isinstance(i, dict):
					candidate = Actor(**i)
					if not candidate._original in self._editors:
						self._editors.append(candidate._original)
				else:
					raise ValueError(u'Editors in list must be Actor or dict')
		elif isinstance(editors, Actor):
			if not editors._original in self._editors:
				self._editors.append(editors._original)
		elif isinstance(editors, dict):
			candidate = Actor(**i)
			if not candidate._original in self._editors:
				self._editors.append(candidate._original)
		else:
			raise ValueError(u'Editors must be list, Actor, or dict')

	@property
	def cites(self):
		return sorted(list(self._cites), key=Text.call_label, reverse=True)

	@cites.setter
	def cites(self, others):
		self._cites = set()
		self.add_citations_to(others)

	def add_citations_to(self, others):
		if isinstance(others, list):
			for i in others:
				if isinstance(i, Text): 
					self._cites.add(i._original)
				elif isinstance(i, dict):
					candidate = Text(**i)
					self._cites.add(candidate._original)
				else:
					raise ValueError(u'Citations in list must be Text or dict')
		elif isinstance(others, Text):
			self._cites.add(others._original)
		elif isinstance(others, dict):
			candidate = Text(**others)
			self._cites.add(candidate._original)
		else:
			raise ValueError(u'Citations must be list, Text, or dict')

	def cited_by(self, population):
		if isinstance(population, Intertext):
			population = population._texts
		if not (
			isinstance(population, (list, set, tuple)) 
			and all(isinstance(i, Text) for i in population)
			):
				raise ValueError(u'Poulation must be iterable and can only contain Text elements')
		return sorted([t for t in population if self in t.cites], key=Text.call_label, reverse=True)

	@property
	def rawtext(self, read_method=u'textract'):
		if not self.rawtext_path:
			return u''
		return read_text(self.rawtext_path, read_method=read_method)

	@property
	def doc(self):
		return self._doc

	def refresh_doc(self, content=None, metadata=None, lang=u'en_core_web_sm'):
		if not any(isinstance(content, t) for t in [basestring, textacy.Doc]):
			raise ValueError(u'Content must be unicode, string or textacy.Doc')
		# What if content is empty? Try and decide
		metadata = metadata or {}
		if not isinstance(metadata, dict):
			raise ValueError(u'metadata must be dict')

		metadata.update({u'text':self})
		# print '==> metadata', metadata
		self._doc = textacy.Doc(content, metadata=metadata, lang=lang)

	# @doc.setter
	# def doc(self, content, metadata=None, lang=u'en_core_web_sm'):
	# 	if content is None:
	# 		self._doc = None
	# 		return
	# 	if not any(isinstance(content, t) for t in [basestring, textacy.Doc]):
	# 		raise ValueError(u'Content must be unicode, string or textacy.Doc')
	# 	# What if content is empty? Try and decide
	# 	metadata = metadata or {}
	# 	if not isinstance(metadata, dict):
	# 		raise ValueError(u'metadata must be dict')

	# 	metadata.update({u'text':self})
	# 	print '==> metadata', metadata
	# 	self._doc = textacy.Doc(content, metadata=metadata, lang=lang)

	# def refresh_doc(self):
	# 	self.doc = self.cleantext

	@property
	def cleantext(self, read_method=u'textract'):
		if not self.cleantext_path:
			return u''
		return read_text(self.cleantext_path, read_method=read_method)


	def make_cleantext(self, path=u'', replace=False, read_method=u'textract',
		fix_unicode=True, transliterate=True, **kwargs):
 		""" Reads rawtext and creates cleantext file (to be further hand cleaned)
 			To Do:
 			- handle user given paths: Should they only provide path or filename?
 			- When, where and how are cleantext paths uploaded to zotero?
 		"""
 		if not self.rawtext_path or not os.path.isfile(self.rawtext_path):
 			print u'Provide correct rawtext_path!'
			return
		if not path:
			path = self.rawtext_path.rsplit(u'.',1)[0]+'_CLEAN.txt'
		else:
			u'Sorry, this functionality is not yet implemented...'
			return
		if os.path.isfile(path) and not replace:
			print u'A file with that name already exists. Set "replace=True" to overwrite'
			return
		cleantext = read_text(self.rawtext_path, read_method=read_method)
		if not cleantext:
			print u'Error while reading rawtext. '\
			u'Make sure this file exists: "{}"'.format(self.rawtext_path)
		cleantext = clean_text(cleantext, **kwargs)
		# file_path = unicode(os.path.join(path, self.label)) # what if label changes?
		print u'\t...creating file: "{}"'.format(path)
		print self.rawtext_path
		with open(path, 'w') as f:
			f.write(cleantext)
		self.cleantext_path = path # Hieraus noch richtige setter machen?

	def open_rawtext(self):
		if not self.rawtext_path:
 			print u'Provide rawtext_path!'
			return
		os.system(''.join([u'open ',self.rawtext_path])) # https://stackoverflow.com/questions/7343388/open-pdf-with-default-program-in-windows-7


	def open_cleantext(self):
		if not self.cleantext_path:
 			print u'Provide cleantext_path!'
			return
		os.system(''.join([u'open ',self.cleantext_path])) # https://stackoverflow.com/questions/7343388/open-pdf-with-default-program-in-windows-7
		# subprocess.call(['sublime',self.cleantext_path]) # only if I know the app...

	def words_in_context(self, words, ignore_case=True, window_width=50, 
		print_only=True):
		if not self.doc:
			raise ValueError(u'Text has no doc!')
		words_in_context([self.doc], words=words, ignore_case=True, 
			window_width=50, print_only=True)

	def terms(self, ngrams=(1, 2, 3), named_entities=True, normalize=u'lemma',
		lemmatize=None, lowercase=None, as_strings=False, **kwargs):
		if self.doc:
			return self.doc.to_terms_list(ngrams=ngrams, 
				named_entities=named_entities, normalize=normalize, 
				lemmatize=lemmatize, lowercase=lowercase, 
				as_strings=as_strings, **kwargs)

	def keywords(self, normalize=u'lemma', window_width=2, 
		edge_weighting=u'binary', ranking_algo=u'pagerank', 
		join_key_words=False, n_keyterms=10, **kwargs):
		if self.doc:
			return textacy.keyterms.key_terms_from_semantic_network(self.doc,
				normalize=normalize, window_width=window_width, 
				edge_weighting=edge_weighting, ranking_algo=ranking_algo, 
				join_key_words=join_key_words, 
				n_keyterms=n_keyterms, **kwargs)

	def semantic_network(self, nodes=u'words', normalize=u'lemma', 
		edge_weighting=u'default', window_width=10):
		if self.doc:
			return self.doc.to_semantic_network(nodes=nodes, 
				normalize=normalize, edge_weighting=edge_weighting, 
				window_width=window_width)

	def bag_of_words(self, normalize=u'lemma', lemmatize=None, lowercase=None, 
		weighting=u'count', as_strings=False):
		if self.doc:
			return self.doc.to_bag_of_words(normalize=normalize, 
				lemmatize=lemmatize, lowercase=lowercase, weighting=weighting, 
				as_strings=as_strings)

	def bag_of_term(self, normalize=u'lemma', lemmatize=None, lowercase=None, 
		weighting=u'count', as_strings=False):
		if self.doc:
			return self.doc.to_bag_of_words(normalize=normalize, 
				lemmatize=lemmatize, lowercase=lowercase, weighting=weighting, 
				as_strings=as_strings)

	def bag_of_terms(self, ngrams=(1, 2, 3), named_entities=True, 
		normalize=u'lemma', lemmatize=None, lowercase=None, weighting=u'count', 
		as_strings=False, **kwargs):
		if self.doc:
			return self.doc.to_bag_of_terms(ngrams=ngrams,
				named_entities=named_entities, normalize=normalize, 
				lemmatize=lemmatize, lowercase=lowercase, weighting=weighting, 
				as_strings=as_strings, **kwargs)

	



### Intertext Class
###############################################################################
class Intertext(object):
	'''
	Build Intertext container like? So that I can call Intertext[:4], etc?
	https://stackoverflow.com/questions/43627405/understanding-getitem-method
	'''

	def __init__(self, name, texts=None):
		self.name = name
		self.texts = texts
		# self.refresh_corpus()

	def __len__(self):
		return len(self._texts)

	@property
	def name(self):
		return self._name

	@name.setter
	def name(self, name):
		if not isinstance(name, basestring):
			raise ValueError(u'Name must be unicode or string')
		self._name = name

	# @property
	# def corpus(self):
	# 	return self._corpus

	# def refresh_corpus(self):
	# 	docs = [t.doc for t in self.texts if t.doc]
	# 	self._corpus = Corpus(docs=docs)

	@property
	def docs(self):
		return [t.doc for t in self._texts if t.doc]

	@property
	def texts(self):
		return sorted(list(self._texts), key=Text.call_label)

	@texts.setter
	def texts(self, texts):
		self._texts = set()
		if texts:
			self.add_texts(texts)

	def add_texts(self, texts):
		if isinstance(texts, list):
			for i in texts:
				if isinstance(i, Text):
					self._texts.add(i._original)
				elif isinstance(i, dict):
					self._texts.add(Text(**i)._original)
				else:
					raise ValueError(u'Texts in list must be Text or dict')
		elif isinstance(texts, Text):
			self._texts.add(texts._original)
		elif isinstance(texts, dict):
			self._texts.add(Text(**i)._original)
		else:
			raise ValueError(u'Texts must be list, Text, or dict')

	@property
	def authors(self):
		return sorted(list(set(a for t in self._texts for a in t.authors)), key=Actor.call_label)

	@property
	def editors(self):
		return sorted(list(set(a for t in self._texts for a in t.editors)), key=Actor.call_label)

	@property
	def co_authors(self):
		edgelist = ((d,a) for d in self._texts for a in d.authors)
		return co_occurrences(edgelist)

	@property
	def co_editors(self):
		edgelist = ((d,a) for d in self._texts for a in d.editors)
		return co_occurrences(edgelist)

	@property
	def cited_texts(self):
		return sorted(set([c for t in self._texts for c in t.cites]), key=Text.call_label)

	@property
	def citations(self):
		return [(d,c) for d in self._texts for c in d.cites]

	@property
	def co_citations(self):
		edgelist = ((d,c) for d in self._texts for c in d.cites)
		return co_occurrences(edgelist)

	@property
	def bibliographic_coupling(self):
		edgelist = ((d,c) for d in self._texts for c in d.cites)
		return co_occurrences(edgelist, focus=u'source')


	def load_Zotero(self, Z, basic=True, citations=True, fulltext=False, 
		upload_new=True, match_hierarchy=MATCH_HIERARCHY, 
		min_percent_titlelength=80, same_firstletter=True):
		'''
		Loads data from Zotero Collection
		'''
		# What about refresh? Check workflow
		print u'\nLoading Zotero data...'
		zot_texts = set()
		zot_citfiles = []
		for i in Z.texts:
			d = dict(i) # to be able to pop
			d[u'type'] = d.pop(u'itemType', u'')
			d[u'publication'] = d.pop(u'publicationTitle', u'')
			d[u'abstract'] = d.pop(u'abstractNote', u'')			
			d[u'authors'] = [Actor(
				lastname=c[u'lastName'],
				firstname=c[u'firstName'],
				) for c in d[u'creators'] if c[u'creatorType'] == u'author']
			d[u'editors'] = [Actor(
				lastname=c[u'lastName'],
				firstname=c[u'firstName'],
				) for c in d.pop(u'creators') if c[u'creatorType'] == u'editor']
			rawtext = Z.rawtext_by_key(d[u'key'])
			if rawtext:
				d[u'rawtext_path'] = rawtext['path']
			cleantext = Z.cleantext_by_key(d[u'key'])
			if cleantext:
				d[u'cleantext_path'] = cleantext['path']
			t = Text(**d)
			print u'...adding {}'.format(t._original)
			self.add_texts(t._original)
			if upload_new:
				zot_texts.add(t._original)
			if citations:
				citfile = Z.citfile_by_key(d[u'key'])
				if citfile:
					zot_citfiles.append((citfile, t))
		if citations:
			zot_uploads = set()
			for citfile in zot_citfiles:
				citfile, citing = citfile
				print u'\t...loading citations from "{}"'.format(
					citfile[u'path'])
				citlist = read_text(citfile[u'path'])
				for c in parse_citlist(citlist):
					print u'\t\t...adding {}'.format(
						u'_'.join([c[u'date'], c[u'title'][:15]]))
					c = Text(**c)
					matches = c.best_matches_in(self.texts, 
						match_hierarchy=MATCH_HIERARCHY,
						min_percent_titlelength=min_percent_titlelength,
						same_firstletter=same_firstletter) # takes long, can I speed up somehow? 
					if matches[0]:
						c = matches[0][0]
						print u'\t\t...adding {}'.format(c)
						print '\t\t\t...matches {} (at level {})'.format(matches[0][0],matches[1])
						if len(matches[0]) > 1:
							print u'\t\t\t\t...took the first out of {}'.format(matches[0])
						citing.add_citations_to(c)
					else:
						c = c._original
						citing.add_citations_to(c)
					if upload_new:
						zot_uploads.add(c)
			if upload_new:
				'''
				Complete this part...
				'''
				zot_uploads_old = zot_uploads
				zot_uploads = zot_uploads.difference(zot_texts)
				print u'\n...AFTER: zot_uploads:', len(zot_uploads)
				for i in zot_uploads:
					print i
				print u'\n...AFTER: not_uploads:', len(zot_uploads_old.difference(zot_uploads))
				for i in zot_uploads_old.difference(zot_uploads):
					print i

		clean_originals(Actor) # to remove dead weakrefs
		clean_originals(Text) # to remove dead weakrefs
		# self.refresh_corpus()
		Z.refresh()
		print u'...done.'


	def co_words(self, min_freq=3, width=4, 
		directed=False, lemma=True, within_doc=False, connectors=False,
		filter_stops=True, filter_punct=True, filter_nums=True,
		include_pos=None, exclude_pos=None, output=u'generator'):
		''' 
		Returns co_words for the intertext
		- min_freq = only output co_words that occur more than or equal to this threshold
		- width = length of the sliding window
		- within_doc = if True: counts each co-ocurrence within doc, if False: max 1 co-occurrence per doc
		- connectors: If True, shows connectors (only applicable if output is either 'gnerator' or 'list')
		- directed: If True, DiGraph is used to differentiate between (emissions, trading) and (trading, emissions)
		To Do:
		- Option for connector = author?
		'''
		print u'\nExtracting co-words from "{}"'.format(self.name)
		# if not isinstance(self._corpus, Corpus):
		# 	print u'\t...no corpus. Make one first.'
		# 	return
		# if self._corpus.__len__() < 1:
		# 	print u'\t...corpus is empty.'
		# 	return
		kwargs = {
			u'filter_stops':filter_stops,
			u'filter_punct':filter_punct,
			u'filter_nums':filter_nums,
			u'include_pos':include_pos,
			u'exclude_pos':exclude_pos, # Note that min_freq is used here not within textacy.extract.words() but for co-words! 
		}
		G = nx.DiGraph() if directed else nx.Graph()
		label_tokens_pairs = ((
			text.label, list(textacy.extract.words(text.doc, **kwargs))) 
			for text in self._texts if text.doc)
		for ltp in label_tokens_pairs:
			for win in sliding_window(ltp[1], width):
				win = [t.lemma_ for t in win] \
					if lemma else [t.lower_ for t in win]
				for i in range(1, width):
					if not G.has_edge(win[0], win[i]):
						G.add_edge(win[0], win[i], 
							freq = 1, 
							connectors = {ltp[0]:1})
					elif not within_doc:
						if not ltp[0] in G[win[0]][win[i]]\
							[u'connectors'].iterkeys():
							G[win[0]][win[i]][u'freq'] += 1
							G[win[0]][win[i]][u'connectors'][ltp[0]] = 1
					elif within_doc:
						G[win[0]][win[i]][u'freq'] += 1
						if not ltp[0] in G[win[0]][win[i]][u'connectors'].iterkeys():
							G[win[0]][win[i]][u'connectors'][ltp[0]] = 1
						else:
							G[win[0]][win[i]][u'connectors'][ltp[0]] += 1
		if output==u'generator':
			return (e if connectors else e[:2]+({u'freq':e[2][u'freq']},) 
				for e in G.edges(data=True) if e[2][u'freq']>=min_freq)
		elif output==u'list':
			return [e if connectors else e[:2]+({u'freq':e[2][u'freq']},) 
				for e in G.edges(data=True) if e[2][u'freq']>=min_freq]
		elif output==u'nx':
			G.remove_edges_from([e for e in G.edges(data=True) if e[2][u'freq']<min_freq])
			return G

	def words_in_context(self, words, ignore_case=True, window_width=50, print_only=True):
		words_in_context((doc for doc in self.docs), words=words, ignore_case=True, window_width=50, print_only=True)


	def topics(self, selection=None, method=u'nmf', n_topics=20, 
		weighting=u'tfidf', normalize=True, smooth_idf=True, 
		min_df=1, max_df=1.0, max_n_terms=100000):
		# http://textacy.readthedocs.io/en/latest/_modules/textacy/tm/topic_model.html
		# https://textacy.readthedocs.io/en/latest/api_reference.html#textacy.vsm.Vectorizer
		print u'\nExtracting topics'
		terms_list = (doc.to_terms_list(ngrams=1, named_entities=True, as_strings=True) 
			for doc in self.docs) # add if conditions!
		# understanding min_df/max_df -> https://stackoverflow.com/questions/27697766/understanding-min-df-and-max-df-in-scikit-countvectorizer
		vectorizer = textacy.vsm.Vectorizer(weighting=weighting, normalize=normalize, 
			smooth_idf=smooth_idf, min_df=min_df, max_df=max_df, max_n_terms=max_n_terms)
		return TopicModel(terms_list, vectorizer, method=method, n_topics=n_topics)


### Zotero class
###############################################################################
class Zotero(object):
	
	def __init__(self, api_key, library_id, library_type, collection_id=None):
		print u'\nEstablishing Zotero handler...'
		if collection_id == None:
			raise ValueError(u'Provide collection_id')
		self.web = zotero.Zotero(library_id, library_type, api_key)
		self.library_id = library_id
		self.library_type = library_type
		self.api_key = api_key
		self.collection_id = collection_id
		self.refresh()
		print u'...done.'

	def refresh(self):
		self._data = [i[u'data'] for i in self.web.everything(
			self.web.collection_items(self.collection_id))]

	@property
	def data(self):
		return self._data

	@property
	def texts(self):
		return [i for i in self._data if not any(
			i[u'itemType'] == t for t in [u'attachment', u'note'])]

	@property
	def attachments(self):
		return [i for i in self._data 
			if i[u'itemType'] == u'attachment']

	@property
	def citnotes(self):
		return [i for i in self._data 
			if i[u'itemType'] == u'note'
			and u'parentItem' in i.iterkeys()
			and u'RDA citations' in [t.values()[0] for t in i[u'tags']]]
	
	@property
	def citfiles(self):
		return [i for i in self._data 
			if i[u'itemType'] == u'attachment'
			and any(
				i[u'contentType'] == t for t in [u'text/html', u'text/plain'])
			and i.get(u'parentItem')
			and u'RDA citations' in [t.values()[0] for t in i[u'tags']]]

	def citfile_by_key(self, key):
		result = [i for i in self.citfiles if i.get(u'parentItem') == key]
		if result:
			if len(result) > 1:
				raise ValueError(u'More than one citfile of parent "{}"'.format(key))
			return result[0]
		return None
		
	@property
	def rawtexts(self):
		return [i for i in self._data
			if i['itemType'] == u'attachment' 
			and all(k in i.iterkeys() for k in [u'parentItem', u'path'])
			and u'RDA rawtext' in [t.values()[0] for t in i[u'tags']]]

	def rawtext_by_key(self, key):
		result = [i for i in self.rawtexts if i.get(u'parentItem') == key]
		if result:
			if len(result) > 1:
				raise ValueError(u'More than one rawtexts of parent "{}"'.format(key))
			return result[0]
		return None

	@property
	def cleantexts(self):
		return [i for i in self._data
			if i[u'itemType'] == u'attachment' 
			and all(k in i.iterkeys() for k in [u'parentItem', u'path'])
			and u'RDA cleantext' in [t.values()[0] for t in i[u'tags']]]


	def cleantext_by_key(self, key):
		result = [i for i in self.cleantexts if i.get(u'parentItem') == key]
		if result:
			if len(result) > 1:
				raise ValueError(u'More than one cleantexts of parent "{}"'.format(key))
			return result[0]
		return None

	@property
	def publicationTitles(self, filename=None):
		titles = [data.get('publicationTitle') for i in self._data 
				if data.get('publicationTitle')]
		if not filename:
			return titles
		else:
			write_list_to_lines(titles, filename)
			print u'publicationTitles written to: "{}"'.format(filename)
			return None

	def item_by_key(self, key):
		'''
		Returns a Zotero item given its key
		'''
		result = [i for i in self._data if i.get(u'key') == key]
		if result:
			if len(result) > 1:
				raise ValueError(u'More than one item with key "{}"'.format(key))
			return result[0]
		return None

	def upload_cleantexts(self, source):
		'''
		uploads new cleantexts from source (text or intertext) 
		as attachments to zotero library
		'''
		if not any(isinstance(source, t) for t in [Intertext, Text]):
			raise ValueError(u'source must be Text or Intertext')
		if isinstance(source, Text):
			if not source.cleantext_path:
				print u'No cleantexts to upload'
				return
			source = [source]
		else: # source = Intertext
			source = source.texts
		relevant_texts = (text for text in source if text.cleantext_path 
			and text.cleantext_path not in (i['path'] for i in self.cleantexts)) # allow update of existing attachments?
		if not relevant_texts:
			print u'No cleantexts to upload'
			return
		for t in relevant_texts:
			upload = self.web._attachment_template('linked_file') # see https://github.com/urschrei/pyzotero/blob/master/pyzotero/zotero.py
			upload[u'title'] = os.path.split(t.cleantext_path)[1]
			upload[u'path'] = t.cleantext_path
			upload[u'tags'] = [{u'tag':u'RDA cleantext'}]
			upload[u'contentType'] = u'text/html'
			print u'\tUploading Zotero attachment: "{}"'.format(t.cleantext_path)
			self.web.create_items([upload],t.attr[u'key'])
		return

	def prepare_cleantexts(self, path=u'', replace=False, read_method=u'textract',
		fix_unicode=True, transliterate=True, **kwargs):
 		""" Reads any textfile tagged in Zotero as 'RDA rawtext' and reates 
 		clean txt.file (to be further hand cleaned), 

 		To Do: 
 		- allow user specific path?
 		- refresh at start? Otherwise replace=True can result in multiple uploads cause self.cleantexts remains old!
 		"""
		kwargs = dict(kwargs)
		kwargs[u'transliterate'] = transliterate
		kwargs[u'fix_unicode'] = fix_unicode
 		print u'\nPreparing Zotero cleantext attachments. '\
 			u'Existing files will {}be replaced.\n'\
 			u'...settings for text cleaning: {}'.\
 			format('' if replace else 'not ', kwargs)
 		self.refresh()
 
 		if replace == True:
			new_attachments = [{
				u'rawpath': r[u'path'],
				u'cleanpath': r[u'path'].rsplit(u'.',1)[0]+'_CLEAN.txt',
				u'title': os.path.split(r[u'path'].rsplit(u'.',1)[0]+'_CLEAN.txt')[1],
				u'existing_clean': [c[u'key'] for c in self.cleantexts \
					if c[u'parentItem'] == r[u'parentItem']],
				u'parent': r[u'parentItem'],
				u'tags': [{u'tag':u'RDA cleantext'}]} 
				for r in self.rawtexts
				]
		elif replace == False:
 			new_attachments = [{
 				u'rawpath': r[u'path'],
				u'cleanpath': r[u'path'].rsplit(u'.',1)[0]+'_CLEAN.txt',
				u'title': os.path.split(r[u'path'].rsplit(u'.',1)[0]+'_CLEAN.txt')[1],
				u'existing_clean': '',
				u'parent': r[u'parentItem'],
				u'tags': [{u'tag': u'RDA cleantext'}]} 
				for r in self.rawtexts 
				if not r[u'parentItem'] in [c[u'parentItem'] 
					for c in self.cleantexts]]
		else:
			raise ValueError(u'keyword argument "replace" must be True or False!')
		if new_attachments:
			print u'\t...{} file{} found. Please wait...'.\
				format(len(new_attachments),'s' if len(new_attachments) > 1 else '')
 			for a in new_attachments:
				cleantext = read_text(a[u'rawpath'], read_method=read_method)
				cleantext = clean_text(cleantext, **kwargs)

				### create txt file
				print u'\t...creating file: "{}"'.format(a[u'cleanpath'])
				with open(a[u'cleanpath'], u'w') as f:
					f.write(cleantext)
				
				### create or update Zotero attachment
				upload = self.web._attachment_template('linked_file') # see https://github.com/urschrei/pyzotero/blob/master/pyzotero/zotero.py
				upload[u'title'] = a[u'title']
				upload[u'path'] = a[u'cleanpath']
				upload[u'tags'] = [{u'tag':u'RDA cleantext'}]
				upload[u'contentType'] = u'text/html'
				if not a[u'existing_clean']:
					print u'\t...creating Zotero attachment: "{}"'.format(a[u'cleanpath'])
					self.web.create_items([upload],a['parent'])
				else:
					print u'\t...updating path in existing Zotero '\
						'attachment: "{}"'.format(a[u'cleanpath'])
					existing = self.web.item(a['existing_clean'][0])
					existing[u'data'][u'title'] = upload[u'title']
					existing[u'data'][u'path'] = upload[u'path']
					existing[u'data'][u'contentType'] = upload[u'contentType']
					self.web.update_item(existing)
		else:
			print u'...no files to prepare.'




### TopicModel class
###############################################################################
class TopicModel(object):
	'''
	This class only implements textacy's original TM handling.
	'''

	def __init__(self, terms_list, vectorizer, method=u'nmf', n_topics=20):
		print '\n Creating mew topic model'
		self.vectorizer = vectorizer
		self.doc_term_matrix = self.vectorizer.fit_transform(terms_list)
		self.model = textacy.tm.TopicModel(method, n_topics=n_topics)
		self.model.fit(self.doc_term_matrix)
		# self.doc_topic_matrix = self.model.transform(self.doc_term_matrix)
		self.doc_topic_matrix = self.model.get_doc_topic_matrix(
			self.doc_term_matrix, normalize=True) # builds on model.transform
		self.id2term = vectorizer.id_to_term

	def __repr__(self):
		return repr(self.model)

	def __len__(self):
		return len(self.model)

	def top_topic_terms(self, topics=-1, top_n=10, weights=False):
		return self.model.top_topic_terms(
			self.id2term , topics=-1, top_n=10, weights=False)

	def top_topic_docs(self, topics=-1, top_n=10, weights=False):
		return self.model.top_topic_docs(
			self.doc_topic_matrix, topics=-1, top_n=10, weights=False)

	def top_doc_topics(self, docs=-1, top_n=3, weights=False):
		return self.model.top_doc_topics(
			self.doc_topic_matrix, docs=-1, top_n=3, weights=False)

	def topic_weights(self):
		return self.model.topic_weights(self.doc_topic_matrix)

	def termite_plot(self, topics=-1, sort_topics_by='index', highlight_topics=None, 
		n_terms=25, rank_terms_by='topic_weight', sort_terms_by='seriation', 
		save=False):
		return self.model.termite_plot(self.doc_term_matrix, self.id2term , 
			topics=-1, sort_topics_by='index', highlight_topics=None, n_terms=25, 
			rank_terms_by='topic_weight', sort_terms_by='seriation', save=False)



### Corpus class
###############################################################################
class Corpus(textacy.Corpus):

	def __init__(self, lang=u'en_core_web_sm', texts=None, docs=None, metadatas=None):
		textacy.Corpus.__init__(self, lang=lang, texts=texts, docs=docs, metadatas=metadatas)

	def stopwords(self, case_sensitive=True):
		if case_sensitive == True:
			return sorted([l.orth_ for l in self.spacy_lang.vocab if l.is_stop])
		elif case_sensitive == False:
			return sorted(set([l.lower_ for l in self.spacy_lang.vocab if l.is_stop]))
		else:
			raise ValueError(u'keyword argument "case_sensitive" must be True or False.')
		# return sorted(list(self._stopwords))

	def add_stopwords(self,words,case_sensitive=True):
		print u'\n Adding stopwords:', words
		for word in words:
			if case_sensitive:
				self.spacy_lang.vocab[unicode(word.lower())].is_stop = True
				self.spacy_lang.vocab[unicode(word.upper())].is_stop = True
				self.spacy_lang.vocab[unicode(word.title())].is_stop = True
			else:
				self.spacy_lang.vocab[unicode(word)].is_stop = True

	def remove_stopwords(self,words,case_sensitive=True):
		print u'\n Removing stopwords:', words
		for word in words:
			if case_sensitive:
				self.spacy_lang.vocab[unicode(word.lower())].is_stop = False
				self.spacy_lang.vocab[unicode(word.upper())].is_stop = False
				self.spacy_lang.vocab[unicode(word.title())].is_stop = False
			else:
				self.spacy_lang.vocab[unicode(word)].is_stop = False




