import subprocess
import codecs
import json
import os
from urllib.request import urlopen
from pathlib import Path
from urllib.error import URLError
import lxml
from lxml import html as lxml_html
# from multiprocessing import Pool

#---/ PATH variables /---------------------------------------------------------
# 
PATH_SRC = os.path.dirname(os.path.abspath(__file__))
PATH_PROJECT = os.path.dirname(PATH_SRC)
PATH_DATA = os.path.join(PATH_PROJECT, 'data')

#---/ CHECKS /-----------------------------------------------------------------
#
def is_int(char):
  try:
    int(char)
    return True
  except ValueError:
    return False  

#---/ Common functions /-------------------------------------------------------
#
class common_functions:
  """
  Class for commonly required funcitons.
  """

  def load_json(self, filepath):
    """
    Load data from JSON file.
    Arguments
      ´filepath´: path to JSON file.
    """
    with codecs.open(filepath, 'r', 'utf-8') as f:
      json_data = json.load(f)
    return json_data

  def load_json_sets(self, json_sets_lst, path='', prefix='', add=False):
    """
    Return a list of sets from a list of JSON filenames.
    Arguments
      ´path´: relative path (default '').
      ´prefix´: prefix for JSON files (default '').
      ´add´: when True, add as attributes to ´self´ object (default False).
    """
    json_sets_lst_new = []
    for (var, data) in json_sets_lst:
      filepath = os.path.join(PATH_DATA, path, prefix+var+'.json')
      data = self.load_json(filepath)
      json_sets_lst_new.append((var, data))
      if add==True:
        setattr(self, var, data)
    return json_sets_lst_new

  def dump_json_sets(self, json_sets_lst, path='', prefix=''):
    """
    Dump sets (filename, data) in list as JSON.
    Arguments
      ´path´: relative path (default '').
      ´prefix´: prefix for JSON files (default '').
    """ 
    for (var, data) in json_sets_lst:
      filename = os.path.join(PATH_DATA, path, prefix+var+'.json')
      self.dump(json.dumps(data, sort_keys=True, indent=2), filename)
  
  def dump(self, data, filepath):
    """
    Dump data to filepath.
    """
    with codecs.open(filepath, 'w', 'utf-8') as dump:
      dump.write(data)

  def get_html(self, url="", path="", repeated=False):
    """
    Get lxml_html object from url or path.
    """
    html = None
    if url:
      try:
        with urlopen(url) as response:
          html = lxml_html.parse(response).getroot()
      except (TimeoutError, URLError) as e:
        if repeated==False:
          print('TimeoutError: %s\nTrying again...' %(url))
          return self.get_html(url=url, repeated=True)
        else:
          print('TimeoutError: %s\nFailed' %(url))
          self.errors.append('TimeoutError: %s' %(url))
          return None
    elif path:
      html = lxml_html.parse(path).getroot()
    return html

#---/ SUBPROCESS /-------------------------------------------------------------
#
class subprocesses(common_functions):

  def __init__(self):
    self.subprocesses_list = []
    self.pending_lst = []
    self.max = 4
    self.env = os.environ.copy()
    
  def run(self, cmd, cwd='', stdin=None, print_stdout=False,
          return_stdout=True, decode_stdout=True, log_stdout=False):
    print('\n')
    print(r'run: %s' %(' '.join(cmd)))
    if not cwd:
      cwd = os.getcwd()
##    print(r'cwd: %s' %(cwd))
    p = subprocess.run(cmd,
                       cwd=r'%s' %(cwd),
                       input=stdin,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT,
                       env=self.env,
                       shell=True,
                       )
    output = self.trace_console(p, decode_stdout)
    if output==None:
      return None
    if print_stdout==True and type(output)!=bytes:
      print(output)
    if log_stdout==True and type(output)!=bytes:
      self.dump(output, 'syntax_pipeline.log')
    if return_stdout==True:
      return output
      
  def trace_console(self, p, decode_stdout):
    if decode_stdout:
      return p.stdout.decode('utf-8')
    return p.stdout
  
if __name__ == '__main__':
  pass
