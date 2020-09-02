import subprocess
import os
import codecs
import json
import re
from pathlib import Path
from .translation import translation
from .ATF_transliteration_parser import transliteration

class Object(object):
  pass

PLACEHOLDERS = ['NUMB']

#---/ ATF parser /-------------------------------------------------------------
#
class atf_parser:
  '''
  '''
  re_brc = re.compile(r'(\(.+\))')
  re_translit_comment = re.compile(r'(( |-|)\(\$.+\$\)( |-|))')

  def __init__(self, path='', filenames='', dest_path='', prefix=''):
    '''
    '''
    self.data = []
    self.texts = []
    all_vars = True
    for v in [path, filenames, dest_path, prefix]:
      if len(v)==0:
        all_vars = False
        break
    if all_vars==True:
      self.parse(path, filenames, dest_path, prefix)

  def parse(self, path, filenames, dest_path, prefix):
    '''
    '''
    if not os.path.exists(dest_path):
      os.makedirs(dest_path)
    self.load_collection(path, filenames)
    self.parse_all_data()
    self.export_csv(dest_path, prefix)
    self.export_for_giza(dest_path, prefix)

  def load_collection(self, path, filenames):
    '''
    '''
    for f in filenames:
      with codecs.open(path+'/'+f, 'r', 'utf-8') as f:
        self.data+=f.readlines()

  def parse_all_data(self):
    '''
    '''
    for line in self.data:
      self.parse_line(line)

  def parse_line(self, line):
    '''
    '''
    if not hasattr(self, 'O'):
      self.O = Object()
    line = line.strip('\n')
    if line:
      if '&P' in line and ' = ' in line:
        if hasattr(self.O, 'CDLI'):
          self.texts.append({'CDLI': self.O.CDLI,
                             'PUB': self.O.PUB,
                             'lines_lst': self.O.lines_lst})
        self.O.lines_lst = []
        self.O.CDLI, self.O.PUB = line.strip('&').split(' = ', 1)
      elif '#tr.en' in line:
        tlat_str = line.replace('#tr.en', '').strip(' :')
        tlat_obj = translation(tlat_str)
        self.O.translation = tlat_obj.processed_str
        self.O.lines_lst.append({'no': self.O.line_no,
                               'translit': self.O.translit,
                               'translation': self.O.translation,
                               'normalization': \
                                 self.normalize_tltr(self.O.translit)
                               })
      elif is_int(line[0]) and '. ' in line:
        self.O.line_no, self.O.translit = line.split('. ', 1)
      else:
        pass
        # the parser is designed to extract only certain, relevant data.
        # extend here to retrieve other information.

  def export_csv(self, path, prefix):
    '''
    '''
    data_str = ''
    for txt in self.texts:
      for l in txt['lines_lst']:
        data_str+='%s$%s\n' %(l['normalization'], l['translation'])
    self.dump(data_str, path+'/sum_eng_%s.csv' %prefix)

  def export_for_giza(self, path, prefix):
    '''
    '''
    data_str_normalization = ''
    data_str_translation = ''
    for txt in self.texts:
      for l in txt['lines_lst']:
        data_str_normalization+='%s\n' %l['normalization']
        data_str_translation+='%s\n' %l['translation']
    self.dump(data_str_normalization, path+'/sumerian_'+prefix)
    self.dump(data_str_translation, path+'/english_'+prefix)

  def normalize_tltr(self, translit):
    '''
    '''
    n_lst = []
    if '($' in translit:
      #IMPORTANT! this removes comments:
      translit = self.re_translit_comment.sub('', translit)
    for token in translit.split(' '):
      t = transliteration(token)
      n = t.normalization
      if n!=None:
        if self.prev_same_placeholder_check(n, n_lst)==False:
          n_lst.append(n)
        else:
          n_lst = n_lst[:-1]+[n]
    return ' '.join(n_lst)

  def prev_same_placeholder_check(self, n, n_lst):
    '''
    '''
    if n_lst==[]:
      return False
    for p in PLACEHOLDERS:
      if p in n and p==n_lst[-1]:
        return True
    return False

  def normalize_trsl(self, tra_str):
    '''
    '''
    tra = translation(tra_str)
    return trt.processed_str

  def dump(self, data, filename):
    '''
    '''
    with codecs.open(filename, 'w', 'utf-8') as dump:
      dump.write(data)


if __name__ == '__main__':
  pass
