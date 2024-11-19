import re
from datetime import datetime
import pytz
from enum import Enum
import collections

class GameState(Enum):
 Preflop=1
 Flop=2
 Turn=3
 River=4

FirstLine = re.compile(r"PokerStars Hand \#(\d+): +Hold'em No Limit \((.+)\).*\[(\d{4}\/\d{2}\/\d{2} \d{1,2}\:\d{1,2}\:\d{1,2}) ([A-Z]+)\].*")

SBBBDict = {"$0.50/$1.00 USD": ("USD", 0.5, 1.),
         "$1.00/$2.00 USD": ("USD", 1., 2.)}

TimeZoneDict = {"ET": "US/Eastern"}

SecondLine = re.compile(r"Table .* Seat \#(\d+) is the button")

# Lines that should be skipped
SittingOutLine = re.compile(r"(.+) is sitting out")
SitsOutLine = re.compile(r"(.+) sits out")
JoinsTheTableLine = re.compile(r"(.+) joins the table at seat \#\d+")
LeavesTheTableLine = re.compile(r"(.+) leaves the table")
TimedOutLine = re.compile(r"(.+) has timed out.*")
ConnectedLine = re.compile(r"(.+) is (dis)?connected.*")

PlayerLine = re.compile(r"Seat (\d+): (.+) \([^\d.]*([\d.]+) in chips\)")

SmallBlindLine = re.compile(r"(.+)\: posts small blind [^\d.]*([\d.]+)")
BigBlindLine = re.compile(r"(.+)\: posts big blind [^\d.]*([\d.]+)")
BothBlindsLine = re.compile(r"(.+): posts small \& big blinds [^\d.]*([\d.]+)")

HoleCardsLine = re.compile(r"\*\*\* HOLE CARDS \*\*\*")
FlopLine = re.compile(r"\*\*\* FLOP \*\*\* \[(.{2}) (.{2}) (.{2})\]")
TurnLine = re.compile(r"\*\*\* TURN \*\*\* \[(.{2}) (.{2}) (.{2})\] \[(.{2})\]")
RiverLine = re.compile(r"\*\*\* RIVER \*\*\* \[(.{2}) (.{2}) (.{2}) (.{2})\] \[(.{2})\]")

# Moves
FoldsLine = re.compile(r"(.+): folds")
ChecksLine = re.compile(r"(.+): checks")
BetsLine = re.compile(r"(.+): bets [^\d.]*([\d.]+)( and is all-in)?")
CallsLine = re.compile(r"(.+): Calls [^\d.]*([\d.]+)( and is all-in)?")
RaisesLine = re.compile(r"(.+): raises [^\d.]*([\d.]+) to [^\d.]*([\d.]+)( and is all-in)?")

SummaryLine = re.compile(r"\*\*\* SUMMARY \*\*\*")


