import codecs
from .common_functions import *
from .ATF_transliteration_parser import transliteration, sylb
from .morph_annotation import *

'''
>>> CDLI <<<

1. ID

2. FORM: CDLI-ATF transliteration.
    E.g. 'nam-szusz3-ta'.
3. SEGM: normalization[sense][-omitted morphemes]-spelled morphemes.
    E.g. 'namszusz[cattle-management][-ak]-ta'
4. XPOSTAG: morph. annotation & segmentation, no labels.
     E.g. 'N.GEN.ABL', 'PN' etc.
5. HEAD: parent element or zero.
    (empty).
6. DEPREL: relation type.
    (empty).
7. MISC: comments.
    (empty).

for syntax: configure_str_output(['ID_NUM', 'FORM', 'SEGM', 'MORPH2', 'HEAD', 'DEPREL', 'MISC'])

>>> ORACC <<<

2. WORD: ORACC-ATF transliteration.
    E.g. 'ul-li₂-a-ta'.
3. BASE: ORACC-ATF transliteration, base only
    E.g. 'ul-li₂'.
4. CF: base normalization, named entites start with capital.
    E.g. 'ul', 'Enlil'
5. EPOS: Part of speech of named entites abbreviation.
    E.g. 'V/t', 'N', 'DN', 'RN' etc.
6. FORM: WORD with elements of morph. annotation
    E.g. 'kiš\gen\erg'.
7. GW: translation.
    E.g. 'person', '1' (for named entites).
8. LANG: Language or other abberviation.
    E.g. 'sux'.
9. MORPH: Morphological segmentation with labels and morphemes.
    E.g. 'N1=kiš.N5=ak.N5=ø'.
10. MORPH2: Morphological segmentation with labels and abbreviations.
    E.g. 'N1=STEM.N5=GEN.N5=ABS'
11. NORM: MORPH without labels.
    E.g. 'kiš.ak.ø'.
12. EPOS: Same as GW.
    E.g. 'V/t', 'N', 'DN', 'RN' etc.
13. SENSE: Dict. entry, explanation.
    E.g. '2nd king of dynasty of Agade', 'king', '1'.

# Local: 'ID', 'FORM', 'BASE', 'SENSE', 'MORPH2', 'POS', 'SEGM'
# Lemmatizer additional: 'CSTLemma', LEMMA_ATF
#
# ACTIONS:
#
# ID:
#     Transformations:
#       1. ID_NUM (for all): replace with plain numeration (+)
#
# FORM (WORD in ORACC):
#     Transformations: 
#       1. FORM_ATF: escape unicode, use same symbols (+)
#       2. FORM_NORM: list with normalizations (3 types) (+)
# 
# BASE (see SEGM in CDLI):
#     Transformations: 
#       1. CDLI: Extract data, create field (+)
#
# SENSE (see SEGM in CDLI):
#     Transformations: 
#       1. CDLI: Extract data, create field (+)
#
# MORPH2 (see XPOSTAG in CDLI)
#       1. CDLI: add labels, create field (+)
#
# XPOSTAG (see MORPH2 & EPOS in ORACC)
#       1. ORACC: Extract data, create field (?)
'''
#
#---/ Auxiliary instances for morph. annotation /------------------------------
#
mc = morph_converter()
tg = tags()
#
#---/ CoNLL file /-------------------------------------------------------------
#
class conll_file(common_functions):
  '''
  Class for processing CoNLL data.
  '''
  COLUMNS_CDLI = [
    'ID', 'FORM', 'SEGM', 'XPOSTAG', 'HEAD', 'DEPREL', 'MISC']
  COLUMNS_ORACC = [
    'ID', 'WORD', 'BASE', 'CF', 'EPOS', 'FORM', 'GW', 'LANG', 'MORPH',
    'MORPH2', 'NORM', 'POS', 'SENSE']
  COLUMNS_ETCSL = ['ID', 'WORD', 'BASE', 'POS', 'SENSE']
  corpus_conventions = {
    'cdli': 'ORACC',
    'etcsl': 'ETCSL',
    'etcsri': 'ORACC'
    }

  def __init__(self, path='', conll_str='', corpus='', data_dict={}):
    '''
    Pass either ´path´ or both ´conll_str´ and ´corpus´.
    Alternatively, load data directly from ´data_dict´.
    '''
    self.tags = tags()
    self.tokens_lst = []
    self.info_dict = {}
    self.info_lst = []
    self.filename = ''
    self.output_columns = []
    self.override_columns = []
    if data_dict:
      self.load_from_dict(data_dict)
    elif path or conll_str:
      self.load_from_path_or_str(path, conll_str, corpus)

  #---/ Loading data /---------------------------------------------------------
  #
  def load_from_dict(self, data_dict):
    '''
    Load and parse data from data_dict.
    The following data are included:
      ´self.tokens_lst´
      ´self.info_dict´
      ´self.info_lst´
      ´self.corpus´
      ´self.convention´
      ´self.filename´ (if path given)
    '''
    for key in data_dict.keys():
      setattr(self, key, data_dict[key])
    # remove:
