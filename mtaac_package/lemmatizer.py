import codecs
from .common_functions import *
from .ATF_transliteration_parser import *

# TODO:
# 1. save file with tokens for lemmatization to temp
# 2. lemmatize to temp (no stdin / stdout as it seems)
# 3. read lemmatized temp
# 4. delete both
# 5. return lemmata

lemma_norm_dict = {
  '1' : ['dita', 'did'],
  '100': ['meat'],
  '1000' : ['lim', 'limum'],
  '60': ['jec', 'cuci'],
  '600' : ['jectu'],
  'amatud': ['emedu'],
  'anzu': ['anzud'],
  'asil': ['asila'],
  'bilulu': ['belili'],
  'sipad': ['suba'],
  'de': ['tum', 'lah', 'di', 'ga'],
  'tuc': ['dur', 'durun'],
  'uc': ['ug'],
  'jen': ['du', 'er', 'ri', 'ere', 'era', 'iri', 'sub'],
  'lug': ['se', 'ze', 'ce'],
  'til': ['se'],
  'gub': ['sug'],
  'dug': ['di', 'e'],
  'kur': ['sun'],
  'nin': ['gacan'],
  'gecnimbar': ['gecimmar'],
}

sp = subprocesses()
_path = os.path.dirname(os.path.realpath(__file__))