# See game_record_attrib_desc.txt for attribute description
class GameRecord:
 def ProcessPerUserWasteLine(self, m):
  assert m.group(1) not in self.players


 def ProcessIgnoreWasteLine(self, m):
  pass


 WasteLines = [([SittingOutLine, SitsOutLine, JoinsTheTableLine,
  LeavesTheTableLine], ProcessPerUserWasteLine),
  ([TimedOutLine, ConnectedLine], ProcessIgnoreWasteLine)]


 def SkipWaste(self):
  # Each element in waste_list is a tuple consisting of the list of lines
  # and its processing function

  while True:
   good_line = True
   for e in self.WasteLines:
    for line in e[0]:
     m = line.match(self.lines[self.ln])
     if m is not None:
      e[1](self, m)
      self.ln += 1
      good_line = False
      break
    if not good_line:
     break 
   if good_line or (self.ln >= len(self.lines)):
    return
   

 def __init__(self):
  pass


 def ParseLines(self, lines: list): 
  self.lines = lines
  self.ln = 0
  self.players = []
  self.state = GameState.Invalid
  self.MatchFirstLine()

  self.ln = 1
  self.MatchSecondLine()

  self.parsed_players_info = {}
  self.ln = 2
  while self.MatchPlayerLine():
   self.ln += 1
  self.ProcessPlayers()

  self.sb_found = self.bb_found = False
  while self.MatchBlindsLine():
   self.ln += 1
  assert self.sb_found and self.bb_found
  del self.sb_found
  del self.bb_found
  self.current_bet = self.bb_fee

  self.MatchHoleCardsLine()
  self.ln += 1

  self.index_in_pos = 2 % len(self.players_pos)
  self.all_in_state_val = 999 # Very high
  while self.MatchMoveLine():
   self.ln += 1
  if len(self.players_pos) == 1:
   self.in_progress = False
  else:
   self.AssertEqualBets()

  if self.in_progress:
   self.MatchFlopLine()
   self.ln += 1
   self.index_in_pos = 0
   while self.MatchMoveLine():
    self.ln += 1
   if len(self.players_pos) == 1:
    self.in_progress = False
   else:
    self.AssertEqualBets()

  if self.in_progress:
   self.MatchTurnLine()
   self.ln += 1
   self.index_in_pos = 0
   while self.MatchMoveLine():
    self.ln += 1
   if len(self.players_pos) == 1:
    self.in_progress = False
   else:
    self.AssertEqualBets()

  if self.in_progress:
   self.MatchRiverLine()
   self.ln += 1
   self.index_in_pos = 0
   while self.MatchMoveLine():
    self.ln += 1
   if len(self.players_pos) == 1:
    self.in_progress = False
   else:
    self.AssertEqualBets()

  del self.index_in_pos
  
 def MatchMoveLine(self):
  self.SkipWaste()
  if self.all_in_state_val < self.state.value:
   return False

  m = FoldsLine.match(self.lines[self.ln]) 
  if m is not None:
   index = self.players.index(m.group(1))
   assert self.players[self.players_pos[self.index_in_pos]] == m.group(1)
   if m.group(1) in self.special_bet:
    assert self.bet[m.group(1)] == self.sb_fee+self.bb_fee
    self.special_bet.remove(m.group(1))
   self.players_pos.pop(self.index_in_pos)
   self.index_in_pos %= len(self.players_pos)
   return True

  m = ChecksLine.match(self.lines[self.ln])
  if m is not None:
   index = self.players.index(m.group(1))
   assert self.players[self.players_pos[self.index_in_pos]] == m.group(1)
   self.index_in_pos += 1
   self.index_in_pos %= len(self.players_pos)
   return True


  m = BetsLine.match(self.lines[self.ln])
  if m is not None:
   assert self.players[self.players_pos[self.index_in_pos]] == m.group(1)
   amount = float(m.group(2))
   self.bet[m.group(1)] += amount
   assert self.bet[m.group(1)] > self.current_bet
   self.current_bet = self.bet[m.group(1)]
   if self.current_bet >= self.sb_fee+self.bb_fee:
    # Special bets are no longer valid
    self.special_bet = set()
   self.index_in_pos += 1
   self.index_in_pos %= len(self.players_pos)
   if m.group(3) is not None:
    self.all_in_state_val = self.state.value
   return True


 def AssertEqualBets(self):
  assert len(self.players_pos) >= 2
  active_players = [self.players[x] for x in self.players_pos]
  active_bets = {x:self.bet[x] for x in active_players}
  min_bet = min(active_bets.values())
  max_bet = max(active_bets.values())
  if min_bet != max_bet:
   assert max_bet == self.sb_fee + self.bb_fee
   for p,b in active_bets.items:
    assert (b == min_bet) or ((b == max_bet) and (p in self.special_bets))
   

 def MatchFirstLine(self):
  m = FirstLine.match(self.lines[self.ln])
  assert m is not None
  self.hand_number = int(m.group(1))
  assert m.group(2) in SBBBDict
  tup = SBBBDict[m.group(2)]
  self.currency = tup[0]
  self.sb_fee = tup[1]
  self.bb_fee = tup[2]

  assert m.group(4) in TimeZoneDict
  self.GenerateUtcTimestamp(m.group(3), TimeZoneDict[m.group(4)])


 def MatchSecondLine(self):
  m = SecondLine.match(self.lines[self.ln])
  assert m is not None
  self.button = int(m.group(1))


 def MatchPlayerLine(self):
  self.SkipWaste()
  m = PlayerLine.match(self.lines[self.ln])
  if m is None:
   return False
  seat = int(m.group(1))
  assert seat not in self.parsed_players_info
  self.parsed_players_info[seat] = (m.group(2), round(float(m.group(3)), 2))
  return True


 def ProcessPlayers(self):
  player_count = len(self.parsed_players_info)
  assert player_count >= 2
  assert player_count <= 20
  assert self.button in self.parsed_players_info
  seats = sorted(list(self.parsed_players_info.keys()))
  bindx = seats.index(self.button)

  self.in_chips = {}
  self.seat = {}
  self.bet = collections.defaultdict(float)
  self.special_bets = set()
  indx = bindx + 1 if player_count > 2 else bindx
  for _ in range(player_count):
   if indx >= len(seats):
    indx = 0
   tup = self.parsed_players_info[seats[indx]]
   name = tup[0]
   self.players.append(name)
   self.in_chips[name] = tup[1] 
   self.seat[name] = seats[indx]
   indx += 1
  self.players_pos = list(range(player_count))
   
  del self.parsed_players_info


 def MatchBlindsLine(self):
  self.SkipWaste()
  m = SmallBlindLine.match(self.lines[self.ln])
  if m is not None:
   assert m.group(1) in self.players
   assert float(m.group(2)) == self.sb_fee
   assert not self.bet[m.group(1)]
   self.bet[m.group(1)] = self.sb_fee
   if m.group(1) == self.players[0]:
    self.sb_found = True
   return True
   
  m = BigBlindLine.match(self.lines[self.ln])
  if m is not None:
   assert m.group(1) in self.players
   assert float(m.group(2)) == self.bb_fee
   assert not self.bet[m.group(1)]
   self.bet[m.group(1)] = self.bb_fee
   if m.group(1) == self.players[1]:
    self.bb_found = True
   return True

  m = BothBlindsLine.match(self.lines[self.ln])
  if m is None:
   return False
  assert m.group(1) in self.players
  assert float(m.group(2)) == self.sb_fee+self.bb_fee
  assert not self.bet[m.group(1)]
  self.bet[m.group(1)] = self.sb_fee+self.bb_fee
  self.special_bets.add(m.group(1))
  return True


 def MatchHoleCardsLine(self):
  self.SkipWaste()
  m = HoleCardsLine.match(self.lines[self.ln])
  assert m is not None
  self.state = GameState.Preflop
  self.in_progress = True


 def MatchFlopLine(self):
  m = FlopLine.match(self.lines[self.ln])
  assert m is not None
  self.communal = [m.group(1), m.group(2), m.group(3)]
  self.state = GameState.Flop


 def MatchTurnLine(self):
  m = TurnLine.match(self.lines[self.ln])
  assert m is not None
  assert (m.group(1) == self.communal[0]) and (m.group(2) == self.communal[1]) \
   (m.group(3) == self.communal[2])
  self.communal += [m.group(4)]
  self.state = GameState.Turn


 def MatchRiverLine(self):
  m = RiverLine.match(self.lines[self.ln])
  assert m is not None
  assert (m.group(1) == self.communal[0]) and (m.group(2) == self.communal[1]) \
   (m.group(3) == self.communal[2]) and (m.group(4) == self.communal[3])
  self.communal += [m.group(5)]
  self.state = GameState.River


 def GenerateUtcTimestamp(self, tstr, tzstr):
  tz = pytz.timezone(tzstr)
  dt = datetime.strptime(tstr, "%Y/%m/%d %H:%M:%S").replace(tzinfo=tz)
  self.timestamp = dt.astimezone(pytz.utc)

