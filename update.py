# Last Updated | 2019-11-14

from datetime import datetime
from typing import List

def update_metadata():
  pass

def update_ms_txt():
  pass

def update_all():
  pass

def update_time():
  """ Extract timestamp at the top of this file and update it. """
  # Initialize date to write and container for the text
  now_str = str(datetime.now()).split(' ')[0]
  lines = []

  # open file, extract text, and modify
  with open('./update.py', 'r') as f:
    lines = f.read().split('\n')
    lines[0] = "# Last Updated | " + now_str
  
  # write modified text
  f = open('./update.py', 'w')
  f.write('\n'.join(lines))
  f.close

def update():
  """ Run each update function. """
  update_metadata()
  update_ms_txt()
  update_all()
  update_time()
  print('updated!')

update()