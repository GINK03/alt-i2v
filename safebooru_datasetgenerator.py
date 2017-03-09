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
from concurrent import futures
def html_adhoc_fetcher(url):
  html = None
  retrys = [i for i in range(10)]
  for _ in retrys :
    headers = {"Accept-Language": "en-US,en;q=0.5","User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Referer": "http://thewebsite.com","Connection": "keep-alive" } 
    request = urllib.request.Request(url=url, headers=headers)
    opener = urllib.request.build_opener()
    _TIME_OUT = 10.
    try:
      html = opener.open(request, timeout = _TIME_OUT).read()
    except EOFError as e:
      print('[WARN] Cannot access url with EOFError, try number is...', e, _, url, mp.current_process() )
      continue
    except urllib.error.URLError as e:
      #print('[WARN] Cannot access url with URLError, try number is...', e, _, url, mp.current_process() )
      continue
    except urllib.error.HTTPError as e:
      print('[WARN] Cannot access url with urllib2.httperror, try number is...', e, _, url, mp.current_process() )
      continue
    except ssl.SSLError as e:
      print('[WARN] Cannot access url with ssl error, try number is...', e, _, url, mp.current_process() )
      continue
    except http.client.BadStatusLine as e:
      print('[WARN] Cannot access url with BadStatusLine, try number is...', e, _, url, mp.current_process() )
      continue
    except http.client.IncompleteRead as e:
      print('[WARN] Cannot access url with IncompleteRead, try number is...', e, _, url, mp.current_process() )
      continue
    except SocketError as e:
      print('[WARN] Cannot access url with SocketError, try number is...', e, _, url, mp.current_process() )
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

if __name__ == '__main__':
  # store the original SIGINT handler
  original_sigint = signal.getsignal(signal.SIGINT)
  signal.signal(signal.SIGINT, exit_gracefully)
  parser = argparse.ArgumentParser(description='Process Kindle Referenced Index Score.')
  parser.add_argument('--URL', help='set default URL which to scrape at first')
  parser.add_argument('--depth', help='how number of url this program will scrape')
  parser.add_argument('--mode', help='you can specify mode...')
  parser.add_argument('--refresh', help='create snapshot(true|false)')
  parser.add_argument('--file', help='input filespath')
  parser.add_argument('--active', help='spcific active thread number')
  args_obj = vars(parser.parse_args())
  depth      = (lambda x:int(x) if x else 10)( args_obj.get('depth') )
  mode       = (lambda x:x if x else 'undefined')( args_obj.get('mode') )
  refresh    = (lambda x:False if x=='false' else True)( args_obj.get('refresh') )
  active     = (lambda x:15 if x==None else int(x) )( args_obj.get('active') )
  filename   = args_obj.get('file')

  if mode == 'scrape':
    from threading import Thread as Th
    import glob
    
    def analyzing(inputs) -> str:
      url, index = inputs
      burl = bytes(url, 'utf-8')
      html, title, soup = html_adhoc_fetcher(url)
      if soup is None:
        print('except miss')
        return str(False)
      sec = soup.find('section', {'id':'image-container'})
      if sec.find('img') is None:
        print('except no contents')
        open('./finished/{index}'.format(index=index), 'w').write("n")
        return str(False)
      img_url = 'http://safebooru.donmai.us{}'.format(sec.find('img').get('src'))
      data_tags = sec.find('img').get('data-tags')
      def _i(img_url, data_tags, index):
        opener  = urllib.request.build_opener()
        request = urllib.request.Request(url=img_url)
        con = opener.open(request).read()
        open('./imgs/{}.jpg'.format( img_url.split('/')[-1] ), 'wb').write(con)
        open('./imgs/{name}.txt'.format(name=img_url.split('/')[-1] ), 'w').write(data_tags)
        open('./finished/{index}'.format(index=index), 'w').write("f")
        print('complete storing image of {url}'.format(url=img_url) )
      th = Th(target=_i, args=(img_url, data_tags, index,))
      th.start()
      return sec.find('img').get('data-tags')
    
    finished = set(name.split('/')[-1] for name in glob.glob('./finished/*'))
    samples  = filter( lambda x:x not in finished, range(1, 2653427))
    urls = [ ('http://safebooru.donmai.us/posts/{i}'.format(i=i), i) for i in samples]
    random.shuffle(urls)
    
    with futures.ProcessPoolExecutor(max_workers=768) as executor:
      mappings = {executor.submit(analyzing, url): url for url in urls}
      for future in futures.as_completed(mappings):
        input_arg = mappings[future]
        result = future.result()
        msg = '{n}: {result}'.format(n=input_arg, result=result)
        print(msg)
  
  if mode == 'chaine':
    import os
    db = plyvel.DB('./tmp/pixiv_htmls', create_if_missing=False)

