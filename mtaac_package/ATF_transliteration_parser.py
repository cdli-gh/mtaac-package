import re
from lxml import etree
from .common_functions import *
from .syllabary import syllabary
from .morph_annotation import tags
       
sylb = syllabary() 

#---/ Transliteration parser & normalizer /------------------------------------
#
# IMPORTANT:
#
# THIS SHOULD BE MERGED WITH ANOTHER VERSION (for translated texts)
# BELOW
#
# NOTE DIFFERENCES -
# E.G. HANDLING DETERMINATIVES (ignored there),
# NORMALIZATIONS (3 types here), PLACEHOLDERS ETC.

re_x_index = re.compile(r'(?P<a>[\w])x')
re_x_sign = re.compile(r'(ₓ\(.+\))')
re_brc = re.compile(r'(\(.+\))')
re_source = re.compile(r'(?P<a>.+)(?P<b>\(source:)(?P<c>[^)]+)(?P<d>\))')
re_index = re.compile(r'(?P<sign>[^\d]+)(?P<index>\d+)')
re_brc_div = re.compile(r'(?P<a>\([^\)]+)(?P<b>-+)(?P<c>[^\(]+\))')
extra = re.compile('(\[|\]|\{\?\}|\{\!\})')
numerals = ['barig', "gec'u", 'dic', 'dic@t', 'dic@v', 'ban2', "bur'u",
            'cargal', "car'u@c", 'ac@c', 'u@c', "bur'u@c", "gec'u@c",
            'iku@c', 'esze3', 'bur3']
re_num = re.compile(r'|'.join(numerals))
remove_lst = ['…', '$)', '#', '$', '<', '>']

class transliteration(common_functions):
  '''
  '''
    
  def __init__(self, translit, base=False, syllabary_check=True):
    '''
    Use base=True for (partly) normalized transcriptions.
    '''
    self.defective = False
    self.annotation = None
    self.syllabary_check = syllabary_check
    self.syl_dict_lst = []
    self.raw_translit = translit
    self.parse_translit(translit, base)
    if self.defective==True:
      return None
    
  def parse_translit(self, translit, base):
    '''
    '''
    translit = translit.strip(' ')
    translit = translit.replace('source: ', 'source:')
    if '\\' in translit:
      translit = self.parse_slash(translit)
    self.defective_checks(translit)
    if self.defective==True:
      return None
    translit = self.brc_slash_replace(translit)
    translit = extra.sub('', translit)
    translit = self.standardize_translit(translit)
    self.base_translit = translit
    self.sign_list = self.parse_signs(translit)
    for el in self.sign_list:
      if 'x' in el['value'].lower() and '×' not in el['value'].lower():
        self.defective = True
        return None
      if '(' in el['value']:
        pass
        #print([self.raw_translit, self.base_translit, el['value'], self.sign_list])
    i=0
    while i < len(self.sign_list):
      if 'det' not in self.sign_list[i]['type']:
        self.sign_list[i] = self.get_unicode_index(self.sign_list[i])
      i+=1
    if base!=True:
      self.signs_in_syllabary()
    self.set_normalizations()

  def defective_checks(self, translit):
    '''
    '''
    if [t for t in ['blank', 'space'] if t in translit]!=[]:
      self.defective = True
    if ' ' in translit:
      self.defective = True
    for expt in ['_', '...', 'line', '(X', 'X)', '.X',
                 ' X', 'Xbr','-X', 'ṭ', 'ṣ', 'missing']:
      if expt in translit or expt.lower() in translit.lower():
        self.defective = True
    if translit.lower()!=translit:
      self.defective = True

  def brc_slash_replace(self, translit):
    """
    Replace combinations of slashes and brackets with brackets.
    """
    brc_lst = ['(', ')', '{', '}']
    slash_lst = ['\\', '/']
    translit_new = ''
    for t in translit:
      if translit_new!='':
        if t in brc_lst and translit_new[-1] in slash_lst:
          translit_new = translit_new[:-1]+t
        elif t in slash_lst and translit_new[-1] in brc_lst:
          pass
        else:
          translit_new+=t
      else:
        translit_new+=t
    return translit_new

  def parse_slash(self, translit):
    '''
    Divide and extract annotation divided with slash.
    '''
    annot_lst = ['erg', 'gen', 'abs', 'com', 'dat', 'term', 'adv', 'abl',
                 'dem1', 'dem2', 'poss', 'l1', 'l2', 'l3', 'cop', 'x']
    t_lst = [t for t in translit.split('\\') if t!='']
    i = 1
    while i < len(t_lst):
      if (t_lst[i] in annot_lst) or \
         (t_lst[i][0] in ['v', 'n'] and is_int(t_lst[i][1])==True):
        translit = '\\'.join(t_lst[:i])
        self.annotation = '\\'.join(t_lst[i:])
        break
      i+=1
    return translit

  def signs_in_syllabary(self):
    '''
    Check parsed signs against syllabary data.
    '''
    if self.syllabary_check!=True:
      return None
    s_dict_lst = []
    for s in self.sign_list:
      s_dict = None
      #skip numerals for the time:
      if '(' not in s['value'] and s['value']!='n' \
         and not is_int(s['value'][0]):
        index = s['index']
        if index=='':
          index = 1
        s_dict = sylb.find_entry_by_value(s['value'], index)
        if s_dict==None:
          s_dict = sylb.find_entry_by_name(s['value_of'])
        if s_dict==None:
          s_dict = sylb.find_entry_by_name(self.raw_translit)
        if s_dict==None:
          print('No entry found for sign:', self.raw_translit, s)
      s_dict_lst+=[s_dict]
    self.syl_dict_lst = s_dict_lst

  def get_unicode_str(self):
    '''
    Return the transliteration as str in cuneiform Unicode chars.
    '''
    self.syllabary_check = True
    self.signs_in_syllabary()
    for s_dict in self.syl_dict_lst:
      print(s_dict)
