'''
TODO: ADD DESCRIPTION HERE
'''
#---/Translation normalizer/---------------------------------------------------
#
class translation:
  '''
  TODO: escape numb with `self.escape_numbers_eng()`
        and `self.add_punct_spaces()` should be made optional.
  '''
  re_brc = re.compile(r'(\(.+\))')
  punct_lst = [':', ';', '?', '.', ',', '”', '“']

  def __init__(self, tra_str):
    self.trt_str = tra_str
    self.processed_str = self.process()

  def process(self):
    '''
    Functions to process translated text for MT. 
    '''
    line = self.trt_str
    line = self.add_punct_spaces(line)
    line = self.escape_numbers_eng(line)
    return line
  
  def add_punct_spaces(self, line):
    '''
    Add spaces to translation before and after punctuation signs.
    Remove square brackets. 
    '''
    line = self.re_brc.sub('', line)
    line = line.replace('...', '…')
    for sq_brc in ['[', ']']:
      line = line.replace(sq_brc, '')
    i = 0
    while i < len(line):
      c = line[i]
      if i>0 and c in self.punct_lst:
        if line[i-1] not in [' ']:
          line = '%s %s' %(line[:i], line[i:])
          i+=1
      if i+1 < len(line) and c in self.punct_lst:  
        if line[i+1] not in [' ', '\n']:
          line = '%s %s' %(line[:i+1], line[i+1:])
          i+=1
      i+=1
    return line.strip(' ')

  def escape_numbers_eng(self, line):
    '''
    Replace numbers in translation or sequences of numbers with NUMB.
    '''
    new_line = ""
    new_line_lst = []
    for t in line.split(' '):
      t_clean = t.replace("/", "").replace("…", "")
      if is_int(t_clean)==True or t in ['Ø', 'n', '+', 'n+']:
        new_line_lst = self.add_numb_eng(new_line_lst, t)
      elif t[-2:] in ['th', 'st', 'rd', 'nd'] and is_int(t[:-2])==True:
        new_line_lst.append("ordNUMB")
      else:
        new_line_lst.append(t)
    return " ".join(new_line_lst)

  def add_numb_eng(self, new_line_lst, t):
    '''
    Subfunction of `self.escape_numbers_eng()`.
    '''
    if new_line_lst==[]:
      return ["NUMB"]
    elif new_line_lst[-1]!='NUMB':
      new_line_lst.append("NUMB")
    return new_line_lst

if __name__ == '__main__':
  pass
