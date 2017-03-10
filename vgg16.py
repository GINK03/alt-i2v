import keras
from keras.applications.vgg16 import VGG16 
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential, Model, Merge
from keras.layers import Input, Activation, Dropout, Flatten, Dense, Reshape, merge
from keras.preprocessing.image import ImageDataGenerator
from keras import optimizers
from keras.preprocessing.image import ImageDataGenerator
import numpy as np
import os
from PIL import Image
import glob 
import pickle
import sys

img_width, img_height = 150, 150
train_data_dir = './danbooru.imgs'
validation_data_dir = './imgs'
nb_train_samples = 2000
nb_validation_samples = 800
nb_epoch = 50
result_dir = 'results'

def build_dataset():
  Xs = []
  Ys = []
  keys = [name.replace('.txt', '') for name in glob.glob('imgs/*.txt')]
  tag_index = pickle.loads(open('tag_index.pkl', 'rb').read())
  for key in keys[:100]:
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
    img = img.convert('RGB')
    img = np.array(img.resize((150, 150)))
    img = np.expand_dims(img, axis=0)

    #print(key)
    #print(list(filter(lambda x:x!=0.,vec)))
    #print(img.shape)
    Ys.append(vec)
    Xs.append(img)
  return Xs, Ys

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
  #for tag, index in tag_index.items():
  #  print(tag, index)

def build_model():
  input_tensor = Input(shape=(150, 150, 3))
  vgg16_model = VGG16(include_top=False, weights='imagenet', input_tensor=input_tensor)
  w1 = Flatten()(vgg16_model.layers[14].output)
  w2 = Flatten()(vgg16_model.layers[10].output)
  w3 = Flatten()(vgg16_model.layers[6].output)
  dense  = Flatten()(Dense(512, activation='relu')(vgg16_model.layers[-1].output))
  merged = merge([w1, dense, w2, w3], mode='concat')
  dense2 = Dense(4096)(merged)
  acted  = Activation('sigmoid')(dense2)
  print('vgg16_model:', vgg16_model)
  model = Model(input=vgg16_model.input, output=acted)
  sgd = optimizers.SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
  model.compile(loss='binary_crossentropy', optimizer=sgd)
  return model
  #for i in range(len(model.layers)):
  #  print(i, model.layers[i])
  # 最後のconv層の直前までの層をfreeze
  #for layer in model.layers[:15]:
  #  layer.trainable = False
  #model.summary()

if __name__ == '__main__':
  if '--maeshori' in sys.argv:
    tag2index()
  if '--test' in sys.argv:
    Xs, Ys = build_dataset()
    model = build_model()
    model.fit([Xs[0]], np.array([Ys[0]]), batch_size=32, nb_epoch=15 )
  pass