#
# NOTE: this was meant to be part of a normalization line,
# that is not finished:
#
##    if None not in s_dict_lst:
##      sylb.check_sequence(s_dict_lst, self.sign_list)
##      if s_dict!=None:
##        self.normalize_with_syllabary(s_dict, [s['value'], index])
##
##  def normalize_with_syllabary(self, s_dict, sign_index_lst):
##    '''
##    '''
##    old_sign = sign_index_lst[0]+self.stringify_index(sign_index_lst[1])
##    new_sign = sylb.standardize(s_dict, sign_index_lst)
##    if old_sign!=new_sign:
##      print(self.raw_translit, '|', old_sign, '-->', new_sign)

  def restyle_determinatives(self, translit):
    '''
    '''
    re_det = re.compile(r'((?P<o_brc>\{)(?P<det>.*?)(?P<c_brc>\}))')
    while re_det.search(translit):
      m = re_det.search(translit)
      prefix = postfix = ''
      if m.start() > 0:
        if translit[m.start()-1] not in ['-']:
          prefix = '-'
          typ = 1 #follows
      else:
        typ = 0 #preceedes
      if m.end()+1 < len(translit):
        if translit[m.end()] not in ['-']:
          postfix = '-'
          typ = 0 #preceeds
      else:
        typ = 1 #follows
      translit = re_det.sub('%s%s_DT%s%s' %(prefix, m.group('det'),
                                            typ, postfix), translit, 1)
    return translit

  def parse_signs(self, translit, num2unit=True):
    '''
    `num2unit=True` means escaping numbers and having basic values
    or units instead:
    E.g. 3(disz)[one] > disz, 5(gesz)[sixty] > gesz,
    1(gesz'u)[six_hundred] > gesz'u, 3(ban)[unit] > ban, etc. 
    '''
    signs_lst = []
    translit = self.restyle_determinatives(translit)
    if re_brc_div.search(translit):
      translit = re_brc_div.sub(lambda m: m.group().replace('-',"="),
                                translit)
    for sign in [s for s in translit.split('-') if s!='']:
      if ':' not in sign or 'source:' in sign:
        signs_lst = self.parse_and_append_to_sign_list(sign,
                                                       num2unit,
                                                       signs_lst)
      else:
        for s in sign.split(':')[::-1]:
          signs_lst = self.parse_and_append_to_sign_list(s,
                                                         num2unit,
                                                         signs_lst)
    return signs_lst

  def parse_and_append_to_sign_list(self, sign, num2unit, signs_lst):
    '''
    '''
    s = self.parse_sign(sign, num2unit)
    if s['value']!='' and s['emendation']=='':
      signs_lst.append(s)
    # ATTENTION: the following replaces sequences of signs with seq.
    # emendations and single sign values with their emendations.
    elif s['emendation']!='':
      if '-' in s['emendation']:
        signs_lst = self.parse_signs(s['emendation'])
      else:
        signs_lst.append(self.parse_sign(s['emendation'], num2unit))
    return signs_lst

  def parse_sign(self, sign, num2unit):
    '''
    '''
    index = ''
    emendation = ''
    value_of = ''
    typ = ''
    sign = sign.strip('/\\')
    if 'source' in sign:
      emendation = re_source.sub(r'\g<c>', sign).replace('=',"-").strip('()')
      sign = re_source.sub(r'\g<a>', sign).strip('()')
    for el in remove_lst:
      if el in sign:
        sign = sign.replace(el, '')
    if '_DT' in sign:
      sign, direction = sign.split('_DT')
      typ = 'det'+direction
    if re_x_index.search(sign):
      sign = re_x_index.sub('\g<a>ₓ', sign)
    if 'ₓ(' in sign.lower():
      index='x'
      value_of = re_x_sign.search(sign).group().strip('ₓ()').replace('=',"-")
      sign = re_x_sign.sub('', sign)
    if re_brc.search(sign) and not re_num.search(sign):
      value_of = re_brc.search(sign).group().strip('()').replace('=',"-")
      sign = re_brc.sub('', sign)
    if 'x' in sign.lower() and len(sign)>1:
      pass
    if (re_index.search(sign) and '/' not in sign \
        and not re_num.search(sign)) or sign in ['bur3']:
      #quick fix for bur3 as it can appear both in re_num and as "normal" value
      [sign, index] = self.parse_index(sign)
    if value_of!='' and sign!='':
      if num2unit==True and sign[0] in [str(i) for i in range(0, 9)]:
        [sign, index] = self.parse_index(value_of)
    return {'value': sign,
            'index': index,
            'type': typ,
            'emendation': emendation,
            'value_of': value_of
            }

  def parse_index(self, sign):
    '''
    '''
    re_index = re.compile(r'(?P<sign>[^\d]+)(?P<index>\d+)')
    i = 0
    index = ''
    for x in re_index.finditer(sign):
      if i==0:
        index = x.groupdict()['index']
        sign = x.groupdict()['sign']
      else:
        pass
        #print(self.raw_translit, sign, i, x.groupdict()['sign'], x.groupdict()['index'])
      i+=1
    return [sign, index]

  def set_normalizations(self):
    '''
    '''
    norm_flat_lst = [s['value'] for s in self.sign_list
                     if 'det' not in s['type'] and s['value']!='']
    norm_unicode_lst = [s['u_sign'] for s in self.sign_list
                        if 'det' not in s['type']]
    self.set_sign_and_determinative_normalization()
    i = 0
    self.normalization = ''
    self.normalization_u = ''
    while i < len(norm_flat_lst):
      if self.normalization:
        if self.normalization[-1]==norm_flat_lst[i][0]:
          self.normalization+=norm_flat_lst[i][1:]
          self.normalization_u+=norm_unicode_lst[i][1:]
        else:
          self.normalization+=norm_flat_lst[i]
          self.normalization_u+=norm_unicode_lst[i]          
      else:
        self.normalization+=norm_flat_lst[i]
        self.normalization_u+=norm_unicode_lst[i]
      i+=1

  def set_sign_and_determinative_normalization(self):
    '''
    Special type of normalization for the purpuse of lemmatization testing:
      First non determinative sign and first determinative in order
      of spelling, no index.
    '''
    self.first_sign = ''
    self.sign_and_det_normalization = ''
    assigned = [False, False]
    for s in self.sign_list:
      if 'det' not in s['type'] and assigned[0]==False:
        self.sign_and_det_normalization+=s['value']
        self.first_sign = s['value']
        assigned[0] = True
      elif 'det' in s['type'] and assigned[1]==False:
        self.sign_and_det_normalization+=s['value']
        assigned[1] = True

  def get_unicode_index(self, sign_dict):
    '''
    '''
    vow_lst = ['a', 'A', 'e', 'E', 'i', 'I', 'u', 'U']
    re_last_vow = re.compile(r'(%s)' %('|'.join(vow_lst)))
    sign_dict['u_sign'] = sign_dict['value']
    if sign_dict['index'] not in ['', 'x']:
      val = sign_dict['value']
      try:
        v = re_last_vow.findall(val)[-1]
        esc = chr((vow_lst.index(v)+1)*1000+int(sign_dict['index']))
        i = val.rfind(v)
        u_sign = '%s%s%s' %(val[:i], esc, val[i+1:])
        sign_dict['u_sign'] = u_sign
      except IndexError:
        sign_dict['u_sign'] = val
    return sign_dict    

  def revert_unicode_index(self, u_sign):
    '''
    '''
    vow_lst = ['a', 'A', 'e', 'E', 'i', 'I', 'u', 'U']
    i =0
    while i < len(u_sign):
      n = ord(u_sign[i])
      if n > 1000:
        vow_i = int(str(n)[0])-1
        index = int(str(n)[2:])
        return {'value': u_sign[:i]+vow_lst[vow_i]+u_sign[i+1:],
                'index': index}
      i+=1

