import sys
from lark import Lark, Transformer, v_args
from lark.lexer import Lexer, Token

atf_test = '''
2014-07-05 18:52:20, entered by englund for aupperle 
&P102313 = ASJ 09, 254 37
#atf: lang sux
@tablet
@obverse
1. 1(gesz2) la2 1(disz) udu
#tr.en: 59 sheep,
2. 8(disz) masz2
#tr.en: 8 goats,
3. szu la2-a
#tr.en: ...,
4. ki ab-ba-sa6-ga-ta
#tr.en: from Abbasaga
@reverse
1. be-li2-a-zu
#tr.en: Belī-azu
2. i3-dab5
#tr.en: accepted;
$ blank space
3. iti ses-da-gu7
#tr.en: month: “Piglet-feast,”
4. mu {d}gu-za {d}en-lil2-la2 ba-dim2
#tr.en: year: “The throne of Enlil was fashioned;”
@left
1. 1(gesz2) 7(disz)
#tr.en: (total:) 67.
'''

##atf_grammar = r"""
##    ?start: text
##    text: text_element (ws text_element)*
##    ?text_element: token
##          | lacuna
##          | line_no
##
##    ?token: token_element (separator token_element)*
##    token_element: sign
##          | lacuna
##          | line_no
##          | gloss
##
##    separator: /-|\.|:/
##    nl: "\r\n" | "\n"
##    line_no: nl (alp_lower | (num_plain "'"*) ".")+
##    gloss: "{" token "}"
##    sign: value
##    value: logogram
##          | syllabogram
##          | determinative
##          | numeral
##          | uncertain
##          | undefined
##          
##    ws : " "
##
##    alp_lower: /[a-z]+/
##    alp_upper: /[A-Z]+/
##    alp: alp_lower | alp_upper
##
##    num_plain : /\d+/
##    num_subscript : /[₀-₉]+/
##    num_fract_vulgar : num_plain "/" num_plain
##    num_placeholder : /n|N/
##    num : num_plain | num_fract_vulgar | num_placeholder
##    
##    lacuna : "..."
##    index : (num_plain | num_subscript | "x" | "ₓ")*
##    quantity: num
##    modifier : ("@" alp)*
##
##    sign_name_log: alp_upper
##    sign_name_syl: alp_lower
##    sign_name_det: alp_lower 
##    sign_name_num: alp
##    sign_name_uct: alp_upper
##    sign_name_ndf: "X" | "x"
##
##    logogram.1 : sign_name_log index modifier
##    syllabogram.1 : sign_name_syl index modifier
##    determinative.1 : sign_name_det index modifier
##    numeral : quantity ("(" sign_name_num index modifier ")")*
##    uncertain : sign_name_uct
##    undefined : sign_name_ndf
##    
##    //array  : "[" [value ("," value)*] "]"
##    //object : "{" [pair ("," pair)*] "}"
##    //pair   : string ":" value
##    //string : ESCAPED_STRING
##    //%import common.ESCAPED_STRING
##    //%import common.SIGNED_NUMBER
##    //%import common.WS
##    //%ignore WS
##"""


from lark import Lark, Transformer, v_args
from lark.lexer import Lexer, Token

class TypeLexer(Lexer):
    def __init__(self, lexer_conf):
        pass

    def lex(self, data):
        for obj in data:
            if isinstance(obj, int):
                yield Token('INT', obj)
            elif isinstance(obj, (type(''), type(u''))):
                yield Token('STR', obj)
            else:
                raise TypeError(obj)

parser = Lark("""
        start: data_item+
        data_item: STR INT*
        %declare STR INT
        """, parser='lalr', lexer=TypeLexer)


class ParseToDict(Transformer):
    @v_args(inline=True)
    def data_item(self, name, *numbers):
        return name.value, [n.value for n in numbers]

    start = dict


def test():
    data = ['alice', 1, 27, 3, 'bob', 4, 'carrie', 'dan', 8, 6]

    print(data)

    tree = parser.parse(data)
    res = ParseToDict().transform(tree)

    print('-->')
    print(res) # prints {'alice': [1, 27, 3], 'bob': [4], 'carrie': [], 'dan': [8, 6]}

if __name__ == '__main__':
    test()


##if __name__ == '__main__':
##    # test()
##    with open(sys.argv[1]) as f:
##        print(parse(f.read()))