##    for t in self.tokens_lst:
##      self.make_FORM_fields(t)
##      print(t['FORM_ATF'], ['FORM_NORM_SD'])
    
  def load_from_path_or_str(self, path, conll_str, corpus):
    '''
    Load and parse data from path or CoNLL string.
    '''
    if not corpus:
      corpus = 'cdli'
    self.line_ID = '' # ID prefix for ETCSL, from commented lines
    if path:
      self.filename = os.path.basename(path)
      self.correct_format(path)
      else:
        # try to get if from PATH
        self.corpus = None
        for c in self.corpus_conventions.keys():
          if c in str(path):
            self.corpus = c
            self.convention = self.corpus_conventions[c]
            break
      if not self.corpus:
        self.corpus = corpus
        self.convention = self.corpus_conventions[corpus]
      with codecs.open(path, 'r', 'utf-8') as f:
        self.data = f.read()
    elif conll_str:
      self.data = conll_str
      self.corpus = corpus
      self.convention = self.corpus_conventions[corpus]
    self.process_data()
    
  def process_data(self):
    '''
    Process the CoNLL data:
      1. Parse
      2. Create missing fields
      3. Adjust POS conventions.
      4. Configure string output.
    '''
    self.parse_conll()
    if 'legend' not in self.info_dict.keys():
      self.info_dict['legend'] = self.COLUMNS_ETCSL
    self.make_missing_fields()
    self.make_adjustments()
    self.configure_str_output()
  
  #---/ Primary parsing /------------------------------------------------------
  #
  def parse_conll(self):
    '''
    Main function to parse CoNLL tokens and meta.
    '''
    for l in self.data.splitlines():
      if l:
        if l[0] not in ['#', ' ']:
          if ('lines ' or 'line ') in l:
            # Cases when (line) comments are does not have #.
            pass
          else:
            token_lst = l.split('\t')
            if ' ' in token_lst[0][:-1]:
              token_lst = token_lst[0].split(' ') + token_lst[1:]
            self.add_token(token_lst)
        elif l[0]=='#' and '.' not in l:
          self.add_meta(l)
        elif '.' in l:
          # ID prefix for ETCSL, from commented lines.
          self.line_ID = l.strip('# ')

  def add_meta(self, l):
    '''
    Function to parse meta lines: text ID and column names (legend).
    '''
    self.info_lst.append(l)
    if ': ' in l:
      info_lst = l.strip('# ').split(': ')
      key = info_lst[0].strip(' ')
      value = ': '.join(info_lst[1:]).strip(' ')
      self.info_dict[key] = value
    else:
      l = l.strip('# ')
      if l:
        if ('WORD' in l or 'FORM' in l) and 'ID' in l:
          self.info_dict['legend'] = [col for col in l.split('\t')
                                      if col.strip('_," ')]
        else:
          self.info_dict['title'] = l

  def add_token(self, token_lst):
    '''
    Function to parse token lines.
    Create dict. for token, with legend columns as keys.
      1. Add legend if missing (for ETCSL).
      2. Arrange columns.
    '''
    legend = self.info_dict['legend']
    token_dict = {}
    i = 0
    while i < len(legend):
      try:
        value = token_lst[i].strip('_ ')
        if not value.strip('[]_, '):
          value = '_'
        elif legend[i]=='ID' and self.line_ID:
          value = '%s.%s' %(self.line_ID, value)
        token_dict[legend[i]] = value
      except IndexError:
        token_dict[legend[i]] = '_'
      i+=1
    self.tokens_lst.append(token_dict)

  #---/ Make basic fields /----------------------------------------------------
  #
  def make_missing_fields(self):
    '''
    Add basic fields commonly used fields, when missing.
    These are namely:
      ID_NUM: plain numeration ID.
      BASE: lemma in ASCII ATF.
      SENSE: sense / translation.
      POS: part of speech.
      EPOS: part of speech / named entity.
      MORPH2: ORACC-style morph. annotation with labels.
      XPOSTAG: MTAAC-style morph. annotation with POS / named entity.
      FORM: Raw ATF transliteration (same as WORD).
      FORM_ATF: transliteration in ASCII ATF.
      FORM_NORM: Plain normalization for FORM, indicies omitted.
      FORM_NORM_U: Normalization for FORM, escaped indicies+vow as unicode.
      FORM_NORM_SD: Normalization for FORM, first sign & determinative.
      BASE_NORM: Plain normalization for BASE, indicies omitted.
      BASE_NORM_U: Normalization for BASE, escaped indicies+vow as unicode.
      BASE_NORM_SD: Normalization for BASE, first sign & determinative.
      BASE_NORM_BD: Normalization for BASE, base & determinative.
      UNICODE: Glyphs as Unicode chars.
    '''
    fields_minimun_dict = {
      'ID_NUM': self.make_field_ID_NUM,
      'BASE': self.make_fields_BASE_and_SENSE,
      'SENSE': self.make_fields_BASE_and_SENSE,
      'MORPH2': self.make_field_MORPH2,
      'EPOS': self.make_field_EPOS,
      'POS': self.make_field_POS,
      'XPOSTAG': self.make_field_XPOSTAG,
      'FORM': self.make_FORM_fields,
      'FORM_ATF': self.make_FORM_fields,
      'FORM_NORM': self.make_FORM_fields,
      'FORM_NORM_U': self.make_FORM_fields,
      'FORM_NORM_SD': self.make_FORM_fields,
      'BASE_NORM': self.make_BASE_fields,
      'BASE_NORM_U': self.make_BASE_fields,
      'BASE_NORM_SD': self.make_BASE_fields,
      'BASE_NORM_BD': self.make_BASE_fields,
      'UNICODE': self.make_unicode_fields
      }
    for field in fields_minimun_dict.keys():
      if field not in self.info_dict['legend']:
        for t in self.tokens_lst:
          if not self.are_fields_valid(t, field):
            fields_minimun_dict[field](t)

  def are_fields_valid(self, token_dict, fields_lst):
    '''
    Check if fields in token_dict are valid:
    key in dict. and value is not '_'.
    '''
    for field in fields_lst:
      if field not in token_dict.keys():
        return False
      elif token_dict[field] in ['_', '']:
        return False
    return True

  def make_field_ID_NUM(self, token_dict):
    '''
    Add ID_NUM field with plain numeration. 
    '''
    token_dict['ID_NUM'] = str(self.tokens_lst.index(token_dict)+1)

  def make_fields_BASE_and_SENSE(self, token_dict):
    '''
    Add field BASE for lemma, SENSE for translation.
    '''
    if self.are_fields_valid(token_dict, ['SEGM']):
      for s in token_dict['SEGM'].split('-'):
        if '[' in s and ']' in s:
          token_dict['BASE'] = s.split('[')[0]
          token_dict['SENSE'] = s.split('[')[1][:-1]
          return None
    self.make_empty_fields(token_dict, ['SENSE', 'BASE'])

    # TODO NOTE: make sure this is a proper normalization

  def make_field_MORPH2(self, token_dict):
    '''
    Add MORPH2 field for ORACC-style annotation.
    Convert MTAAC-style annotation to ORACC.
    '''
    if self.are_fields_valid(token_dict, ['XPOSTAG']):
      [token_dict['MORPH2'], token_dict['EPOS']] = \
                             mc.MTAAC2ORACC(token_dict['XPOSTAG'])
      return None
    self.make_empty_fields(token_dict, ['XPOSTAG'])

  def make_field_EPOS(self, token_dict):
    '''
    Add EPOS field for ORACC / MTAAC parts of speech or named entities.
    '''
    if self.are_fields_valid(token_dict, ['POS']):
      token_dict['EPOS'] = token_dict['POS']
      return None
    self.make_empty_fields(token_dict, ['EPOS'])

  def make_field_POS(self, token_dict):
    '''
    Add POS field for ORACC / MTAAC parts of speech.
    '''
    if self.are_fields_valid(token_dict, ['EPOS']):
      if tg.is_named_entity(token_dict['EPOS']):
        token_dict['POS'] = 'N' #ToDo: ajust to corpus? 
      else:
        token_dict['POS'] = token_dict['EPOS']
      return None
    self.make_empty_fields(token_dict, ['POS'])

  def make_field_XPOSTAG(self, token_dict):
    '''
    Add XPOSTAG field for MTAAC-style annotation.
    Convert ORACC-style annotation to MTAAC.
    '''
    if self.are_fields_valid(token_dict, ['POS', 'MORPH2']):
      token_dict['XPOSTAG'] = mc.ORACC2MTAAC(
        token_dict['MORPH2'], token_dict['POS'])
      return None
    self.make_empty_fields(token_dict, ['MORPH2'])

  def make_FORM_fields(self, token_dict):
    '''
    Add the following FORM_ fields:
      (1. FORM: Raw FORM, copy of WORD field for ORACC).
      2. FORM_ATF: field with raw FORM or WORD (ORACC), chars unified.
      3. FORM_NORM: Plain normalization for FORM, indicies omitted.
      4. FORM_NORM_U: Normalization for FORM, escaped indicies+vow as unicode.
      5. FORM_NORM_SD: Normalization for FORM, first sign & determinative.
    '''
    if not self.are_fields_valid(token_dict, ['FORM']) and \
       self.are_fields_valid(token_dict, ['WORD']):
      token_dict['FORM'] = token_dict['WORD']
    tw = transliteration(token_dict['FORM'])
    if tw.defective==False:
      token_dict['FORM_ATF'] = tw.base_translit
      token_dict['FORM_NORM'] = tw.normalization
      token_dict['FORM_NORM_U'] = tw.normalization_u
      token_dict['FORM_NORM_SD'] = tw.sign_and_det_normalization
      if 'FORM' not in token_dict.keys():
        token_dict['FORM'] = tw.base_translit
    else:
      self.make_empty_fields(
        token_dict,
        ['FORM', 'FORM_ATF', 'FORM_NORM', 'FORM_NORM_U', 'FORM_NORM_SD'])

  def make_BASE_fields(self, token_dict):
    '''
    Add the following BASE_ fields:
      1. BASE_NORM: Plain normalization for BASE.
      2. BASE_NORM_U: Normalization for BASE, escaped indicies+vow as unicode.
      3. BASE_NORM_SD: Normalization for BASE, first sign & determinative.
      4. BASE_NORM_BD: Normalization for BASE, base & determinative.
    '''
    tw = transliteration(token_dict['BASE'], syllabary_check=False)
    if tw.defective==False:
      for k, v in [
        ('BASE_NORM', tw.normalization),
        ('BASE_NORM_U', tw.normalization_u),
        ('BASE_NORM_SD', tw.sign_and_det_normalization)]:
        if v:
          token_dict[k] = v
        else:
          self.make_empty_fields(token_dict,[k])
        token_dict['BASE_NORM_BD'] = self.get_BASE_NORM_BD_value(token_dict)
    else:
      self.make_empty_fields(
        token_dict, ['BASE_NORM', 'BASE_NORM_U',
                     'BASE_NORM_SD', 'BASE_NORM_BD'])

  def get_BASE_NORM_BD_value(self, token_dict):
    '''
    Get value for 'BASE_NORM_BD':
    Normalization for BASE, base & determinative.
    Subfunction of ´self.make_BASE_fields()´
    '''
    tw = transliteration(token_dict['FORM_ATF'])
    if token_dict['BASE_NORM']=='_' or tw.defective:
      return '_'
    return '-'.join(
      [token_dict['BASE_NORM']]+
      [s['value'] for s in tw.sign_list
       if s['type']=='det']
      )

  def make_unicode_fields(self, token_dict):
    '''
    '''
    print(token_dict)

  def make_empty_fields(self, token_dict, fields_lst):
    '''
    Add fields from ´fields_lst´ to ´token_dict´ with empty placeholers.
    '''
    for k in fields_lst:
      if k not in token_dict.keys():
        token_dict[k] = '_'
  
  #---/ Adjustments /---------------------------------------------------------
  #
  def make_adjustments(self):
    '''
    Adjust and unify certain data:
      1. Adjust POS conventions.
      2. Unify characters in BASE.
    '''
    for t in self.tokens_lst:
      self.adjust_POS_conventions(t)
      self.unify_chars(t)
    
  def adjust_POS_conventions(self, token_dict):
    '''
    Adjust POS conventions.
    '''
    for p in ['EPOS', 'POS']:
      token_dict[p] = tg.adjust_POS(tag=token_dict[p],
                                    src_convention=self.convention)

  def unify_chars(self, token_dict):
    '''
    Unify chars in BASE.
    Make BASE lowercase. 
    '''
    token_dict['BASE'] = self.standardize_translit(token_dict['BASE']).lower()

  #---/ Output /---------------------------------------------------------------
  #
  def dict_output(self):
    '''
    The following data are included:
      ´self.tokens_lst´
      ´self.info_dict´
      ´self.info_lst´
      ´self.corpus´
      ´self.convention´
      ´self.filename´ (if path given)
    '''
    keys_lst = ['tokens_lst', 'info_dict', 'corpus', 'convention', 'info_lst',
                'filename']
    data_dict = {}
    for k in keys_lst:
      data_dict[k] = getattr(self, k)
    return data_dict
    
  def __str__(self):
    '''
    Return CoNLL string.
    Use ´self.configure_str_output()´ to customize output.
    '''
    if not self.output_columns:
      self.configure_str_output()
    conll_str = '%s\n# %s\n' \
                %(self.info_lst[0], '\t'.join(self.override_columns))
    for t in self.tokens_lst:
      conll_str+=self.make_token_str_row(t)
    return conll_str[:-1]
  
  def configure_str_output(self, columns=[], override={}):
    '''
    Configure ´self.__str__()´ output.
    Use ´override´ to override col. name.
    '''
    if not columns:
      columns = self.COLUMNS_CDLI
    self.output_columns = columns
    self.override_columns = [
      override[c] if c in override.keys() else c for c in columns]

  def make_token_str_row(self, token_dict):
    '''
    Convert token_dict to CoNLL row.
    Subfunction of ´self.__str__()´.
    '''
    conll_row_lst = []
    for col in self.output_columns:
      if col in token_dict.keys():
        conll_row_lst.append(token_dict[col])
      else:
        conll_row_lst.append('_')
    return '\t'.join(conll_row_lst)+'\n'
  
  #----/ Merge columns from CoNLL string /-------------------------------------
  #
  def merge_columns_from_conll_str(self, conll_str, columns_lst,
                                   key_column=''):
    '''
    Add values from another CoNLL string of the same text. Values to be merged:
    Added or overwritten.
    'conll_str' - CoNLL as string.
    'columns_lst'- list of column names that have to be merged. pass strings
                    and tuples: (col_from, col_to) to override column names.
    'key_column' - name of column that serves as key for merging. #not used
    '''
    c = conll_file(conll_str=conll_str)
    i = 0
    while i < len(c.tokens_lst):
      for column in columns_lst:
        if type(column)==tuple:
          col_from, col_to = column
        else:
          col_from = col_to = column
        self.tokens_lst[i][col_to] = c.tokens_lst[i][col_from]
      i+=1
  
  #----/ Checks and corrections /----------------------------------------------
  #
  def correct_format(self, path):
    '''
    For each file from a list of IDs in dir_path (default is self.PROCESSED):
    1. run ´self.csv2tsv()´: convert CSV to TSV. 
    2. Run mpat with -f switch to correct the file format:
      2a. remove extra columns and
      2b. add underscores in empty cells.
      2c. Then replace the original with it.
    '''
    if os.path.basename(path)[0]=='c':
      # Do not apply to ETCSL, e.g. 'c111.conll'
      return None
    if self.correct_unicode(path):
      print('Corrected invalid unicode: %s' %path)
    if self.csv2tsv(path):
      print('Corrected CSV: %s' %path)

  def correct_unicode(self, path):
    '''
    Check if valid Unicode, convert from ANSI, if needed.
    Subfunction of ´self.correct_format()´.
    '''
    with codecs.open(path, 'r', 'utf-8') as f:
      try:
        conll_lines = f.readlines()
        return False
      except UnicodeDecodeError:
        pass
    with codecs.open(path, 'r', 'windows-1252') as f:
      f_str = str(f.read()).replace('', "'")
    self.dump(f_str, path)      
    return True
      
  def csv2tsv(self, path):
    '''
    WARNING: This function clears the content of the last 3 columns.
    Convert CST to TSV.
    Also:
      - Remove extra tabs rests.
      - Insert '_' to empty fields.
    Subfunction of ´self.correct_format()´.
    '''
    with codecs.open(path, 'r', 'utf-8') as f:
      conll_lines = list(f.readlines())
      if ',' not in ''.join(conll_lines):
        return False
      conll_lines = [l.strip('\r\n') for l in conll_lines]
      if conll_lines==[]:
        return False
    tsv_str = ''
    for csv_row in conll_lines:
      if '#' in csv_row:
        csv_row = csv_row.strip(',')
      else:
        columns = []
        for cell in [c.strip('\t_ ') for c in csv_row.split(',')[:4]]:
          if cell=='':
            cell = '_'
          columns.append(cell)
        csv_row = ','.join(columns+['_' for i in range(0,3)])
      tsv_row = csv_row.replace(',', '\t')
      if tsv_row.strip('\t_ ')!='':
        tsv_str+=tsv_row+'\n'
    self.dump(tsv_str[:-1], path)
    return True

if __name__ == '__main__':
  pass
