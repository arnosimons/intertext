# -*- coding: utf-8 -*-

# constants.py
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

import re

### For Text() Matching
###############################################################################
MATCH_HIERARCHY = [1,2,3,4,5]


### For citation parsing
###############################################################################
DEFAULT_A_GRAMMAR = u'ln,fn;'
DEFAULT_C_GRAMMAR = u'a/y/t/r'
A_GRAMMARS = {
	u'ln,fn;': u'lastname, firstname;',
	u'ln,fn,': u'lastname, firstname,',
	u'fn ln,': u'firstname lastname,',
	u'fn ln;': u'firstname lastname;',
	u'ln;': u'lastname;',
	u'ln,': u'lastname,'
	}
C_GRAMMARS = {
	u'a/y/t/r': u'author/year/title/rest',
	u'a/t/y/r': u'author/title/year/rest',
	u'y/a/t/r': u'year/author/title/rest',
	u'y/t/a/r': u'year/title/author/rest',
	u't/a/y/r': u'title/author/year/rest',
	u't/y/a/r': u'title/year/author/rest'
	}

ZOT_TEMPLATE_TXT = {
	u'contentType': u'text/plain', 
	u'itemType': u'attachment', 
	u'title': u'', 
	u'accessDate': u'', 
	u'linkMode': u'linked_file', 
	u'charset': u'', 
	u'relations': {}, 
	u'note': u'', 
	u'url': u'', 
	u'path': u'', 
	u'tags': []
	}

NOFIRSTNAME = u'_firstname'

RE_QUOTATIONS_SINGLE = re.compile(u'[\u0027\u2018\u2019\u201A\u201B\u2039'\
	u'\u203A\u300C\u300D\uFE41\uFE42\uFF07\uFF62\uFF63]') 

RE_QUOTATIONS_DOUBLE = re.compile(u'[\u0022\u00AB\u00BB\u201C\u201D\u201E'\
	u'\u201F\u300E\u300F\u301D\u301E\u301F\uFE43\uFE44\uFF02]')

RE_ESCAPE = re.compile(r'|'.join([r"(\\)'",r'(\\)"']))
RE_CHAR = re.compile(r'[\'",/:)(.&%\[\]\\*+-]')
RE_LONELY_CHAR = re.compile(r'(?<=\b)'
	+r'[bcdefghjklmnopqrstuvwxyzBCDEFGHJKLMNOPQRSTUVWXYZ](?=\b)')
RE_NUM = re.compile(r'[\d]+')
RE_P_TAGS = re.compile(r'<p>|</p>| ( )')
RE_AMP = re.compile(r'&amp;')
RE_CIT_LINEBREAKS = re.compile(r'<br />|<br>|<br/>|\r|\v')
RE_LINEBREAKS = re.compile(r'<br />|<br>|<br/>|\r|\v|\n')
RE_DOUBLE_SPACE = re.compile(r'\s+')
RE_CLEAN_DOUBLELINEBREAK = re.compile(r'\n([\s]*\n)') # yellow brackets needed?
RE_EMPTY_END_OF_STRING = re.compile(r'\n[\s]*$')
RE_EMPTY_END_OF_LINE = re.compile(r'[ \t]+\n')
RE_FORTHCOMING = re.compile(r'forthcoming|Forthcoming|FORTHCOMING|'\
	r'In Print|in print|IN PRINT')
RE_INTEXT_CITATION_CANDIDATE = re.compile(
	r'\([^()]*(?:19|20)\d\d[a-f]*[^()]*\)')
RE_DOI = re.compile(r'[dD][oO][iI]: *10[0-9./():<>;A-Za-z-]+|'\
	r'http://dx.doi.org/10[0-9./():<>;A-Za-z-]+')


