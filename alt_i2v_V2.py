import keras
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential, Model, load_model
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
import msgpack
import numpy as np
import json

from keras.applications.vgg16 import VGG16 
input_tensor = Input(shape=(224, 224, 3))
vgg16_model = VGG16(include_top=False, weights='imagenet', input_tensor=input_tensor)
dense  = Flatten()( \
           Dense(6000, activation='relu')( \
             BN()( \
         vgg16_model.layers[-1].output ) ) )
result = Activation('sigmoid')(\
           Activation('linear')( \
              Dense(5000)(\
                dense) ) )

model = Model(input=vgg16_model.input, output=result)
model.compile(loss='binary_crossentropy', optimizer='adam')

def train():
  print('load pickled dataset...')
  Xs = []
  ys = []
  for idx, name in enumerate( glob.glob('make_datapair/dataset/*.pkl') ):
    X,y = pickle.loads(open(name,'rb').read() ) 
    if idx >= 1000:
      break
    Xs.append( X )
    ys.append( y )
    print( X.shape )

  Xs = np.array( Xs )
  ys = np.array( ys )
  print( ys.shape )
  for i in range(100):
    model.fit(Xs, ys, epochs=1 )
    if i%1 == 0:
      model.save('models/model%05d.model'%i)

def eval():
  tag_index = pickle.loads(open('tag_index.pkl', 'rb').read())
  index_tag = { index:tag for tag, index in tag_index.items() }
  model = build_model()
  model = load_model(sorted(glob.glob('models/*.model'))[-1]) 
  Xs, Ys = loader(db='lexical_eval.ldb', th=100)
  for i in range(30):
    result = model.predict(np.array([Xs[i]]) )

    for i,w in sorted(result.items(), key=lambda x:x[1]*-1)[:30]:
      print(index_tag[i], i, w)

def pred():
  tag_index = pickle.loads(open('tag_index.pkl', 'rb').read())
  index_tag = { index:tag for tag, index in tag_index.items() }
  name_img150 = []
  for name in filter(lambda x: '.jpg' in x, sys.argv):
    img = Image.open('{name}'.format(name=name))
    img = img.convert('RGB')
    img150 = np.array(img.resize((150, 150)))
    name_img150.append( (name, img150) )
  model = load_model(sorted(glob.glob('models/*.model'))[-1]) 
  for name, img150 in name_img150:
    result = model.predict(np.array([img150]) )
    result = result.tolist()[0]
    result = { i:w for i,w in enumerate(result)}
    for i,w in sorted(result.items(), key=lambda x:x[1]*-1)[:30]:
      print("{name} tag={tag} prob={prob}".format(name=name, tag=index_tag[i], prob=w) )
if __name__ == '__main__':
  if '--maeshori' in sys.argv:
    tag2index()
  if '--build' in sys.argv:
    build_dataset()
  if '--train' in sys.argv:
    train()
  if '--eval' in sys.argv:
    eval()
  if '--pred' in sys.argv:
    pred()
