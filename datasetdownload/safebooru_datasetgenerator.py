import bs4
import sys
import urllib.request, urllib.error, urllib.parse
import http.client
from socket import error as SocketError
import ssl
import os.path
import argparse
import datetime
import pickle
import signal
import http.cookiejar
import re
import json
import random
from multiprocessing import Pool  
from multiprocessing import Process, Queue
import multiprocessing as mp
from concurrent import futures
import time
from threading import Thread as Th
import glob

def html_fetcher(url, phost):
  html = None
  for ret in range(10) :
    headers = {"Accept-Language": "en-US,en;q=0.5","User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Referer": "http://thewebsite.com","Connection": "keep-alive" } 
    request = urllib.request.Request(url=url, headers=headers)
    proxy = urllib.request.ProxyHandler({'http': phost})
    opener = urllib.request.build_opener(proxy)
    #opener = urllib.request.build_opener()
    TIME_OUT = 10.
    try:
      html = opener.open(request, timeout=TIME_OUT).read()
    except Exception as e:
      print( e )
      continue
  if html == None:
    return (None, None, None)
  soup = bs4.BeautifulSoup(html, "html.parser")
  title = (lambda x:str(x.string) if x != None else 'Untitled')(soup.title )
  return (html, title, soup)

def exit_gracefully(signum, frame):
  signal.signal(signal.SIGINT, original_sigint)
  try:
    if input("\nReally quit? (y/n)> ").lower().startswith('y'): sys.exit(1)
  except KeyboardInterrupt:
    print("Ok ok, quitting")
    sys.exit(1)
  signal.signal(signal.SIGINT, exit_gracefully)

def analyzing(inputs) -> str:
  url, index, phost = inputs
  burl = bytes(url, 'utf-8')
  html, title, soup = html_fetcher(url, phost)
  if soup is None:
    print('except miss')
    return None
  img = soup.find('img', {'id':'image'} )
  if img is None:
    return None
  img_url = 'https:{}'.format(img.get('src'))
  data_tags = img.get('alt')
  for trial in range(15):
    try:
      proxy = urllib.request.ProxyHandler({'http': phost})
      opener  = urllib.request.build_opener(proxy)
      #opener  = urllib.request.build_opener()
      request = urllib.request.Request(url=img_url)
      con = opener.open(request, timeout=10.0).read()
    except Exception as e:
      print( phost )
      print('aaa', e )
      time.sleep(1.)
      continue
    save_name = re.sub(r'\?.*$', '', img_url)
    break

  try:
    save_name = save_name
    open('imgs/{name}.jpg'.format( name=save_name.split('/')[-1] ), 'wb').write(con)
    open('imgs/{name}.txt'.format( name=save_name.split('/')[-1] ), 'w').write(data_tags)
    open('imgs/{name}.url'.format( name=save_name.split('/')[-1] ), 'w').write(url)
    open('finished/{index}'.format(index=index), 'w').write('flag')
    print('complete storing image of {url}'.format(url=img_url) )
  except UnboundLocalError as e:
    print( e )

if __name__ == '__main__':
  original_sigint = signal.getsignal(signal.SIGINT)
  signal.signal(signal.SIGINT, exit_gracefully)
  parser = argparse.ArgumentParser(description='Process Safebooru image tag scraper.')
  parser.add_argument('--mode', help='you can specify mode...')
  parser.add_argument('--proxy', help='you can specify mode...')
  args_obj = vars(parser.parse_args())
  mode = (lambda x:x if x else 'undefined')( args_obj.get('mode') )
  proxy = (lambda x:x if x else 'undefined')( args_obj.get('proxy') )
  phosts = ['http://{proxy}:{proxy}awr003@{phost}:8086'.format(proxy=proxy, phost=phost.strip()) for phost in open('proxys.txt')] 
  if mode == 'scrape':
    finished = set(name.split('/')[-1] for name in glob.glob('./finished/*'))
    samples  = filter( lambda x: str(x) not in finished, range(1, 2653427))
    urls = [ ('http://safebooru.org/index.php?page=post&s=view&id={i}'.format(i=i), i, random.choice(phosts)) for i in samples]
    random.shuffle(urls)
   
    #[ analyzing(url) for url in urls ] 
    # 元々は768で並列処理
    with futures.ProcessPoolExecutor(max_workers=100) as executor:
      executor.map( analyzing, urls )
