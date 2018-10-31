from mtaac_package.common_functions import *

#
#===/ DESCRIPTION /============================================================
#
'''
This contains the `tags` class.
for managing tags order in dict. lists: ORACC, ETCSL, and UD.
* Main functions:
  - `convert()` to switch between conventions for abbreviations.
    values or the `source` and `target` arguments
    can be 'ORACC', 'ETCSL', or 'UD'.
* Datasets: See below.

This contains the `morph_converter` class.
Use to switch between conventions of annotations.
* Main functions:
  - MTAAC > ORACC: `self.MTAAC2ORACC()` with annotation str as argument.
* Datasets: See below.
* TODO:
  - (if needed:) integrate `tags` (above) here.
  - (if needed:) add ORACC > MTAAC (or move functionality here from elsewhere).
'''
#
#===/ DATASETS: ORACC morphology /=============================================
#
'''
* Source: http://oracc.museum.upenn.edu/etcsri/parsing/index.html
* Location:
  Kept as JSON in /json/ with prefix 'ORACC_morph_annotation_'.
  See `datasets_lst` and `load_json_sets` params in class
  `morph_converter` below.
* Transliteration convention: MTAAC
* Abbreviations:
  N, V, and NV stand respectively for nominal form,
  verbal finite form, and verbal non-finite form.
* Comments:
  Double vowels stand for long vowel.
'''
#
#===/ DATASETS: ORACC ETCSL UD abbreviations /=================================
#
'''
* Source: https://docs.google.com/spreadsheets/d/1Is7MGG0h8h0vfHj9C9mnWOD2utPeu
          vm1ZeYb1dsaejg/edit#gid=0
* Location:
  Kept as JSON in /json/ with prefix 'ORACC_ETCSL_UD_abbr_'.
  See `datasets_lst` and `load_json_sets` params in class
  `tags` below.
* Data:
  - named_entities_dict:
    abbreviations for named entities
    key - full name
    value - abbr. list: [ORACC, ETCSL, UD]
  - POS_dict:
    abbreviations for POS
    key - full name
    value - abbr. list: [ORACC, ETCSL, UD]
  - order_dict:
    key - numbers from 0 to 2 
    value - convention name
    order: ORACC, ETCSL, UD
* Comments:
  Double vowels stand for long vowel.
'''
#---/ POS and named entities /-------------------------------------------------
#
class tags(common_functions):
  '''
  Class for managing tags order in dict. lists:
  ORACC, ETCSL, UD.
  '''
  datasets_lst = [
    ('order_dict', None),
    ('POS_dict', None),
    ('named_entities_dict', None)
    ]
  
  def __init__(self):
    '''
    Create a list of all possible values.
    '''
    self.load_json_sets(self.datasets_lst,
                        path='json',
                        prefix='ORACC_ETCSL_UD_abbr_',
                        add=True)
##  # This is used to dump the datasets, if needed: 
##    self.dump_json_sets(self.datasets_lst,
##                        path='json',
##                        prefix='ORACC_ETCSL_UD_abbr_')
    self.all = ['_']
    for dct in [self.POS_dict, self.named_entities_dict]:
      for k in dct.keys():
        for el in dct[k]:
          if el not in self.all:
            self.all.append(el)
    #ToDo: Ensure this line is everywhere elsewhere:
    self.all = sorted(self.all, key=lambda k: -len(k))

  def convert(self, tag, source, target):
    '''
    Recieve tag in one convention and return it in another, if exists.
    Allowed `source` and `target` values: 'ORACC', 'ETCSL', and 'UD'.
    '''
    if source==target or tag=='_':
      return tag
    src = self.order_dict[source]
    trg = self.order_dict[target]
    for dct in [self.POS_dict, self.named_entities_dict]:
      for k in dct.keys():
        if dct[k][src]==tag and dct[k][trg]!='':
          return dct[k][trg]
    #print('No %s value found for %s tag: %s' %(target, source, tag))
    return tag

  def adjust_POS(self, tag, src_convention, trg_convention='ORACC'):
    #ToDo: Ensure the following function is so elsewhere:
    '''
    Strip and unify POS tag.
    '''
    # NOTE 'X', 'U', 'L', and 'MA' as POS tags (clarify!)
    tag = tag.upper()
    if ' ' in tag:
      tag = tag.split(' ')[0]
    for t in self.all:
      for p in ['.', '/', ':']:
        if '%s%s' %(t,p) in tag:
          #print([t, self.convert(t, src_convention, trg_convention)])
          return self.convert(t, src_convention, trg_convention)
    if tag not in self.all:
      #print('Undefined %s tag escaped: %s' %(src_convention, tag))
      return '_'
    c_tag = self.convert(tag, src_convention, trg_convention)
    if c_tag!='':
      return c_tag
    return tag
#
#---/ Converter /--------------------------------------------------------------
#

class morph_converter(common_functions):
  '''
  Converts different Sumerian annotation styles with dict. given above.
  MTAAC > ORACC: `self.MTAAC2ORACC()` with annotation str as argument.
  '''
  datasets_lst = [
    ('N', None),
    ('V', None),
    ('NV', None),
    ('NAMED_ENTITIES', None)
    ]
  
  def __init__(self):
    self.load_json_sets(self.datasets_lst,
                        path='json',
                        prefix='ORACC_morph_annotation_',
                        add=True)
##  # This is used to dump the datasets, if needed: 
##    self.dump_json_sets(self.datasets_lst,
##                        path='json',
##                        prefix='ORACC_morph_annotation_')
    
  def MTAAC2ORACC(self, m_str):
    '''
    Convert MTAAC morph. annotation style to ORACC style.
    Shortcut for `self.add_slot_lables_to_abbr()`
    '''
    return self.add_slot_lables_to_abbr(m_str)

  def add_slot_lables_to_abbr(self, m_str):
    '''
    Add ORACC-style slots (N1=..., V1=..., NV11=...)
    to MTAAC morph. annotation. 
    '''
    [N, V, NV, NAMED_ENTITIES] = [self.N, self.V, self.NV, self.NAMED_ENTITIES]
    default_slot = ''
    m_lst = m_str.replace('’', "'").split('.')
    if 'NF' in m_lst:
      lst = NV+N
      m_lst = m_lst[1:]
      default_slot = 'NV2=STEM'
    elif 'V' not in m_lst:
      lst = N
      default_slot = 'N1=STEM'
      if set(m_lst) & set(NAMED_ENTITIES):
        default_slot = 'N1=NAME' 
    else:
      lst = V
      default_slot = 'V12=STEM'
    m_lst_new = []
    for m in m_lst:
      slot_m = ''
      for d in lst:
        if m in d['abbreviations']:
          slot_m = '%s=%s' %(d['slot'], m)
          break
      if slot_m=='':
        slot_m = default_slot
      m_lst_new.append(slot_m)
    return '.'.join(m_lst_new)

if __name__ == '__main__':
  pass
