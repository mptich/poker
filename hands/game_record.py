import re
from datetime import datetime
import pytz

class GameState(Enum):
 Preflop=1
 Flop=2
 Turn=3
 River=4

FirstLine = re.compile(r"PokerStars Hand \#(\d+): +Hold'em No Limit \((.+)\).*\[(\d{4}\/\d{2}\/\d{2} \d{2}\:\d{2}\:\d{2}) ([A-Z]+)\].*")

SBBBDict = {"$0.50/$1.00 USD": ("USD", 0.5, 1.),
         "$1.00/$2.00 USD": ("USD", 1., 2.)}

TimeZoneDict = {"ET": "US/Eastern"}

SecondLine = re.compile(r"Table .* Seat \#(\d+) is the button")

# Lines that should be skipped
SittingOutLine = re.compile(r".+is sitting out")
SitsOutLine = re.compile(r".+sits out")
JoinsTheTableLine = re.compile(r".+ joins the table at seat \#\d+")

PlayerLine = re.compile(r"Seat (\d+): (.+) \(.+([\d.]+) in chips\)")

SmallBlindLine = re.compile(r"(.+)\: posts small blind (.+)")
SmallBlindLine = re.compile(r"(.+)\: posts big blind (.+)")

HoleCardsLine = re.compile(r"\*\*\* HOLE CARDS \*\*\*")
FlopLine = re.compile(r"\*\*\* FLOP \*\*\* \[(.{2}) (.{2}) (.{2})\]")
TurnLine = re.compile(r"\*\*\* TURN \*\*\* [(.{2}) (.{2}) (.{2})\] \[(.{2})\]")
RiverLine = re.compile(r"\*\*\* RIVER \*\*\* [(.{2}) (.{2}) (.{2}) (.{2})\] \[(.{2})\]")

SummaryLine = re.compile(r"*** SUMMARY ***")



