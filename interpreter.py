from argparse import ArgumentParser


def parse_hrm(filepath):
  opcodes = []
  jumps = {}
  for line in open(filepath):
    if line.startswith('    '):
      opcodes.append(line.strip().split())
    elif line[1] == ':':
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
      print ' '.join('%d:%s' % (i,x) for i,x in enumerate(memory)
                     if x is not None)
      print ip, hand, inst
    op = inst[0]
    if op == 'INBOX':
      if not inbox:
        return
      hand = inbox.pop()
    elif op == 'OUTBOX':
      print '>>', hand
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
      raise ValueError('Operation NYI:', op)
    ip += 1


def main():
  ap = ArgumentParser()
  ap.add_argument('--verbose', action='store_true')
  ap.add_argument('--memsize', type=int, default=25,
                  help='size of memory (floor), default = %(default)s')
  ap.add_argument('--initmem', nargs='*', default=[],
                  help='pairs of [index value] to initialize memory with')
  ap.add_argument('program')
  ap.add_argument('inbox', nargs='+', help='space-separated inbox values')
  args = ap.parse_args()
  if len(args.initmem) % 2 != 0:
    ap.error('Must provide pairs to --initmem')

  memory = initialize_memory(args.memsize, args.initmem)
  opcodes, jumps = parse_hrm(args.program)
  inbox = [int(x) if x.isdigit() else x.upper() for x in args.inbox[::-1]]
  run_program(opcodes, jumps, memory, inbox, verbose=args.verbose)


if __name__ == '__main__':
  main()
