import numpy as np
import turtle
from argparse import ArgumentParser
from base64 import decodestring
from zlib import decompress

'''TODO:
 * add a matplotlib-based plotter
 * add a path export function (for pasting back into HRM)
 * path cleanup (length reduction)
 * handwriting -> ascii conversion?
'''


def parse_images(filepath):
  lines = iter(open(filepath))
  while True:
    # clever trick!
    # when next() raises StopIteration, it stops this generator too
    line = next(lines)
    if not line.startswith('DEFINE '):
      continue
    _, kind, number = line.split()
    number = int(number)
    raw_data = ''
    while line[-1] != ';':
      line = next(lines).strip()
      raw_data += line
    # strip ; terminator
    raw_data = raw_data[:-1]
    # add base64 padding
    if len(raw_data) % 4 != 0:
      raw_data += '=' * (2 - (len(raw_data) % 2))
    # decode base64 -> decode zlib -> convert to byte array
    data = np.fromstring(decompress(decodestring(raw_data)), dtype=np.uint8)
    assert data.shape == (1028,)
    path_len, = data[:4].view(np.uint32)
    path = data[4:4+4*path_len].view(np.uint16).reshape((-1,2))
    yield kind, number, path


def main():
  ap = ArgumentParser()
  ap.add_argument('--speed', type=int, default=10,
                  help='Number 1-10 for drawing speed, or 0 for no added delay')
  ap.add_argument('program')
  args = ap.parse_args()

  for kind, number, path in parse_images(args.program):
    title = '%s #%d, path length %d' % (kind, number, path.shape[0])
    print title
    if not path.size:
      continue
    pen_up = (path==0).all(axis=1)
    # convert from path (0 to 65536) to turtle coords (0 to 655.36)
    path = path / 100.
    turtle.title(title)
    turtle.speed(args.speed)
    turtle.setworldcoordinates(0, 655.36, 655.36, 0)
    turtle.pen(shown=False, pendown=False, pensize=10)
    for i in xrange(path.shape[0]):
      if pen_up[i]:
        turtle.penup()
      else:
        turtle.setpos(path[i])
        turtle.pendown()
        turtle.dot(size=10)
    raw_input('Press enter to continue')
    turtle.clear()
  turtle.bye()


if __name__ == '__main__':
  main()
