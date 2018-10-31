from mtaac_package.common_functions import *
from mtaac_package.CoNLL_file_parser import conll_file

class conll_collection(common_functions):
  '''
  The class collects .conll files and exports the data for training.
  '''
  
  def __init__(self, source_root):
    '''
    '''
    self.source_root = os.path.abspath(source_root)
    self.conll_lst = []
    self.collect_files()
    #self.make_tokens_dict()
    self.random_plus_corpus_split()
    self.export_data()

##  def load_tokens_dict(self):
##    with open('tokens_dict.json') as data_file:
##      return json.load(data_file)

  def collect_files(self):
    '''
    '''
    self.legends = []
    for dirpath, dirnames, filenames in os.walk(self.source_root):
      for filename in [f for f in filenames if f.endswith('.conll')]:
        path = Path(os.path.join(self.source_root, dirpath, filename))
        c = conll_file(path)
        self.conll_lst.append(c)
        if 'legend' in c.info_dict.keys():
          if c.info_dict['legend'] not in self.legends:
            self.legends.append(c.info_dict['legend'])
    print('Total CoNLL files:', len(self.conll_lst))
    self.dump(json.dumps(sylb.norm_dict), 'norm_dict.json')

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
      for t in c.tokens_lst:
        if c.corpus=='cdli_ur3':
          entries_gold.append(t)
        else:
          entries_lst.append(t)
        whole+=1
    print('Total tokens:', whole)
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

  def export_data(self):
    '''
    '''
    sets_lst = ['norm', 'norm_u', 's_and_d']
    export_strings_dict = {}
    for part in self.parts_lst:
      if part['name'] in ['train', 'test']:
        for t in part['entries']:
          for i in range(0, 3):
            temp_t_dict = {}
            if part['name']=='train':
              name = '%sing_data_%s' %(part['name'], sets_lst[i])
              tokens_lst = [t['WORD'][i], t['BASE'][i], t['POS']]
              export_strings_dict = self.populate_string_dict(
                export_strings_dict, name, tokens_lst)
            elif part['name']=='test':
              for f in ['', '_full', '_stem']:
                name = '%sing%s_data_%s' %(part['name'], f, sets_lst[i])
                if f=='_full':
                  tokens_lst = [t['WORD'][i], t['BASE'][i], t['POS']]
                elif f=='_stem':
                  tokens_lst = [t['BASE'][i]]
                else:
                  tokens_lst = [t['WORD'][i]]
                export_strings_dict = self.populate_string_dict(
                  export_strings_dict, name, tokens_lst)
    for k in export_strings_dict:
      self.dump(export_strings_dict[k], k)

  def populate_string_dict(self, export_strings_dict, name, tokens_lst):
    '''
    '''
    write = '\t'.join(tokens_lst)+'\n'
    if name in export_strings_dict.keys():
      export_strings_dict[name]+=write
    else:
      export_strings_dict[name] = write
    return export_strings_dict

if __name__ == '__main__':
  a = conll_collection(source_root='conll_source')
