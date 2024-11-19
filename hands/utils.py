from game_record import GameRecord

def ProcessRecordFile(fn: str, org_file: str):
 """
 Processes a text file containing hands. Returns a list of GameRecord objects
 """
 print(f"Processing {fn} from {org_file}")

 hands = []
 lines = []
 with open(fn, 'r') as fin:
  first_line = None
  for ln, l in enumerate(fin):
   l = l.strip()
   if l:
    lines.append(l)
    if first_line is None:
     first_line = ln
   else:
    if lines:
     hands.append(GameRecord(lines=lines, line_number=first_line))
     lines = []
    first_line = None

 if lines:
  hands.append(GameRecord(lines=lines, line_number=ln))

 return hands 
    