class CSTLemma(common_functions):
  '''
  Basic wrapper class to lemmatize with CSTLemma.
  Windows only.
  '''
  CSTLEMMA_PATH = os.path.join(
    _path, 'CSTLemma', 'executables', 'cstlemma64.exe')
  AFFIXTRAIN_PATH = os.path.join(
    _path, 'CSTLemma', 'executables', 'affixtrain.exe')
  FLEX_PATH = os.path.join(
    _path, 'CSTLemma', 'flex_patterns', 'data_norm_u', '0',
    'flexrules.training_data_norm_u_XC')
  DICT_PATH = os.path.join(_path, 'CSTLemma', 'dictionaries', 'dict_norm_u')
  LEMMATIZE_PATH = os.path.join(_path, 'CSTLemma', 'temp', 'lemmatize.txt')
  LEMMATIZED_PATH = os.path.join(_path, 'CSTLemma', 'temp', 'lemmatized.txt')
  
  def __init__(self):
    '''
    '''
    pass
  
  def lemmatize_conll_lst(self, conll_lst):
    '''
    '''
    self.drop_for_lemmatization(conll_lst)
    self.lemmatize(self.FLEX_PATH, self.DICT_PATH,
                   self.LEMMATIZE_PATH, self.LEMMATIZED_PATH)
    self.add_lemmatized_to_conll_lst(conll_lst)
    return conll_lst
  
  def drop_for_lemmatization(self, conll_lst):
    '''
    '''
    tokens_lst = []
    for c in conll_lst:
      tokens_lst+=[t['FORM_NORM_U'] for t in c['tokens_lst']]
    self.dump('\n'.join(tokens_lst), self.LEMMATIZE_PATH)

  def add_lemmatized_to_conll_lst(self, conll_lst):
    '''
    '''
    self.different_base = '' #just for testing
    with codecs.open(self.LEMMATIZED_PATH, 'r', 'utf-8') as l_file:
      lemmata_lst = [l.strip('\r\n') for l in l_file.readlines() if '\t' in l]
    i = 0
    for c in conll_lst:
      for t in c['tokens_lst']:
        if t['FORM_NORM_U']!=lemmata_lst[i].split('\t')[0]:
          t['CSTLemma'] = '_'
          t['LEMMA_ATF'] = '_'
        else:
          lemma = lemmata_lst[i].split('\t')[1]
          if '|' in lemma:
            lemma = lemma.split('|')[0]
          t['CSTLemma'] = lemma
          t['LEMMA_ATF'] = self.lemma_to_ATF(lemma, t['FORM_ATF'])
          print(lemma, t['LEMMA_ATF'], t['FORM_ATF'])
          i+=1
    return conll_lst

  def get_lemma_variants(self, lemma):
    '''
    Produce dictionary variants and phonetic variants for lemma.
    '''
    variants_lst = []
    if lemma in lemma_norm_dict.keys():
      variants_lst+=lemma_norm_dict[lemma]
    for v in [lemma]+variants_lst:
      variants_lst+=sylb.produce_variants(
        sylb.unicode_atf_converter(v, 'a>u'))
    variants_lst = [sylb.unicode_atf_converter(l) for l in variants_lst]
    return sorted(set(variants_lst), key=lambda i: variants_lst.index(i))

  def lemma_to_ATF(self, lemma, t_str):
    '''
    Return the ATF segment that corresponds to the lemma.
    '''
    try: 
      sign_list = transliteration(
        t_str, base=False, syllabary_check=False).sign_list
    except AttributeError:
      return '_'
    lemma = ''.join(
      [self.revert_unicode_index(l)['value'] for l in lemma])
    lemma_atf = self.get_lemma_atf(sign_list, lemma)
    if lemma_atf in ['', '_'] and '\t'.join([lemma, t_str, lemma_atf]) \
       not in self.different_base:
      for lv in self.get_lemma_variants(lemma):
        l_atf = self.get_lemma_atf(sign_list, lv)
        if l_atf not in ['', '_']:
          return l_atf
    return lemma_atf

  def get_lemma_atf(self, sign_list, lemma, sign_vars=False):
    '''
    '''
    lemma_atf = []
    prev = ''
    for s in sign_list:
      if 'det' not in s['type']:
        if not sign_vars:
          lemma_atf = self.append_to_lemma_atf(lemma, s, lemma_atf, prev)
          prev = s['value'][0]
        else:
          try:
            entry = sylb.find_entry_by_value(s['value'], s['index'])
            sign_values = entry['values']
            prv = ''
            for s in sign_values:
              lemma_atf = self.append_to_lemma_atf(lemma, s, lemma_atf, prv)
              prv = s['value'][0]
          except ValueError:
            pass
    if not '-'.join(lemma_atf) and not sign_vars:
      return self.get_lemma_atf(sign_list, lemma, sign_vars=True)
    return '-'.join(lemma_atf)

  def append_to_lemma_atf(self, lemma, s, lemma_atf, prev):
    '''
    '''
    value = s['value']
    if 'emendation' in s.keys():
      if s['emendation']:
        value = s['emendation']
    if value in lemma or (len(lemma)<len(value) and lemma in value) \
       or (prev and \
           [s for s in sylb.produce_variants(prev+value[0]) if s in lemma]):
      # ???? NOT CERTAIN
      if prev and prev+value[0] in lemma:
        print('!!!!', prev+value[0], value, lemma, s, lemma_atf)
      index = s['index']
      if index==1:
        index = ''
      lemma_atf.append('%s%s' %(s['value'], index))
    return lemma_atf
  
  def revert_unicode_index(self, u_sign):
    '''
    '''
    vow_lst = ['a', 'A', 'e', 'E', 'i', 'I', 'u', 'U']
    i =0
    if not [u for u in u_sign if ord(u)>1000]:
      return {'value': u_sign, 'index': 1}
    while i < len(u_sign):
      n = ord(u_sign[i])
      if n > 1000:
        vow_i = int(str(n)[0])-1
        index = int(str(n)[2:])
        return {'value': u_sign[:i]+vow_lst[vow_i]+u_sign[i+1:],
                'index': index}
      i+=1

  def lemmatize(self, flex_patterns, dictionary, input_file, output_file):
    '''
    '''
    cmd = [
      self.CSTLEMMA_PATH, '-L', '-d%s' %(dictionary), '-f', flex_patterns,
      '-i', input_file, '-X-', '-H0', '-u', '-t-', '-o', output_file]
    sp.run(cmd, print_stdout=True)

  def create_dictionary(self, input_file, output_file, cwd=''):
    '''
    '''
    cmd = [
      self.CSTLEMMA_PATH,'-D', '-cFBT', '-i', input_file, '-o', output_file]
    sp.run(cmd, cwd)

  def create_flex_patterns(self, input_file, cwd='', classes=False):
    '''
    '''
    if classes==True:
      cmd = [self.AFFIXTRAIN_PATH, '-i', input_file, '-n', 'FBT']
    else:
      cmd = [self.AFFIXTRAIN_PATH, '-i', input_file, '-n', 'FL']
    sp.run(cmd, cwd)

# to lemmatize with variants use:
##  cmd = [self.CSTLEMMA_PATH,'-L', #'-c$w\t$b1[[$b?]~1$B]\t$t\n'
##         '-d%s' %(dictionary), '-f', flex_patterns, '-i',
##         input_file, '-X-', '-t-', '-o', output_file]
