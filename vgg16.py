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
img_width, img_height = 150, 150
train_data_dir = './danbooru.imgs'
validation_data_dir = './imgs'
nb_train_samples = 2000
nb_validation_samples = 800
nb_epoch = 50
result_dir = 'results'

def loader():
  db = plyvel.DB('lexical.ldb', create_if_missing=False)
  Xs, Ys = [], []
  for img, vec in db:
    img = msgpack.unpackb(img, object_hook=m.decode) 
    Xs.append(img)
    vec = msgpack.unpackb(vec, object_hook=m.decode) 
    Ys.append(vec)
  return Xs,Ys

def build_dataset() -> None:
  db = plyvel.DB('lexical.ldb', create_if_missing=True)
  print("A")
  keys = [name.replace('.txt', '') for name in glob.glob('/mnt/sdb1/alt-i2v/alt-i2v/danbooru.imgs/*.txt')]
  print("B")
  tag_index = pickle.loads(open('/mnt/sdb1/alt-i2v/alt-i2v/tag_index.pkl', 'rb').read())
  print("C")
  for ki, key in enumerate(keys):
    if ki%100 == 0:
      print('iter {}'.format(ki))
    vec = [0.]*len(tag_index)
    raw = open('{key}.txt'.format(key=key)).read().split('\n')
    text_tags = raw[0].split()
    for tag in text_tags:
      #print(text_tags)
      if tag_index.get(tag) is not None:
        vec[tag_index[tag]] = 1.
    try:
      json_tag  = raw[1]
    except IndexError as e:
      pass
    
    img = Image.open('{key}.jpg'.format(key=key))
    try:
      img = img.convert('RGB')
    except OSError as e:
      continue
    img = np.array(img.resize((150, 150)))
    vec = np.array(vec)
    img = msgpack.packb(img, default=m.encode)
    vec = msgpack.packb(vec, default=m.encode)
    db.put(img, vec)
  return None

def tag2index():
  keys = [name for name in glob.glob('imgs/*.txt')]
  tags_freq = {}
  for key in keys:
    raw = open('{key}'.format(key=key)).read().split('\n')
    text_tags = raw[0].split()
    for tag in text_tags:
      if tags_freq.get(tag) is None :
        tags_freq[tag] = 0
      tags_freq[tag] += 1
    try:
      json_tag  = raw[1]
    except IndexError as e:
      pass
  tag_index = {}
  for tag, freq in sorted(tags_freq.items(), key=lambda x:x[1]*-1)[:4096]:
    tag_index[tag] = len(tag_index)
    print(tag, len(tag_index), freq)  
  open('tag_index.pkl', 'wb').write(pickle.dumps(tag_index))

def build_model():
  input_tensor = Input(shape=(150, 150, 3))
  vgg16_model = VGG16(include_top=False, weights='imagenet', input_tensor=input_tensor)
  #w1 = Flatten()(vgg16_model.layers[14].output)
  dense  = Flatten()( \
               Dense(128, activation='relu')( \
	           vgg16_model.layers[-1].output ) ) 
  result = Activation('sigmoid')(\
             Dense(4096)(\
               dense) ) 
  
  model = Model(input=vgg16_model.input, output=result)
  for i in range(len(model.layers)):
    print(i, model.layers[i])
  for layer in model.layers[:15]:
    layer.trainable = False
  model.compile(loss='binary_crossentropy', optimizer='sgd')
  return model

if __name__ == '__main__':
  print('b')
  if '--maeshori' in sys.argv:
    tag2index()
  if '--build' in sys.argv:
    build_dataset()
  if '--train' in sys.argv:
    Xs, Ys = loader()
    model = build_model()
    for i in range(20):
      model.fit(np.array(Xs), np.array(Ys), batch_size=16, nb_epoch=1 )
      if i%1 == 0:
        from multiprocessing import Process
        saver = lambda x:model.save('models/model%05d'%i)
        p = Process(target=saver, args=(None,))
        p.start()
  pass
