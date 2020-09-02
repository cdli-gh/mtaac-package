import codecs
import json
from unicodedata import *
##from word2number import w2n
from mtaac_package.syllabary import syllabary
##
##with codecs.open('numerals.txt', 'r', 'utf-8') as num:
##  lines = [l.strip('\r\n').split('\t') for l in num.readlines()]
##
##keys = ['char', 'cp', 'name', 'Borger 2003', 'Borger 1981', 'notes']
##
##dict_lst = [dict(zip(keys,l)) for l in lines]
##for d in dict_lst:
##  d['name-u'] = name(d['char']).replace("CUNEIFORM NUMERIC SIGN ", "")
##  print([d[k] for k in ['name-u']+keys[1:]])
##  try:
##    print(w2n.word_to_num(d['name-u']))
##  except ValueError:
##    print('!!!')

from mtaac_package.syllabary import syllabary

with codecs.open('numerals_ATF_unicode.txt', 'r', 'utf-8') as f:
  lines = [l.strip('\r\n').split('\t') for l in f.readlines()]

syl = syllabary()

keys = ['name', 'code']
dict_lst = [dict(zip(keys,l)) for l in lines]
for d in dict_lst:
  char = chr(int(d['code'].strip('U+'), 16))
  name_u = name(char).replace("CUNEIFORM NUMERIC SIGN ", "")
  print(name_u, syl.find_entry_by_code(d['code']))
