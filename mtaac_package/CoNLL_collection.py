import math
from random import sample
from .common_functions import *
from .CoNLL_file_parser import conll_file
from .lemmatizer import CSTLemma
from .ATF_transliteration_parser import transliteration

lmzr = CSTLemma()

class conll_collection(common_functions):
  '''
  The class collects .conll files and exports the data for training.
  Use 'conll_collection.json' to load processed data.
  ''' 
  
  def __init__(self, source_root, json_filename='conll_collection.json',
               lemmatize=True):

    self.conll_lst = []
    self.legends = []
    self.set_paths(source_root, json_filename)
    self.load_collection_from_json()
    self.collect_files()
    if lemmatize:
      self.conll_lst = lmzr.lemmatize_conll_lst(self.conll_lst)
      self.dump_collection_to_json()
##    self.split_and_export()

  def split_and_export(self):
    '''
    '''
    #self.make_tokens_dict()
    self.random_plus_corpus_split()
    self.export_lemmatization_data()

  def set_paths(self, source_root, json_filename):
    '''
    '''
    self.source_root = os.path.abspath(source_root)
    self.lemmatization_data_path = os.path.join(self.source_root, '..',
                                                'lemmatization_data')
    self.json_path = os.path.join(self.source_root, json_filename)
  
  #---/ Load data /------------------------------------------------------------
  #
##  def load_tokens_dict(self):
##    with open('tokens_dict.json') as data_file:
##      return json.load(data_file)
##
  def load_collection_from_json(self, asObjects=False):
    '''
    By default, returns a list of dictionaries.
    Use asObjects=True to return a list of objects.
    '''
    if os.path.exists(self.json_path):
      if not asObjects:
        self.conll_lst+=self.load_json(self.json_path)
      else:
        self.conll_lst+=[
          conll_file(data_dict=d) for d in self.load_json(self.json_path)]
##      for c in self.conll_lst:
##        print('loading', c['filename'], 'from json')

  def dump_collection_to_json(self):
    '''
    '''
