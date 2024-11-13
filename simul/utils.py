import values

def HandRankToTotalRank(hr, r):
 return hr*13*13*13*13*13 + r

def TotalRankToHandRank(tr):
 return tr//(13*13*13*13*13)

# Translates to cards into a value from TwoCards
def TwoCardsXlate(c1,c2):
 if c1[0] == c2[0]:
  return (c1[0], c1[0])
 return(min(c1[0],c2[0]), max(c1[0],c2[0]), 'o' if c1[1]!=c2[1] else 's') 

def TwoCardsToDisplayStr(tc):
 s1 = values.CardValToDisplayStr[tc[0]]
 s2 = values.CardValToDisplayStr[tc[1]]
 if len(tc) == 3:
  return s1+s2+tc[2]
 return s1+s2

def DisplayCardStr(card):
 return values.CardValToDisplayStr[card[0]] + \
  values.CardSuiteToDisplayStr[card[1]]
 

# Displays all handed out cards
def DisplayCardLayout(handed_cards):
 players = (len(handed_cards) - 5) // 2
 for i in range(players):
  c1 = handed_cards[2*i]
  c2 = handed_cards[2*i+1]
  if c2[0] < c1[0]:
   c1,c2 = (c2,c1)
  s1 = DisplayCardStr(c1)
  s2 = DisplayCardStr(c2)
  print(f"{i}:{s1}{s2}  ", end='')
 print()
 river = handed_cards[-5:].copy()
 river.sort(key = lambda x: x[0])
 for card in river:
  print(f"{DisplayCardStr(card)} ", end='')
 print()

def NiceFraction(f, precision):
 assert f >= 0.
 np = 10**precision
 out = int(f * np)
 if out == np:
  out = np-1
 return out
 
 