# ToDo: this version should be merged with the one above.
#       Make sure the translated scripts run well when testing.
#
#---/ATF Transliteration parser: corpus split version /-----------------------------------------------------------
#
##class transliteration:
##  '''
##  '''
##  re_extra_sign = re.compile(r'(( |-|)<<.+>>( |-|))')
##  re_extra = re.compile('(\[|\]|\{\?\}|\{\!\}|\\\|/|<|>)')
##    
##  re_x_index = re.compile(r'(?P<a>[\w])x')
##  re_x_sign = re.compile(r'(ₓ\(.+\))')
##  re_brc = re.compile(r'(\(.+\))')
##  re_source = re.compile(r'(?P<a>.+)(?P<b>\(source:)(?P<c>[^)]+)(?P<d>\))')
##  re_index = re.compile(r'(?P<sign>[^\d]+)(?P<index>\d+)')
##  re_brc_div = re.compile(r'(?P<a>\([^\)]+)(?P<b>-+)(?P<c>[^\(]+\))')
##
##  vow_lst = ['a', 'A', 'e', 'E', 'i', 'I', 'u', 'U']
##  re_last_vow = re.compile(r'(%s)' %('|'.join(vow_lst)))
##  re_times = re.compile(r'(?P<a>[\w])x(?P<b>[\w])')
##  std_dict = {
##    'š': 'c',
##    'ŋ': 'j',
##    '₀': '0',
##    '₁': '1',
##    '₂': '2',
##    '₃': '3',
##    '₄': '4',
##    '₅': '5',
##    '₆': '6',
##    '₇': '7',
##    '₈': '8',
##    '₉': '9',
##    '+': '-',
##    'Š': 'C',
##    'Ŋ': 'J',
##    'sz': 'c',
##    'SZ': 'C',
##    '·': '',
##    '°': '',
##    '#': '',
##    '!': '',
##    '?': ''}
##
##  def __init__(self, translit):
##    '''
##    '''
##    self.raw_translit = translit
##    translit = self.preporcess_translit(translit)
##    self.check_defective(translit, 'pre')
##    if self.defective==True:
##      self.normalization = 'X'
##      return None
##    self.sign_list = self.get_sign_lst(translit)
##    self.check_defective(translit, 'post')
##    if self.defective==True:
##      self.normalization = 'X'
##      return None
##    self.get_unicode_index_all()
##    self.set_normalizations()
##    
##  def preporcess_translit(self, translit):
##    '''
##    '''
##    translit = translit.strip(' ')
##    translit = translit.replace('source: ', 'source:')
##    if '<<' in translit:
##      translit = self.re_extra_sign.sub('', translit)
##    translit = self.re_extra.sub('', translit)
##    translit = self.standardize_translit(translit)
##    translit = self.remove_determinatives(translit)
##    self.base_translit = translit
##    return translit
##
##  def check_defective(self, translit, step):
##    '''
##    '''
##    self.defective = False
##    if step=="pre":
##      if ' ' in translit:
##        self.defective = True
##      for expt in ['_', '...', 'line', '(X', 'X)', '.X',
##                   ' X', 'Xbr','-X', 'ṭ', 'ṣ', 'missing']:
##        if expt in translit or expt.lower() in translit.lower():
##          self.defective = True
##      if translit.lower()!=translit:
##        pass
##        # ! PROBLEMATIC: TOO MANY SIGNS IGNORED
##        # ! CHANGE THIS
##  ##      self.defective = True
##    elif step=="post":
##      for el in self.sign_list:
##        if 'x' in el['value'].lower() and '×' not in el['value'].lower():
##          self.defective = True
##        if '(' in el['value']:
##          pass
##          print([self.raw_translit, self.base_translit, el['value'],
##                 self.sign_list])
##
##  def get_sign_lst(self, translit):
##    '''
##    '''
##    signs_lst = []
##    if self.re_brc_div.search(translit):
##      translit = self.re_brc_div.sub(lambda m: m.group().replace('-',"="),
##                                translit)    
##    for sign_str in list(filter(lambda x: x!='', translit.split('-'))):
##      signs_lst.append(self.parse_sign(sign_str))
##    return signs_lst
##
##  def parse_sign(self, sign):
##    '''
##    '''
##    index = ''
##    emendation = ''
##    value_of = ''
##    if self.re_x_index.search(sign):
##      sign = self.re_x_index.sub('\g<a>ₓ', sign)
##    if 'ₓ(' in sign.lower():
##      index='x'
##      value_of = self.re_x_sign.search(sign).group().strip('ₓ()')\
##                 .replace('=',"-")
##      sign = self.re_x_sign.sub('', sign)
##    if self.re_brc.search(sign):
##      if sign[0]=='(' and sign[-1]==')':
##        sign = sign.strip('()')
##      else:
##        value_of = self.re_brc.search(sign).group().strip('()')\
##                   .replace('=',"-")
##        sign = self.re_brc.sub('', sign)
##    if 'x' in sign.lower() and len(sign)>1:
##      pass
##    if self.re_source.search(sign):
##      emendation = self.re_source.sub(r'\g<c>', sign).replace('=',"-")
##      sign = self.re_source.sub(r'\g<a>', sign)
##    if self.re_index.search(sign):
##      i = 0
##      for x in self.re_index.finditer(sign):
##        if i==0:
##          index = x.groupdict()['index']
##          sign = x.groupdict()['sign']
##        else:
##          pass
##          # CHECK FOR POSSIBLE ERRORS
##          #print(self.raw_translit, sign, i, x.groupdict()['sign'], x.groupdict()['index'])
##        i+=1
##    return {'value': sign,
##            'index': index,
##            'emendation': emendation,
##            'value_of': value_of}
##
##  def set_normalizations(self, placeholders=True):
##    '''
##    '''
##    s_lst = self.sign_list
##    norm_flat_lst = [s['value'] for s in s_lst]
##    norm_unicode_lst = [s['u_sign'] for s in s_lst]
##    if placeholders==True:
##      s_lst = self.get_placeholders_lst()
##      norm_flat_lst = [s for s in s_lst]
##    self.normalization = ''
##    self.normalization_u = ''
##    i = 0
##    while i < len(norm_flat_lst):
##      if self.normalization:
##        if self.normalization[-1]==norm_flat_lst[i][0]:
##          self.normalization+=norm_flat_lst[i][1:]
##          self.normalization_u+=norm_unicode_lst[i][1:]
##        else:
##          self.normalization+=norm_flat_lst[i]
##          self.normalization_u+=norm_unicode_lst[i]
##      else:
##        self.normalization+=norm_flat_lst[i]
##        self.normalization_u+=norm_unicode_lst[i]
##      i+=1
##
##  def get_placeholders_lst(self):
##    """
##    Returns a list of rule-based placeholders or values.
##    IMPORTANT: ´PLACEHOLDERS´ should contain a full list of possible values.
##    """
##    placeholders_lst = []
##    for s in self.sign_list:
##      if is_int(s['value'][0])==True:
##        placeholders_lst = self.append_if_not_as_last('NUMB',
##                                                      placeholders_lst)
##      # ADD HERE RULES FOR PN, DN etc.
##      # E.g.:
##      # if (s[value], s['index']) in [('lugal', ''), ('lu', '2')]
##      # ADD determinatives handling to class!!!
##      #  for now they are just deleted
##      # NOTE also that PNs can come with cases, e.g. PN-ta 
##      else:
##        placeholders_lst.append(s['value'])
##    return placeholders_lst
##
##  def append_if_not_as_last(self, el, lst):
##    '''
##    '''
##    if lst==[]:
##      return [el]
##    if lst[-1]!=el:
##      lst.append(el)
##    return lst
##  
##  def standardize_translit(self, translit):
##    '''
##    '''
##    for key in self.std_dict.keys():
##      translit = translit.replace(key, std_dict[key])
##    if self.re_times.search(translit):
##      translit = self.re_times.sub('\g<a>×\g<b>', translit)
##    return translit
##
##  def get_unicode_index_all(self):
##    '''
##    '''
##    i = 0
##    while i < len(self.sign_list):
##      self.sign_list[i] = self.get_unicode_index(self.sign_list[i])
##      i+=1
##
##  def get_unicode_index(self, sign_dict):
##    '''
##    '''
##    sign_dict['u_sign'] = sign_dict['value']
##    if sign_dict['index'] not in ['', 'x']:
##      val = sign_dict['value']
##      try:
##        v = self.re_last_vow.findall(val)[-1]
##      except:
##        print(val, self.raw_translit)
##      esc = chr((self.vow_lst.index(v)+1)*1000+int(sign_dict['index']))
##      i = val.rfind(v)
##      u_sign = '%s%s%s' %(val[:i], esc, val[i+1:])
##      sign_dict['u_sign']=u_sign
##    return sign_dict    
##
##  def revert_unicode_index(self, u_sign):
##    '''
##    '''
##    i = 0
##    while i < len(u_sign):
##      n = ord(u_sign[i])
##      if n > 1000:
##        vow_i = int(str(n)[0])-1
##        index = int(str(n)[2:])
##        return {'value': u_sign[:i]+self.vow_lst[vow_i]+u_sign[i+1:],
##                'index': index}
##      i+=1
##
##  def remove_determinatives(self, translit):
##    '''
##    '''
##    det = re.compile('(\{.*?\})')
##    return det.sub('', translit)

if __name__ == '__main__':
  pass