##    data_lst = [c.dict_output() for c in self.conll_lst]
##    self.dump(json.dumps(data_lst), self.json_path)
    self.dump(json.dumps(self.conll_lst), self.json_path)
    
  def get_conll_filenames(self):
    '''
    '''
    paths_lst = []
    processed_conll_files = [c['filename'] for c in self.conll_lst]
    filepaths = self.get_filepaths(self.source_root, endswith='.conll')
    return [f for f in filepaths if f[1] not in processed_conll_files]
    
  def collect_files(self):
    '''
    '''
    for args in self.get_conll_filenames():
      self.collect_file(*args)
    #self.mp_run(self.collect_file, self.get_conll_filenames())
    #self.dump(json.dumps(sylb.norm_dict), 'norm_dict.json')

  def collect_file(self, dirpath, filename):
    '''
    '''
    print('loading', filename, 'from conll')
    path = Path(os.path.join(self.source_root, dirpath, filename))
    c = conll_file(path)
    self.conll_lst.append(c.dict_output())
    if 'legend' in c.info_dict.keys():
      if c.info_dict['legend'] not in self.legends:
        self.legends.append(c.info_dict['legend'])
    self.dump_collection_to_json()

  #---/ Split data /-----------------------------------------------------------
  #
  def random_plus_corpus_split(self):
    '''
    Random division to train, test (gold), and develop subcorpora.
    Returns a list of dictionaries with the following format:
      - name: group's name ('train', 'test', or 'develop'),
      - percent: percent of the corpus (int),
      - items: quantity of randomly defined entries,
      - pre (optional): quantity of predefined entries,
      - and some others.
    '''
    whole = 0
    entries_gold = []
    entries_lst = []
    for c in sample(self.conll_lst, len(self.conll_lst)):
      for t in c['tokens_lst']:
        if '_' not in self.make_tokens_lst(t):
          if c['corpus']=='cdli_ur3':
            entries_gold.append(t)
          else:
            entries_lst.append(t)
          whole+=1
    print('Total valid tokens:', whole)
    parts_lst = [
      {'name': 'train', 'percent': 80},
      {'name': 'test', 'percent': 10, 'pre': len(entries_gold)},
      {'name': 'develop', 'percent': 10}]
    parts_lst = self.percentage_to_items(parts_lst, whole)
    prev = 0
    for el in parts_lst:
      el['entries'] = entries_lst[prev:prev+el['items']]
      prev+=el['items']
      if el['name']=='test':
        el['entries']+=entries_gold
    self.parts_lst = parts_lst

  def percentage_to_items(self, parts_lst, whole):
    '''
    Subfunction of `self.random_plus_corpus_split()`.
    Updates `parts_lst` to include the number of entries
    that matches given percent.
    Note that the `pre` argument's value is deducted from  
    entries in order to leave space for the predefined Gold
    entries.
    '''
    ints = 0
    for el in parts_lst:
      (el['int'], el['dec']) = math.modf((el['percent']*whole)/100.0)
      ints+=el['int']
    for el in sorted(parts_lst, key=lambda x: -x['int']):
      if ints > 0:
        el['items'] = int(el['dec']+1)
        ints-=1
      else:
        el['items'] = int(el['dec'])
      if 'pre' in el.keys():
        el['items']-=el['pre']
    for p in parts_lst:
      pre = 0
      i = p['items']
      if 'pre' in p.keys():
        pre = p['pre']
      print('Corpus split %s items: %s' %(p['name'], i+pre))
      if pre > 0:
        print('\tOf them predefined: %s' %pre)
    return parts_lst

  #---/ Export lemmatization data /--------------------------------------------
  #
  def export_lemmatization_data(self):
    '''
    '''
    norm_suffix_set_dict = {'': 'norm', '_U': 'norm_u', '_SD': 's_and_d'}
    export_strings_dict = {}
    for part in self.parts_lst:
      if part['name'] in ['train', 'test']:
        for t in part['entries']:
          for norm_type in norm_suffix_set_dict.keys():
            set_suffix = norm_suffix_set_dict[norm_type]
            export_string_dict = self.make_sets(
              t,
              norm_type,
              part,
              set_suffix,
              export_strings_dict)
    for k in export_strings_dict:
      self.dump(
        export_strings_dict[k],
        os.path.join(self.lemmatization_data_path, k))

  def make_sets(self, t, norm_type, part, set_suffix, export_strings_dict):
    '''
    Intermediary function:
      `self.export_lemmatization_data` <> `self.populate_string_dict`
    '''
    tokens_lst = self.make_tokens_lst(t, norm_type)
    if part['name']=='test':
      export_string_dict = self.make_test_set(
        part, set_suffix, tokens_lst, export_strings_dict)
    else:
      name = '%sing_data_%s' %(part['name'], set_suffix)
      export_strings_dict = self.make_train_set(
        part, set_suffix, tokens_lst, export_strings_dict)

  def make_tokens_lst(self, t, norm_type=''):
    '''
    Make token fields list for lemmatization training.
    '''
    if norm_type!='_SD': 
      tokens_lst =  [
        t['FORM_NORM%s' %norm_type],
        t['BASE_NORM%s' %norm_type],
        t['EPOS']]
    elif norm_type=='_SD':
      first_sign = '_'
      tw = transliteration(t['FORM'], syllabary_check=False)
      if tw.defective==False:
        first_sign = tw.first_sign
      tokens_lst = [
        t['FORM_NORM_SD'],
        t['BASE_NORM'],
        t['EPOS'],
        t['FORM_NORM'],
        first_sign]
    return tokens_lst

  def make_train_set(self, part, set_suffix, tokens_lst, export_strings_dict):
    '''
    Make train sets for lemmatization.
    Intermediary function:
      `self.export_lemmatization_data` <> `self.populate_string_dict`
    '''
    name = '%sing_data_%s' %(part['name'], set_suffix)
    return self.populate_string_dict(
      export_strings_dict, name, tokens_lst)

  def make_test_set(self, part, set_suffix, tokens_lst, export_strings_dict):
    '''
    Make test sets for lemmatization.
    Intermediary function:
      `self.export_lemmatization_data` <> self.populate_string_dict``
    '''
    for f in ['', '_full', '_stem']:
      name = '%sing%s_data_%s' %(part['name'], f, set_suffix)
      if f=='_full':
        test_tokens_lst = tokens_lst
      elif f=='_stem':
        test_tokens_lst = [tokens_lst[1]] #BASE
      else:
        test_tokens_lst = [tokens_lst[0]] #FORM
      export_strings_dict = self.populate_string_dict(
        export_strings_dict, name, test_tokens_lst)
    return export_strings_dict

  def populate_string_dict(self, export_strings_dict, name, tokens_lst):
    '''
    Write to dict of strings and sets (filenames):
      key: set (filename)
      value: string
    '''
    write = '\t'.join(tokens_lst)+'\n'
    if name in export_strings_dict.keys():
      export_strings_dict[name]+=write
    else:
      export_strings_dict[name] = write
    return export_strings_dict

##  def make_tokens_dict(self, suppletion=False):
##
##    # REWRITE WITH REGARD TO CORPORA SPLIT:
##    # 1. 'primary' must die
##    # 2. split:
##    # etcsl + etcsri for training and evaluation
##    # cdli_ur3 for eval. only    
##    
##    self.tokens_dict = {}
##    exx_counter = 0
##    for c in self.conll_lst:
##      corpus = c.corpus
##      for t in c.tokens_lst:
##        if suppletion==False and t['BASE'][1] not in t['WORD'][0]:
##          pass
##        else:
##          t_key = '\t'.join([t['WORD'][0], t['BASE'][1], t['POS']])
##          #if t_key not in list(self.tokens_dict.keys()):
##          self.tokens_dict[t_key] = t
##          self.tokens_dict[t_key]['COUNT'] = 0
##          self.tokens_dict[t_key]['EX_CLASS'] = 'train'
##          self.tokens_dict[t_key]['CORPUS'] = corpus
##          if exx_counter % 8==0:
##            self.tokens_dict[t_key]['EX_CLASS'] = 'develop'
##          if exx_counter % 9==0:
##            self.tokens_dict[t_key]['EX_CLASS'] = 'test'
##          exx_counter+=1
##          self.tokens_dict[t_key]['COUNT']+=1
##          if self.tokens_dict[t_key]['CORPUS']!=corpus:
##            self.tokens_dict[t_key]['CORPUS']=corpus
##
##    self.dump(json.dumps(self.tokens_dict), 'tokens_dict.json')

if __name__ == '__main__':
  pass

