import re
from datetime import datetime
import pytz
from enum import Enum
import collections
from utils import KnownException

class GameState(Enum):
 Preflop=0
 Flop=1
 Turn=2
 River=3

DateTimeString = r"(\d{4}\/\d{2}\/\d{2} \d{1,2}\:\d{1,2}\:\d{1,2}) ([A-Z]+)"


FirstLine = re.compile(r"PokerStars Hand \#(\d+): +Hold'em No Limit \((.+)\) - " + DateTimeString + r"( \[" + DateTimeString + r"\])?")

SBBBDict = {"$0.50/$1.00 USD": ("USD", 0.5, 1.),
         "$1/$2 USD": ("USD", 1., 2.),
         "$2.50/$5.00 USD": ("USD", 2.50, 5.),
         "$3/$6 USD": ("USD", 3., 6.),
         "$5/$10 USD": ("USD", 5., 10.),
         "$10/$20 USD": ("USD", 10., 20.),
         "$25/$50 USD": ("USD", 25., 50.),
         "$50/$100 USD": ("USD", 50., 100.)}

TimeZoneDict = {"ET": "US/Eastern"}

CurrencyParams = {"USD": (1000., 2)}

SecondLine = re.compile(r"Table .* Seat \#(\d+) is the button")

# Lines that should be skipped
SittingOutLine = re.compile(r"(.+) is sitting out")
SitsOutLine = re.compile(r"(.+) sits out")
JoinsTheTableLine = re.compile(r"(.+) joins the table at seat \#\d+")
LeavesTheTableLine = re.compile(r"(.+) leaves the table")
TimedOutLine = re.compile(r"(.+) has timed out.*")
ConnectedLine = re.compile(r"(.+) is (dis)?connected.*")
AllowedToPlayLine = re.compile(r"(.+) will be allowed to play.*")

PlayerLine = re.compile(r"Seat (\d+): (.+) \([^\d.]*([\d.]+) in chips\)")

SmallBlindLine = re.compile(r"(.+)\: posts small blind [^\d.]*([\d.]+)")
BigBlindLine = re.compile(r"(.+)\: posts big blind [^\d.]*([\d.]+)")
BothBlindsLine = re.compile(r"(.+): posts small \& big blinds [^\d.]*([\d.]+)")
AnteLine = re.compile(r"(.+)\: posts the ante [^\d.]*([\d.]+)")

HoleCardsLine = re.compile(r"\*\*\* HOLE CARDS \*\*\*")
FlopLine = re.compile(r"\*\*\* FLOP \*\*\* \[(.{2}) (.{2}) (.{2})\]")
TurnLine = re.compile(r"\*\*\* TURN \*\*\* \[(.{2}) (.{2}) (.{2})\] \[(.{2})\]")
RiverLine = re.compile(r"\*\*\* RIVER \*\*\* \[(.{2}) (.{2}) (.{2}) (.{2})\] \[(.{2})\]")
FirstFlopLine = re.compile(r"\*\*\* FIRST FLOP.*") 
FirstTurnLine = re.compile(r"\*\*\* FIRST TURN.*")
FirstRiverLine = re.compile(r"\*\*\* FIRST RIVER.*")
ShowDownLine = re.compile(r"\*\*\* SHOW DOWN \*\*\*")
SummaryLine = re.compile(r"\*\*\* SUMMARY \*\*\*")

# Moves
FoldsLine = re.compile(r"(.+): folds")
ChecksLine = re.compile(r"(.+): checks")
BetsLine = re.compile(r"(.+): bets [^\d.]*([\d.]+)( and is all-in)?")
CallsLine = re.compile(r"(.+): calls [^\d.]*([\d.]+)( and is all-in)?")
RaisesLine = re.compile(r"(.+): raises [^\d.]*([\d.]+) to [^\d.]*([\d.]+)( and is all-in)?")
UncalledBetLine = re.compile(r"Uncalled bet \([^\d.]*([\d.]+)\) returned to (.+)")

CollectedLine = re.compile(r"(.+) collected [^\d.]*([\d.]+) from pot")
ShowsLine = re.compile(r"(.+): shows \[(.{2}) (.{2})\] \((.+)\)")
MucksLine = re.compile(r"(.+): mucks hand")
DoesNotShowLine = re.compile(r"(.+): doesn\'t show hand")

TotalPotLine = re.compile(r"Total pot [^\d.]*([\d.]+) \| Rake [^\d.]*([\d.]+)")