### For date parsing
###############################################################################
YEAR = r'\d\d\d\d'
RECENTYEAR = r'(?:19|20)\d\d'
MODERNYEAR = r'(?:15|16|17|18|19|20)\d\d'
DAYOFMONTH = r'(?:0*[1-9]|1\d|2\d|30|31)\.*'
MONTH = r'(?:[Jj][aA][nN][uU]*[aA]*[rR]*[yY]*|'\
	r'[fF][eE][bB][rR]*[uU]*[aA]*[rR]*[yY]*|'\
	u'[mM][aA][rR][cC]*[hH]*|[mM][äÄ][rR][zZ]*|'\
	r'[aA][pP][rR][iI]*[lL]*|'\
	r'[mM][aA][yY]|[mM][aA][iI]|'\
	r'[jJ][uU][nN][eE]*|[jJ][uU][nN][iI]*|'\
	r'[jJ][uU][lL][yY]*|[jJ][uU][lL][iI]*|'\
	r'[aA][uU][gG][uU]*[sS]*[tT]*|'\
	r'[sS][eE][pP][tT]*[eE]*[mM]*[bB]*[eE]*[rR]*|'\
	r'[oO][cC][tT][oO]*[bB]*[eE]*[rR]*|[oO][kK][tT][oO]*[bB]*[eE]*[rR]*|'\
	r'[nN][oO][vV][eE]*[mM]*[bB]*[eE]*[rR]*|'\
	r'[dD][eE][cC][eE]*[mM]*[bB]*[eE]*[rR]*|[dD][eE][zZ][eE]*[mM]*[bB]*[eE]*[rR]*)'
DATE_MY = r' '.join([MONTH, RECENTYEAR])
DATE_DMY = r' '.join([DAYOFMONTH, MONTH, RECENTYEAR])
DATE_DMY_NUM = \
	r'(?:0*[1-9]|1\d|2\d|30|31)(?:/|-)(?:0*[1-9]|1[012])(?:/|-)(?:19|20)\d\d'
DATE_MDY = r' '.join([MONTH, DAYOFMONTH+r',*', RECENTYEAR])
DATE_YMD = r' '.join([RECENTYEAR, MONTH, DAYOFMONTH])
DATE_YMD_NUM = \
	r'(?:19|20)\d\d(?:/|-)(?:0*[1-9]|1[012])(?:/|-)(?:0*[1-9]|1\d|2\d|30|31)'
DATE_ALL = r'|'.join(
	[DATE_MY, DATE_DMY, DATE_YMD, DATE_MDY, DATE_YMD_NUM, DATE_DMY_NUM])

RE_DATE_MY = re.compile(r'\b'+DATE_MY+r'\b')
RE_DATE_DMY = re.compile(r'\b'+DATE_DMY+r'\b')
RE_DATE_MDY = re.compile(r'\b'+DATE_MDY+r'\b')
RE_DATE_ALL = re.compile(r'\b'+DATE_ALL+r'\b')
RE_MONTH = re.compile(r'\b'+MONTH+r'\b')
RE_YEAR = re.compile(r'\b'+YEAR+r'\b')
RE_RECENTYEAR = re.compile(r'\b'+RECENTYEAR+r'\b')
RE_DAYOFMONTH = re.compile(r'\b'+DAYOFMONTH+r'\b')

RE_VALID_DATE = re.compile(u'^'+YEAR+'|'+DATE_ALL+'$') # other formats?


### For name parsing
###############################################################################
ACCENTS_LOWER = u'àáâãäåæčçèéêëìíîïñòóôõöøœšùúûüýÿžß'
ACCENTS_UPPER = u'ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØŒŠÚÛÜÙÝŸŽ'

FIRSTNAME = u'[a-zA-Z{0}{1}][-a-zA-Z \.{0}{1}]*'.format(
	ACCENTS_LOWER, ACCENTS_UPPER)
LASTNAME = u"[a-zA-Z'{0}{1}][-a-zA-Z' {0}{1}]*".format(ACCENTS_LOWER,ACCENTS_UPPER)
NAME = u'{}(, {})?'.format(LASTNAME, FIRSTNAME)

RE_FIRSTNAME = re.compile(u'^{}$'.format(FIRSTNAME))
RE_LASTNAME = re.compile(u'^{}$'.format(LASTNAME))
RE_NAME = re.compile(u'^{}$'.format(NAME))