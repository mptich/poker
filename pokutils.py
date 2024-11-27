import collections
import random

HandRank = { \
 'strfl':8, 
 '4':7,
 'fh':6,
 'fl':5,
 'str':4,
 '3':3,
 '22':2,
 '2':1,
 '':0
}
HandFromHandRank = {v:k for k,v in HandRank.items()}

CardValToDisplayStr = {0:'2', 1:'3', 2:'4', 3:'5', 4:'6', 5:'7', 6:'8',
 7:'9', 8:'T', 9:'J', 10:'Q', 11:'K', 12:'A'}
DisplayStrToCardVal = {v:k for k,v in CardValToDisplayStr.items()}

CardSuiteToDisplayStr = {0:'s', 1:'c', 2:'h', 3:'d'}
DisplayStrToCardSuite = {v:k for k,v in CardSuiteToDisplayStr.items()}

def CardDispToRepresentation(card_str):
 return (DisplayStrToCardVal[card_str[0]], DisplayStrToCardSuite[card_str[1]])


def HandAndRankToTotalRank(hand, rank):
 return HandRank[hand]*13*13*13*13*13 + rank

def TotalRankToHandRank(tr):
 return tr//(13*13*13*13*13)

# Translates to cards into a value from TwoCards
def TwoCardsXlate(c1,c2):
 if c1[0] == c2[0]:
  return (c1[0], c1[0])
 return(min(c1[0],c2[0]), max(c1[0],c2[0]), 'o' if c1[1]!=c2[1] else 's') 

def TwoCardsToDisplayStr(tc):
 s1 = CardValToDisplayStr[tc[0]]
 s2 = CardValToDisplayStr[tc[1]]
 if len(tc) == 3:
  return s1+s2+tc[2]
 return s1+s2

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
 
 
def GetHandAndRankFrom7(h):
 # h must be sorted by card value

 flash = (len(set([x[1] for x in h])) == 1)
 vals = [x[0] for x in h]
 vals_count = collections.Counter(vals)

 if len(vals_count) == 5:
  if (vals[4]-vals[0] == 4) or \
   ((vals[4]==12) and (vals[0]==0) and (vals[3]==3)):
   rank = vals[3]
   ret = 'str' if not flash else 'strfl'
   return  'str' if not flash else 'strfl', rank
  else:
   rank = (((vals[4]*13+vals[3])*13+vals[2])*13+vals[1])*13+vals[0]
   return '' if not flash else 'fl', rank

 elif len(vals_count) == 2:
  rank = 0
  for k,v in vals_count.items():
   if v == 1:
    rank += k
    ret = '4'
   elif v == 2:
    rank += k
    ret = 'fh'
   else:
    rank += k*13
  return ret, rank

 if flash:
  return 'fl', vals[4]

 keys_by_val = sorted(vals_count.keys(), key=lambda x: vals_count[x]*13+x)

 if len(vals_count) == 3:
  rank = (keys_by_val[2]*13+keys_by_val[1])*13+keys_by_val[0]
  if vals_count[keys_by_val[2]] == 3:
   return '3', rank
  else:
   return '22', rank

 rank = ((keys_by_val[3]*13+keys_by_val[2])*13+keys_by_val[1])*13+keys_by_val[0]
 return '2', rank
 

def Process7Cards(h7):
 h7.sort(key = lambda x: x[0])
 best_rank = -1

 for i in range(7):
  for j in range(7):
   if i!=j:

    out = []
    for ind, card in enumerate(h7):
     if ind not in (i,j):
      out.append(card)
    hand, rank = GetHandAndRankFrom5(out)
    total_rank = HandAndRankToTotalRank(hand, rank)
    if total_rank > best_rank:
     best_rank = total_rank
     best_hand = out

 return best_hand, best_rank

