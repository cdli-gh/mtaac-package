import subprocess
import os
import codecs
import json
import re
import math
from pathlib import Path
from random import sample
#from multiprocessing import Pool

from mtaac_package.ATF_transliteration_parser import transliteration, sylb
from mtaac_package.morph_annotation import *

mc = morph_converter()

#---/ CoNLL file /-------------------------------------------------------------
#
class conll_file:
  '''
  The class parses the .conll data.
  '''
  corpus_conventions = {'cdli': 'ORACC',
                        'etcsl': 'ETCSL',
                        'etcsri': 'ORACC'}
  
  def __init__(self, path):
    '''
    '''
    self.tags = tags()
    self.tokens_lst = []
    self.info_dict = {}
    self.info_lst = []
    for c in self.corpus_conventions.keys():
      if c in str(path):
        self.corpus = c
        self.convention = self.corpus_conventions[c]
    with codecs.open(path, 'r', 'utf-8') as f:
      self.data = f.read()
    self.parse()

  def parse(self):
    '''
    '''
    token_ID = ''
    for l in self.data.splitlines():
      if l:
        if l[0] not in ['#', ' ']:
          self.add_token(l.split('\t'), token_ID)
        elif l[0]=='#':
          self.info_lst.append(l)
          if ': ' in l:
            info_lst = l.strip('# ').split(': ')
            key = info_lst[0].strip(' ')
            value = ': '.join(info_lst[1:]).strip(' ')
            self.info_dict[key] = value
          elif '.' in l:
            token_ID = l.strip('# ')
          else:
            l = l.strip('# ')
            if l:
              if ('WORD' in l or 'FORM' in l) and 'ID' in l:
                l = l.replace("XPOSTAG", "POS")
                l = l.replace("FORM", "WORD")
                self.info_dict['legend'] = l.split('\t')
              else:
                self.info_dict['title'] = l
                
  def add_token(self, token_lst, token_ID):
    '''
    '''
    token_dict = self.make_token_dict(token_lst, token_ID)
    if 'SEGM' in token_dict.keys() and 'BASE' not in token_dict.keys():
      [token_dict['BASE'], token_dict['SENSE']] = \
                           self.segm_to_base_and_sense(token_dict['SEGM'])
    if 'WORD' in token_dict.keys():
      tw = transliteration(token_dict['WORD'])
      if tw.defective==False:
        token_dict['WORD'] = [tw.normalization,
                              tw.normalization_u,
                              tw.sign_and_det_normalization]
      token_dict['WORD_RAW'] = tw.raw_translit
    if 'BASE' in token_dict.keys():
      tb = transliteration(token_dict['BASE'], base=True)
      if tb.defective==False:
        token_dict['BASE'] = [tb.normalization,
                              tb.normalization_u,
                              tb.sign_and_det_normalization]
    if self.filter_token(token_dict)!=False:
      self.tokens_lst.append(token_dict)
    else:
      # DO NOT OMIT LINES!
      # ToDo:
      # 1. Ensure this is in the others versions of this class elsewhere.
      # 2. Check cases:
      #     - might be caused by [] in BASE / SEGM!
      print('WARNING! Defective token:', token_dict)
      self.tokens_lst.append(token_dict)

  def make_token_dict(self, token_lst, token_ID):
    '''
    '''
    token_dict = {'ID': token_ID}
    if 'legend' not in self.info_dict.keys():
      if token_lst[-1] not in ['_', 'proper', 'emesal', 'glossakk']:
        print('-1', token_lst[-1])
      legend = ['ID', 'WORD', 'BASE', 'POS', 'SENSE'] # ETCSL
    else:
      legend = self.info_dict['legend']
    i = 0
    while i < len(legend):
      try:
        if legend[i]=='POS':
          token_dict['MORPH2'] = token_lst[i]         
          token_dict['POS'] = self.tags.adjust_POS(
            token_lst[i], self.convention)
        else:
          token_dict[legend[i]] = token_lst[i]
      except IndexError:
        token_dict[legend[i]] = '_'
      i+=1
    return token_dict

  def segm_to_base_and_sense(self, segm):
    '''
    Recieve segmentation, return lemma.
    '''
    for s in segm.split('-'):
      if '[' in s and ']' in s:
        base = s.split('[')[0]
        sense = s.split('[')[1][:-1]
        return [base, sense]
    return ['_', '_']

  def filter_token(self, t):
    '''
    '''
    if 'LANG' in t.keys():
      if 'akk' in t['LANG']:
        return False
    try:
      for tag in ['WORD', 'BASE', 'POS']:
        tt = t[tag]
        if type(tt)==list:
          tt = ''.join(tt)
        if '_' in tt or tt=='':
          return False
    except KeyError:
      return False
    if type(t['WORD'])!=list or type(t['BASE'])!=list:
      return False
    return True    

  def __str__(self):
    '''
    Return CoNLL string.
    '''
    # TODO: costumize output formats, if needed.
    conll_fields = ['ID', 'WORD_RAW', 'BASE', 'SENSE', 'MORPH2', 'POS', 'SEGM']
    conll_str = '\n'.join([i for i in self.info_lst if ' ID\t' not in i])+'\n'
    conll_str+='# %s\n' %'\t'.join(conll_fields)
    for t in self.tokens_lst:
      row_vals = []
      for cf in conll_fields:
        v = t[cf]
        if cf=='MORPH2':
          v = self.add_position_placeholders(t[cf])
        if type(v)==list:
          row_vals.append(v[0])
        else:
          row_vals.append(v)
      conll_str+='\t'.join(row_vals)+'\n'
    print(conll_str)
    return conll_str

  def get_position_placeholders(self, morph_str):

    '''
    Add ORACC-style position placeholders in morph. annotation.
    '''
    return mc.MTAAC2ORACC(morph_str)

if __name__ == '__main__':
  pass
