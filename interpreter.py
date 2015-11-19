from __future__ import print_function
import sys
from argparse import ArgumentParser


def parse_hrm(filepath):
  opcodes = []
  jumps = {}
  for line in open(filepath):
    if line.startswith('    '):
      opcodes.append(line.strip().split())
    elif len(line) >= 2 and line[1] == ':':
      jumps[line[0]] = len(opcodes)
  return opcodes, jumps


def initialize_memory(memsize, initmem):
  memory = [None] * memsize
  for idx,val in zip(initmem[::2], initmem[1::2]):
    if val.isdigit():
      val = int(val)
    memory[int(idx)] = val
  return memory


def dereference(dest, memory):
  if dest[0] == '[':
    return memory[int(dest[1:-1])]
  return int(dest)


def run_program(opcodes, jumps, memory, inbox, verbose=False):
  hand = None
  ip = 0
  while True:
    inst = opcodes[ip]
    if verbose:
      memstr = ' '.join('%d:%s' % (i,x) for i,x in enumerate(memory)
                        if x is not None)
      print('DEBUG:', memstr)
      print('DEBUG:', ip, hand, inst)
    op = inst[0]
    if op == 'INBOX':
      val = next(inbox).strip()
      if len(val) == 1 and val.isalpha():
        hand = val.upper()
      else:
        hand = int(val)
    elif op == 'OUTBOX':
      yield hand
      hand = None
    elif op == 'COPYFROM':
      hand = memory[dereference(inst[1], memory)]
    elif op == 'COPYTO':
      memory[dereference(inst[1], memory)] = hand
    elif op == 'ADD':
      val = memory[dereference(inst[1], memory)]
      hand += val
    elif op == 'SUB':
      val = memory[dereference(inst[1], memory)]
      if isinstance(hand, str):
        hand = ord(hand) - ord(val)
      else:
        hand -= val
    elif op == 'BUMPUP':
      dest = dereference(inst[1], memory)
      memory[dest] += 1
      hand = memory[dest]
    elif op == 'BUMPDN':
      dest = dereference(inst[1], memory)
      memory[dest] -= 1
      hand = memory[dest]
    elif op == 'JUMP':
      ip = jumps[inst[1]]
      continue
    elif op == 'JUMPZ':
      if hand == 0:
        ip = jumps[inst[1]]
        continue
    elif op == 'JUMPN':
      if hand < 0:
        ip = jumps[inst[1]]
        continue
    elif op != 'COMMENT':
      raise ValueError('Invalid operation:', op)
    ip += 1


def main():
  ap = ArgumentParser()
  ap.add_argument('--verbose', action='store_true')
  ap.add_argument('--memsize', type=int, default=25,
                  help='size of memory (floor), default = %(default)s')
  ap.add_argument('--initmem', nargs='*', default=[],
                  help='pairs of [index value] to initialize memory with')
  ap.add_argument('--inbox', type=open, default=sys.stdin,
                  help='File of inbox values, one per line, default = stdin')
  ap.add_argument('program')
  args = ap.parse_args()
  if len(args.initmem) % 2 != 0:
    ap.error('Must provide pairs to --initmem')

  memory = initialize_memory(args.memsize, args.initmem)
  opcodes, jumps = parse_hrm(args.program)
  for out in run_program(opcodes, jumps, memory, args.inbox,
                         verbose=args.verbose):
    print(out)


if __name__ == '__main__':
  main()