# See game_record_attrib_desc.txt for attribute description
class GameRecord:
 def ProcessPerUserWasteLine(self, m):
  if m.group(1) in self.players:
   raise KnownException("Weird repositioning")


 def ProcessIgnoreWasteLine(self, m):
  pass


 WasteLines = [([SittingOutLine, SitsOutLine, JoinsTheTableLine,
  AllowedToPlayLine], ProcessPerUserWasteLine),
  ([TimedOutLine, ConnectedLine, LeavesTheTableLine], ProcessIgnoreWasteLine)]


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
  self.MatchFirstLine()

  self.ln = 1
  self.MatchSecondLine()

  self.parsed_players_info = {}
  self.ln = 2
  while self.MatchPlayerLine():
   self.ln += 1
  self.ProcessPlayers()

  self.ante = 0
  self.contribs = []
  self.moves = [[],[],[],[]]
  self.sb_found = self.bb_found = False
  while self.MatchBlindsLine():
   self.ln += 1
  assert self.sb_found and self.bb_found
  del self.sb_found
  del self.bb_found
  if self.ante:
   # Ante was used. Make sure all players has paid it
   assert len(self.ante_players) == len(self.players)
   del self.ante_players
  self.current_bet = self.bb_fee

  self.MatchHoleCardsLine()
  self.ln += 1

  self.index_in_pos = 2 % len(self.active_pos)
  while self.MatchMoveLine():
   self.ln += 1
  self.AssertEqualBets()

  if self.in_progress:
   self.MatchFlopLine()
   self.ln += 1
   self.index_in_pos = 0 if len(self.players) > 2 else 1
   while self.MatchMoveLine():
    self.ln += 1
   self.AssertEqualBets()

  if self.in_progress:
   self.MatchTurnLine()
   self.ln += 1
   self.index_in_pos = 0 if len(self.players) > 2 else 1
   while self.MatchMoveLine():
    self.ln += 1
   self.AssertEqualBets()

  if self.in_progress:
   self.MatchRiverLine()
   self.ln += 1
   self.index_in_pos = 0 if len(self.players) > 2 else 1
   while self.MatchMoveLine():
    self.ln += 1
   self.AssertEqualBets()

  del self.index_in_pos

  players_left = len(self.all_in_pos) + len(self.active_pos)
  assert players_left
  
  if players_left >= 2:
   self.MatchShowDownLine()
   self.ln += 1
  while self.MatchShowDownContent():
   self.ln += 1

  self.MatchSummaryLine()
  self.ln += 1
  self.MatchTotalPotLine()

  #JUSTATEMP START
  while self.ln < len(self.lines):
   m = TotalPotLine.match(self.lines[self.ln])
   if m is not None:
    amount = self.MoneyToInt(m.group(1))
    tbets = sum([self.bet[x] for x in self.players])
    if amount != tbets + self.donations:
     print("DISCREPANCY", amount, tbets)
     assert False
    break
   self.ln += 1
  #JUSTATEMP END

  
 def MatchMoveLine(self):
  self.SkipWaste()

  m = FoldsLine.match(self.lines[self.ln]) 
  if m is not None:
   index = self.players.index(m.group(1))
   assert self.players[self.active_pos[self.index_in_pos]] == m.group(1)
   self.AddMove(self.active_pos[self.index_in_pos], 'fo')
   self.active_pos.pop(self.index_in_pos)
   if self.active_pos:
    self.index_in_pos %= len(self.active_pos)
   if len(self.all_in_pos) + len(self.active_pos) < 2:
    self.in_progress = False
   return True

  m = ChecksLine.match(self.lines[self.ln])
  if m is not None:
   assert self.players[self.active_pos[self.index_in_pos]] == m.group(1)
   self.AddMove(self.active_pos[self.index_in_pos], 'ch')
   self.index_in_pos += 1
   self.index_in_pos %= len(self.active_pos)
   return True

  m = BetsLine.match(self.lines[self.ln])
  if m is not None:
   assert self.players[self.active_pos[self.index_in_pos]] == m.group(1)
   amount = self.MoneyToInt(m.group(2))
   self.AddMove(self.active_pos[self.index_in_pos], 'be', amount)
   player = m.group(1)
   self.bet[player] += amount
   assert self.bet[player] > self.current_bet
   self.current_bet = self.bet[player]
   assert self.in_chips[player] >= amount
   self.in_chips[player] -= amount
   # m.group(3) is all-in
   assert bool(self.in_chips[player]) == (m.group(3) is None)
   if self.in_chips[player]:
    # Not all-in
    self.index_in_pos += 1
   else:
    self.all_in_pos.append(self.active_pos[self.index_in_pos])
    self.active_pos.pop(self.index_in_pos)
   if self.active_pos:
    self.index_in_pos %= len(self.active_pos)
   return True

  m = CallsLine.match(self.lines[self.ln])
  if m is not None:
   assert self.players[self.active_pos[self.index_in_pos]] == m.group(1)
   amount = self.MoneyToInt(m.group(2))
   self.AddMove(self.active_pos[self.index_in_pos], 'ca', amount)
   player = m.group(1)
   self.bet[player] += amount
   assert self.in_chips[player] >= amount
   self.in_chips[player] -= amount
   assert (self.bet[player] == self.current_bet) or \
    ((self.bet[player] <= self.current_bet) and (self.in_chips[player] == 0.))
   # m.group(3) is all-in
   assert bool(self.in_chips[player]) == (m.group(3) is None)
   if self.in_chips[player]:
    # Not all-in
    self.index_in_pos += 1
   else:
    self.all_in_pos.append(self.active_pos[self.index_in_pos])
    self.active_pos.pop(self.index_in_pos)
   if self.active_pos:
    self.index_in_pos %= len(self.active_pos)
   return True

  m = RaisesLine.match(self.lines[self.ln])
  if m is not None:
   assert self.players[self.active_pos[self.index_in_pos]] == m.group(1)
   by_amount = self.MoneyToInt(m.group(2))
   #to_amount = self.MoneyToInt(m.group(3))
   player = m.group(1)
   bet = self.current_bet + by_amount
   amount = bet - self.bet[player]
   self.AddMove(self.active_pos[self.index_in_pos], 'ra', amount)
   self.current_bet = self.bet[player] = bet
   assert self.in_chips[player] >= amount
   self.in_chips[player] -= amount
   # m.group(4) is all-in
   assert bool(self.in_chips[player]) == (m.group(4) is None)
   if self.in_chips[player]:
    # Not all-in
    self.index_in_pos += 1
   else:
    self.all_in_pos.append(self.active_pos[self.index_in_pos])
    self.active_pos.pop(self.index_in_pos)
   if self.active_pos:
    self.index_in_pos %= len(self.active_pos)
   return True

  m = UncalledBetLine.match(self.lines[self.ln])
  if m is not None:
   amount = self.MoneyToInt(m.group(1))
   player = m.group(2)
   self.AddMove(self.players.index(player), 'un', amount)
   assert self.bet[player] >= amount
   assert self.bet[player] == self.current_bet
   self.bet[player] -= amount
   self.current_bet -= amount
   if (self.in_chips[player] == 0.) and amount:
    # Move it back from all_in_pos to active_pos
    index = self.players.index(player)
    self.all_in_pos.remove(index)
    assert not self.active_pos
    self.active_pos = [index]
   self.in_chips[player] += amount
   for p in self.players:
    assert self.bet[p] <= self.current_bet
   return True

  return False


 def AssertEqualBets(self):
  if len(self.active_pos) < 2:
   return
  active_players = [self.players[x] for x in self.active_pos]
  active_bets = [self.bet[x] for x in active_players]
  max_bet = max(active_bets)
  min_bet = min(active_bets)
  assert max_bet == min_bet == self.current_bet
   

 def MatchFirstLine(self):
  m = FirstLine.match(self.lines[self.ln])
  assert m is not None
  self.hand_number = int(m.group(1))
  tup = SBBBDict[m.group(2)]
  self.currency = tup[0]
  self.sb_fee = self.MoneyToInt(tup[1])
  self.bb_fee = self.MoneyToInt(tup[2])

  if m.group(5) is not None:
   dtstamp = m.group(6)
   tzone = m.group(7)
  else:
   dtstamp = m.group(3)
   tzone = m.group(4)
  self.GenerateUtcTimestamp(dtstamp, TimeZoneDict[tzone])


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
  self.parsed_players_info[seat] = (m.group(2), self.MoneyToInt(m.group(3)))
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
  self.bet = collections.defaultdict(int)
  self.donations = 0 
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
  self.active_pos = list(range(player_count))
  self.all_in_pos = []
   
  del self.parsed_players_info


 def MatchBlindsLine(self):
  self.SkipWaste()
  m = SmallBlindLine.match(self.lines[self.ln])
  if m is not None:
   player = m.group(1)
   amount = self.MoneyToInt(m.group(2))
   assert player in self.players
   assert amount == self.sb_fee
   assert self.in_chips[player] >= amount
   self.in_chips[player] -= amount
   assert not self.bet[player]
   if player == self.players[0]:
    self.sb_found = True
    self.bet[player] = amount
   else:
    self.donations += amount
    self.contribs.append(f"{self.players.index(player)}s")
   return True
   
  m = BigBlindLine.match(self.lines[self.ln])
  if m is not None:
   player = m.group(1)
   amount = self.MoneyToInt(m.group(2))
   assert player in self.players
   assert amount == self.bb_fee
   assert not self.bet[player]
   self.bet[player] = amount
   assert self.in_chips[player] >= amount
   self.in_chips[player] -= amount
   if player == self.players[1]:
    self.bb_found = True
   else:
    self.contribs.append(f"{self.players.index(player)}b")
   return True

  m = BothBlindsLine.match(self.lines[self.ln])
  if m is not None:
   player = m.group(1)
   amount = self.MoneyToInt(m.group(2))
   assert player in self.players
   # He is neither SB nor BB
   assert self.players.index(player) >= 2
   assert amount == self.sb_fee + self.bb_fee
   assert not self.bet[player]
   self.bet[player] = self.bb_fee
   self.donations += self.sb_fee
   assert self.in_chips[player] >= amount
   self.in_chips[player] -= amount
   self.contribs.append(f"{self.players.index(player)}sb")
   return True

  m = AnteLine.match(self.lines[self.ln])
  if m is not None:
   amount = self.MoneyToInt(m.group(2))
   if self.ante == 0:
    self.ante = amount
    self.ante_players = set()
   else:
    assert amount == self.ante
   player = m.group(1)
   assert player in self.players
   self.ante_players.add(player)
   self.donations += self.ante
   assert self.in_chips[player] >= self.ante
   self.in_chips[player] -= self.ante
   return True

  return False


 def MatchHoleCardsLine(self):
  self.SkipWaste()
  m = HoleCardsLine.match(self.lines[self.ln])
  assert m is not None
  self.state = GameState.Preflop
  self.in_progress = True


 def MatchFlopLine(self):
  m = FlopLine.match(self.lines[self.ln])
  if m is None:
   m = FirstFlopLine.match(self.lines[self.ln])
   assert m is not None
   raise  KnownException("Multiple flops")
  self.communal = [m.group(1), m.group(2), m.group(3)]
  self.state = GameState.Flop


 def MatchTurnLine(self):
  m = TurnLine.match(self.lines[self.ln])
  if m is None:
   m = FirstTurnLine.match(self.lines[self.ln])
   assert m is not None
   raise KnownException("Multiple turns")
  assert (m.group(1) == self.communal[0]) and (m.group(2) == self.communal[1]) \
   and (m.group(3) == self.communal[2])
  self.communal += [m.group(4)]
  self.state = GameState.Turn


 def MatchRiverLine(self):
  m = RiverLine.match(self.lines[self.ln])
  if m is None:
   m = FirstRiverLine.match(self.lines[self.ln])
   assert m is not None
   raise KnownException("Multiple rivers")
  assert (m.group(1) == self.communal[0]) and (m.group(2) == self.communal[1]) \
   and (m.group(3) == self.communal[2]) and (m.group(4) == self.communal[3])
  self.communal += [m.group(5)]
  self.state = GameState.River


 def MatchShowDownLine(self):
  m = ShowDownLine.match(self.lines[self.ln])
  assert m is not None
  

 def MatchShowDownContent(self):
  players_left = len(self.all_in_pos) + len(self.active_pos)
  assert players_left

  m = ShowsHandLine.match(self.lines[self.ln])
  if m is not None:
   assert players_left >= 2
   player = m.group(1)
   player_index = self.players.index(player)
   assert (player_index in self.all_in_pos) or (player_index in self.active_pos)
   combination = m.group(4)  
   PRODOLZHIT'

 def GenerateUtcTimestamp(self, tstr, tzstr):
  tz = pytz.timezone(tzstr)
  dt = datetime.strptime(tstr, "%Y/%m/%d %H:%M:%S").replace(tzinfo=tz)
  self.timestamp = dt.astimezone(pytz.utc)


 def AddMove(self, player_index, move, amount=None):
  if amount is None:
   self.moves[self.state.value].append(f"{player_index}{move}")
  else:
   amount_str = self.IntToMoney(amount)
   self.moves[self.state.value].append(f"{player_index}{amount_str}")


 def MoneyToInt(self, amount_str: str):
  multiplier, _ = CurrencyParams[self.currency]
  return round(float(amount_str) * multiplier)


 def IntToMoney(self, amount: int):
  multiplier, precision = CurrencyParams[self.currency]
  formatter = f"%0.{precision}f"
  return formatter % (float(amount) / multiplier)

