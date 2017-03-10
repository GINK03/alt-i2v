import keras
from keras.applications.vgg16 import VGG16 
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential, Model, Merge
from keras.layers import Input, Activation, Dropout, Flatten, Dense, Reshape, merge
from keras.preprocessing.image import ImageDataGenerator
from keras import optimizers
from keras.preprocessing.image import ImageDataGenerator
from keras.layers.normalization import BatchNormalization as BN
import numpy as np
import os
from PIL import Image
import glob 
import pickle
import sys
import plyvel
import msgpack
import msgpack_numpy as m
import numpy as np
import json
img_width, img_height = 150, 150
train_data_dir = './danbooru.imgs'
validation_data_dir = './imgs'
nb_train_samples = 2000
nb_validation_samples = 800
nb_epoch = 50
result_dir = 'results'

def loader():
  db = plyvel.DB('lexical150.ldb', create_if_missing=False)
  Xs, Ys = [], []
  for img, vec in db:
    img = msgpack.unpackb(img, object_hook=m.decode) 
    Xs.append(img)
    vec = msgpack.unpackb(vec, object_hook=m.decode) 
    Ys.append(vec)
  return Xs,Ys

def build_dataset() -> None:
  db150 = plyvel.DB('lexical150.ldb', create_if_missing=True)
  dbeval = plyvel.DB('lexical_eval.ldb', create_if_missing=True)
  dbmemo = plyvel.DB('memo.ldb', create_if_missing=True)
  print("start to loading huge file system...")
  keys = [name.replace('.txt', '') for name in glob.glob('danbooru.imgs/*.txt')]
  print("complete to get file names ...")
  tag_index = pickle.loads(open('tag_index.pkl', 'rb').read())
  print("complete to get tag_index.pkl ...")
  kantai = list(filter(lambda x:'kantai' in x, keys))
  length = len(kantai)
  for ki, key in enumerate(kantai):
    if dbmemo.get(bytes(key, 'utf-8')) is not None:
      continue
    if ki%100 == 0:
      print('iter {}/{}'.format(ki, length))
    vec = [0.]*len(tag_index)
    raw = open('{key}.txt'.format(key=key)).read()
    try:
      json_tag = list(json.loads(open('{key}.metav1'.format(key=key)).read()).values())
    except FileNotFoundError as e:
      continue
    except OSError as e:
      continue
    except json.decoder.JSONDecodeError as  e:
      continue
    json_tag = list(map(lambda x:x.replace(' ', '_'), json_tag))
    text_tags = raw.split()

    for tag in sum([json_tag, text_tags], []):
      if tag_index.get(tag) is not None:
        vec[tag_index[tag]] = 1.
    try: 
      img = Image.open('{key}.jpg'.format(key=key))
    except OSError as e:
      continue
    try:
      img = img.convert('RGB')
    except OSError as e:
      continue
    img150 = np.array(img.resize((150, 150)))
    vec = np.array(vec)
    img150 = msgpack.packb(img150, default=m.encode)
    vec = msgpack.packb(vec, default=m.encode)
    if ki/length < 0.8:
      db150.put(img150, vec)
    else:
      dbeval.put(img150, vec)
    dbmemo.put(bytes(key, 'utf-8'), bytes('f', 'utf-8'))
  return None

def tag2index():
  keys = [name for name in glob.glob('danbooru.imgs/*.txt')]
  tags_freq = {}
  keys   = list(filter(lambda x:'kantai' in x, keys))
  length = len(keys)
  for ki, key in enumerate(keys):
    if ki%10000 == 0:
      print('now on iter {}/{}'.format(ki, length))
    raw = open('{key}'.format(key=key)).read().split('\n')
    text_tags = raw[0].split()
    for tag in text_tags:
      if tags_freq.get(tag) is None :
        tags_freq[tag] = 0
      tags_freq[tag] += 1
    metakey = "{}.metav1".format(key.replace('.txt', ''))
    try:
      dic = json.loads(open('{key}'.format(key=metakey)).read())
      for tag in map(lambda x:x.replace(' ', '_'), list(dic.values())):
        if tags_freq.get(tag) is None :
          tags_freq[tag] = 0
        tags_freq[tag] += 1
      #print(raw)
    except FileNotFoundError as e:
      continue
    except OSError as e:
      continue
    except json.decoder.JSONDecodeError as  e:
      continue
  tag_index = {}
  print('now building pkl file...')
  for tag, freq in sorted(tags_freq.items(), key=lambda x:x[1]*-1)[:4096]:
    tag_index[tag] = len(tag_index)
  open('tag_index.pkl', 'wb').write(pickle.dumps(tag_index))


def build_model():
  input_tensor = Input(shape=(150, 150, 3))
  vgg16_model = VGG16(include_top=False, weights='imagenet', input_tensor=input_tensor)
  #w1 = Flatten()(vgg16_model.layers[14].output)
  dense  = Flatten()( \
             Dense(2048, activation='relu')( \
               BN()( \
	         vgg16_model.layers[-1].output ) ) )
  result = Activation('sigmoid')(\
             Activation('linear')( \
	       Dense(4096)(\
                 dense) ) )
  
  model = Model(input=vgg16_model.input, output=result)
  for i in range(len(model.layers)):
    print(i, model.layers[i])
  for layer in model.layers[:12]: # default 15
    layer.trainable = False
  model.compile(loss='binary_crossentropy', optimizer='adam')
  return model

def train():
  Xs, Ys = loader()
  model = build_model()
  for i in range(30):
    model.fit(np.array(Xs[:3000]), np.array(Ys[:3000]), batch_size=16, nb_epoch=1 )
    if i%1 == 0:
      model.save('models/model%05d.model'%i)

if __name__ == '__main__':
  print('b')
  if '--maeshori' in sys.argv:
    tag2index()
  if '--build' in sys.argv:
    build_dataset()
  if '--train' in sys.argv:
    train()
