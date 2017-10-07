import os
import math
from PIL import Image
import pickle
import numpy as np
import glob
import json
import random
import sys
if '--make_tag_index' in sys.argv:
  tag_freq = {}
  for name in glob.glob('../datasetdownload/imgs/*.txt'):
    for tag in open(name).read().split():
      if tag_freq.get(tag) is None:
        tag_freq[tag] = 0
      tag_freq[tag] += 1

  tag_index = {}
  tags = [tag for tag, freq in sorted( tag_freq.items(), key=lambda x:x[1]*-1)[:5000]]
  random.shuffle( tags )

  for tag in tags:
    print( tag )
    tag_index[tag] = len(tag_index)

  open('tag_index.pkl', 'wb').write( pickle.dumps(tag_index) )

if '--make_pair' in sys.argv:
  tag_index = pickle.loads( open('tag_index.pkl', 'rb').read() )
  target_size = (224,224)
  for name in glob.glob('../datasetdownload/imgs/*.txt'):
    img_name = name.replace('.txt', '.jpg')
    if not os.path.exists(img_name):
      continue

    save_name = 'dataset/{}.pkl'.format(img_name.split('/').pop().replace('.jpg', '') + '.pkl')
    if os.path.exists(save_name):
      continue
    img = Image.open(img_name)
    try:
      img = img.convert('RGB')
    except OSError as e:
      continue
  
    w, h = img.size
    if w > h :
      blank = Image.new('RGB', (w, w))
    if w <= h :
      blank = Image.new('RGB', (h, h))
    blank.paste(img, (0, 0) )
    blank = blank.resize( target_size )
    X = np.asanyarray(blank)
    X = X / 255.0
    y = [0.0]*len(tag_index)
    for tag in open(name).read().split():
      if tag_index.get(tag) is None:
        continue
      index = tag_index[tag]
      y[ index ] = 1.0
    if all(map(lambda x:x==0.0, y)):
      continue
    #print( X )
    #print( y )
    print( name )

    open(save_name, 'wb').write( pickle.dumps( (X,y) ) )
