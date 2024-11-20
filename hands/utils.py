import traceback
import collections

class KnownException(Exception):
 pass

def FloatToInt(fl_str: str):
 """
 To convert money to integer number
 """
 return round(float(fl_str) * 1000)

# Place it here to avoid circular dependecies
from game_record import GameRecord

def ProcessRecordFile(fn: str, org_file: str):
 """
 Processes a text file containing hands. Returns a list of GameRecord objects
 """
 print(f"Processing {fn} from {org_file}")
 bad_error_count = 0
 known_errors = collections.defaultdict(int)

 def __GenerateHand(lines, first_line):
  nonlocal fn, org_file, bad_error_count, known_errors
  h = GameRecord()
  try:
   h.ParseLines(lines)
  except KnownException as ke:
   print(f"KNOWN EXCEPTION {ke} at line {h.ln+first_line} in {fn} " \
    f"from {org_file}")
   known_errors[str(ke)] += 1
   return None
  except Exception as e:
   print(f"ERROR {e} at line {h.ln+first_line} in {fn} from {org_file}") 
   traceback.print_exc()
   bad_error_count += 1
   return None
  return h

 hands = []
 lines = []
 with open(fn, 'r', encoding = "ISO-8859-1") as fin:
  for ln, l in enumerate(fin):
   l = l.strip()
   if (ln == 0) and l:
    # Some files have some junk in the first line
    for ind, c in enumerate(l):
     if c == 'P':
      break
    l = l[ind:]

   if l:
    if not lines:
     first_line = ln
    lines.append(l)
   else:
    if lines:
     h = __GenerateHand(lines, first_line)
     lines = []
     if h is not None:
      hands.append(h)

 if lines:
  h = __GenerateHand(lines, first_line)
  if h is not None:
   hands.append(h)

 return hands, known_errors, bad_error_count 
    
