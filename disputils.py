CardValToDisplayStr = {0:'2', 1:'3', 2:'4', 3:'5', 4:'6', 5:'7', 6:'8',
 7:'9', 8:'T', 9:'J', 10:'Q', 11:'K', 12:'A'}
DisplayStrToCardVal = {v:k for k,v in CardValToDisplayStr.items()}

CardSuiteToDisplayStr = {0:'s', 1:'c', 2:'h', 3:'d'}
DisplayStrToCardSuite = {v:k for k,v in CardSuiteToDisplayStr.items()}

def CardDispToRepresentation(card_str):
 return (DisplayStrToCardVal[card_str[0]], DisplayStrToCardSuite[card_str[1]])

def DisplayCardStr(card):
 return CardValToDisplayStr[card[0]] + CardSuiteToDisplayStr[card[1]]

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