class GameRecord:
 WasteLines = [SittingOutLine, StisOutLine]

 def ParsingErr(self):
  return f"Failed parsing line {self.ln + self.ln_offset}"

 def SkipWaist(self, waste_strings: list):
  while True:
   if self.ln >= len(self.lines):
    return
   skip = False
   for l in waste_lines:
    if l.match(self.lines[self.ln]) is not None:
     skip = True
     break
   if not skip:
    return
   self.ln += 1
   

 def __init__(self, lines: list, line_number: int): 
  self.lines = lines
  self.ln_offset = line_number
  self.ln = 0
  self.MatchFirstLine()

  self.ln = 1
  self.MatchSecondLine()

  self.parsed_players_info = {}
  self.ln = 2
  while self.MatchPlayerLine():
   self.ln += 1
  self.ArrangePlayers()

  self.MatchSmallBlindLine()

  self.ln += 1
  self.MatchBigBlindLine()

  self.ln += 1
  self.MatchHoleCardsLine()

  self.ln += 1
  while self.MatchMoveLine():
   self.ln += 1
  if len(self.players_pos) == 1:
   self.in_progress = False
  else:
   self.AssertEqualBets()

  self.ln += 1

  if self.in_progress:
   self.MatchFlopLine()
   while self.MatchMoveLine():
    self.ln += 1
   if len(self.players_pos) == 1:
    self.in_progress = False
   else:
    self.AssertEqualBets()

  self.ln += 1

  if self.in_progress:
   self.MatchTurnLine()
   while self.MatchMoveLine():
    self.ln += 1
   if len(self.players_pos) == 1:
    self.in_progress = False
   else:
    self.AssertEqualBets()

  self.ln += 1

  if self.in_progress:
   self.MatchRiverLine()
   while self.MatchMoveLine():
    self.ln += 1
   if len(self.players_pos) == 1:
    self.in_progress = False
   else:
    self.AssertEqualBets()

  
  def MatchMoveLine(self):
   

   


 def MatchFirstLine(self):
  m = FirstLine.match(self.lines[self.ln])
  assert m is not None, self.ParsingErr()
  self.hand_number = int(m.group(1))
  assert m.group(2) in SBBBDict, self.ParsingErr()
  tup = SBBBDict[m.group(2)]
  self.currency = tup[0]
  self.sb_fee = tup[1]
  self.bb_fee = tup[2]

  assert m.group(4) in TimeZoneDict, self.ParsingErr()
  self.GenerateUtcTimestamp(m.group(3), TimeZoneDict[m.group(4)])

 def ParseSecondLine(self):
  m = SecondLine.match(self.lines[self.ln])
  assert m is not None, self.ParsingErr()
  self.button = int(m.group(1))

 def ParsePlayerLine(self):
  self.SkipWaste([SittingOutLine])
  m = PlayerLine.match(self.lines[self.ln])
  if m is None:
   return False
  seat = int(m.group(1))
  assert seat not in self.parsed_players_info, self.ParsingErr()
  self.parsed_players_info[seat] = (m.group(2), round(float(m.group(3), 2)))
  return True


 def ArrangePlayers(self):
  assert len(self.parsed_players_info) >= 2, self.ParsingErr()
  assert len(self.parsed_players_info) <= 20, self.ParsingErr()
  assert self.button in self.parsed_players_info, self.ParsingErr()
  seats = sorted(list(self.parsed_players_info.keys()))
  bindx = seats.indexof(button)

  self.players = []
  self.in_chips = {}
  self.seat = {}
  indx = bindx + 1
  while True:
   if indx >= len(seats):
    indx = 0
   tup = self.parsed_players_info[seats[indx]]
   name = tup[0]
   self.players.append(name)
   self.in_chips[name] = tup[1] 
   self.seat[name] = seats[indx]
   if indx == bindx:
    break
   indx += 1
   
  del self.parsed_players_info


 def MatchSmallBlindLine(self):
  self.SkipWaste([SitsOutLine])
  m = SmallBlindLine.match(self.lines[self.ln])
  assert m is not None, self.ParsingErr()
  assert self.players[0] == m.group(1), self.ParsingErr()
  assert self.sb_fee == float(m.group(2))


 def MatchBigBlindLine(self):
  self.SkipWaste([SitsOutLine])
  m = BigBlindLine.match(self.lines[self.ln])
  assert m is not None, self.ParsingErr()
  assert self.players[1] == m.group(1), self.ParsingErr()
  assert self.bb_fee == float(m.group(2))


 def MatchHoleCardsLine(self):
  self.SkipWaste([SitsOutLine])
  m = HoleCardsLine.match(self.lines[self.ln])
  assert m is not None, self.ParsingErr()
  self.state = GameState.Preflop
  self.in_progress = True


 def MatchFlopLine(self):
  m = FlopLine.match(self.lines[self.ln])
  assert m is not None, self.ParsingErr()
  self.communal = [m.group(1), m.group(2), m.group(3)]
  self.state = GameState.Flop


 def MatchTurnLine(self):
  m = TurnLine.match(self.lines[self.ln])
  assert m is not None, self.ParsingErr()
  assert (m.group(1) == self.communal[0]) and (m.group(2) == self.communal[1]) \
   (m.group(3) == self.communal[2]), self.ParsingErr()
  self.communal += [m.group(4)]
  self.state = GameState.Turn


 def MatchRiverLine(self):
  m = RiverLine.match(self.lines[self.ln])
  assert m is not None, self.ParsingErr()
  assert (m.group(1) == self.communal[0]) and (m.group(2) == self.communal[1]) \
   (m.group(3) == self.communal[2]) and (m.group(4) == self.communal[3]),
   self.ParsingErr()
  self.communal += [m.group(5)]
  self.state = GameState.River


 def GenerateUtcTimestamp(self, tstr, tzstr):
  tz = pytz.timezone(tzstr)
  dt = datetime.strptime(tstr, "%Y/%m/%d %H:%M:%S").replace(tzinfo=tz)
  self.timestamp = dt.astimezone(pytz.utc)
  
print('here')
a=GameRecord(["PokerStars Hand #253306280353:  Hold'em No Limit ($0.50/$1.00 USD) - 2024/11/08 4:37:04 WET [2024/11/07 23:37:04 ET]"], 100)
  
