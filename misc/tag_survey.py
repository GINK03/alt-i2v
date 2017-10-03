
import glob
import os

def check_tag_freq():
  tag_freq = {}
  for name in glob.glob('./imgs/*.txt'):
    for tag in open(name).read().split():
      if tag_freq.get(tag) is None: tag_freq[tag] = 0
      tag_freq[tag] += 1

  for tag, freq in sorted(tag_freq.items(), key=lambda x:x[1]*-1):
    print(tag, freq)


if __name__ == '__main__':
  check_tag_freq()