##import re
###from .common_functions import *
##from mtaac_package.common_functions import *
##
##def re_namedgroup(name, regex):
##  '''
##  Convert regex string to regex group with name.
##  '''
##  return r'(?P<%s>%s)' %(name, regex)
##
##reGroup = \
##        re.compile(r'\?P<(?P<name>.*?)(?=>)>(?P<content>.*?|)(?=\))')
##
##def get_namedgroups(regex):
##  '''
##  Return a list of tuples with group names
##  and regex content for regex.
##  '''
##  if hasattr(regex, 'pattern'):
##    return [r for r in reGroup.findall(regex.pattern)]
##  return [r for r in reGroup.findall(regex)]
##
##def get_dictgroup(r, s_str):
##  '''
##  Return groupdict for the LAST found match in re.
##  '''
##  if r.match(s_str):
##    return [x for x in r.finditer(s_str)][0].groupdict()
##  return []
##
##def re2tuple(name, r_str):
##  '''
##  Return tuple (name & compiled re)
##  '''
##  return (name, re.compile(r_str))
##
##class re_nested:
##  '''
##  '''
##  
##  def re_element(self, name, re):
##    '''
##    '''
##    return {
##      'type': 'element',
##      'name': name,
##      're': re,
##      're_named': re_namedgroup(name, re)
##      }
##
##  def re_group_OR(self, name, elements):
##    '''
##    '''
##    return {
##      'type':'group_OR',
##      'name': name,
##      'elements': elements
##      }
##
##  def re_render_element(self, element, elements):
##    '''
##    '''
##    return {
##      }
##
##RE = re_nested()
##
##_val = RE.re_element('value', '[^\d|]+')
##_ind = RE.re_element('index', '\d+|x|X|ₓ|')
##_mod = RE.re_element('modif', '@[a-z]+|')
##_qnt = RE.re_element('quant', '\d+|\d+/\d+')
##_sign_base = RE.re_element('sign_b', _val+_ind+_mod)
##_sign_num_complex = RE.re_element('sign_nc',
##  r'%s\(%s\)'%(_qnt['re_named'],
##               _sign_base['re_named']))
##_sign_num_plain = RE.re_element('sign_np', _qnt['re_named'])
##
##_sign = [_sign_num_complex, _sign_base, _sign_num_plain]
##
####
####
####_re_sign = re_namedgroup('sign', '|'.join([r'(%s)'%s for s in signs]))
##
##print(_re_sign)
##
####_re_sequence = r'%s\(%s\)' %(_qnt, _re_sign)
####
####re_sign = re2tuple('re_sign', _re_sign)
####re_num = re2tuple('re_num', _num)
####re_num_plain = re2tuple('re_num_plain', _qnt)
##
####re_sequence = re2tuple()
##
###print([g for g in re_num_plain.groups])
###print(re_num.groupindex, get_namedgroups(re_num.pattern))
##
##class ATF_char_parser(common_functions):
##  '''
##  '''
##
##  signs_re = [re2tuple('re_sign', _re_sign)] #[re_sign, re_num, re_num_plain]
##
##  def parse(self, s_str, typ=None):
##    '''
##    '''
##    
##    s_str = '1(dic3@c)'
##    s_str = '1'
##    for name, r in self.signs_re:
##      g_dict = get_dictgroup(r, s_str)
##      if g_dict:
##        n_groups = get_namedgroups(r)
##        for n, p in n_groups:
##          print([name, n, g_dict[n], p])
##        break
##
####    
####    v_dict = {}
####    if typ:
####      v_dict = self.get_v_dict()
####    value = s_str
####    index = 1
####    quantity = None
####    modifier = None
####    if re_num.fullmatch(s_str):
####      pass
####    elif re_sign.fullmatch(s_str):
####      pass
####    elif re_num_plain.fullmatch(s_str):
####      pass
##    
##  def get_v_dict(self, typ):
##    '''
##    Returns value dict. for type.
##    '''
##    #Subfunction of ´self.load_extra()´.
##    if typ=='l':
##      return {'type': 'logographic', 'main': None}
##    elif typ=='s':
##      return {'type': 'syllabic'}
##    elif typ=='n':
##      return {'type': 'numeral'}
##
####  def val_and_index(self, s_str):
####    '''
####    Parse value and index in sign, return dict.
####    '''
####    value = s_str
####    index = 1
####    quantity = None
####    modifier = None
####    if '(' in s_str or ')' in s_str:
####      print(s_str)
####    if self.re_index_num.search(s_str):
####      dic = [x for x in self.re_index_num.finditer(s_str)][0].groupdict()
####      value = dic['value']
####      quantity = dic['quantity']
####      if dic['index']:
####        index = dic['index']
####    elif 'ₓ' in s_str:
####      return {'value': s_str.strip('ₓ'),
####              'index': 'ₓ'}
####    elif self.re_index.search(s_str):
####      dic = [x for x in self.re_index.finditer(s_str)][0].groupdict()
####      value = dic['value']
####      index = dic['index']
####    if quantity:
####      #print(s_str, {'index': int(index), 'value': value, 'quantity': quantity})
####      return {'index': int(index), 'value': value, 'quantity': quantity}
####    return {'index': int(index), 'value': value}
##
##  def stringify_index(self, index):
##    '''
##    Return value index as int., x or zero.
##    '''
##    index_str = ''
##    if index in ['ₓ']:
##      return index
##    if int(index) > 1:
##      index_str = str(index)
##    return index_str
##
##ACP = ATF_char_parser()
##ACP.parse('')
