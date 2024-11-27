import sys
import traceback
import collections

class KnownException(Exception):
 pass

# Place it here to avoid circular dependecies
from game_record import GameRecord

def ProcessRecordFile(fn: str, org_file: str, assert_reraise=False,
 other_reraise=True):
 """
 Processes a text file containing hands. Returns a list of GameRecord objects
 fn - path to the file
 org_file - for informational purpose only. Preferably the path relative
  to the base folder for all database files
 """
 print(f"Processing {fn} from {org_file}")
 error_count = 0
 assert_count = 0
 known_errors = collections.defaultdict(int)

 def __GenerateHand(lines, first_line):
  nonlocal fn, org_file, error_count, assert_count, known_errors
  h = GameRecord(fn, org_file, first_line)
  try:
   h.ParseLines(lines)
  except KnownException as ke:
   print(f"KNOWN EXCEPTION {ke} at line {h.ln+first_line} in {fn} " \
    f"from {org_file}")
   known_errors[str(ke)] += 1
   return None
  except AssertionError as ae:
   print(f"ASSERT {ae} at line {h.ln+first_line} in {fn} from {org_file}") 
   traceback.print_exc(file=sys.stdout)
   assert_count += 1
   if assert_reraise:
    raise ae
   return None
  except Exception as e:
   print(f"ERROR {e} at line {h.ln+first_line} in {fn} from {org_file}")
   traceback.print_exc(file=sys.stdout)
   error_count += 1
   if other_reraise:
    raise e
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

 return hands, known_errors, assert_count, error_count 
    
