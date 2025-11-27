import os
#os.environ['NUMBA_DISABLE_JIT'] = '1'
import collections
import random
#from numba import njit, prange
import numpy as np

import disputils as du

HandRank = { \
 'strfl':8, 
 '4':7,
 'fh':6,
 'fl':5,
 'str':4,
 '3':3,
 '22':2,
 '2':1,
 'hc':0
}

HandFromHandRank = {v:k for k,v in HandRank.items()}

# Significant positions in the rank
HandToRankLen = { \
 'strfl': 1,
 '4': 2,
 'fh': 2,
 'fl': 5,
 'str': 1,
 '3': 3,
 '22': 3,
 '2': 4,
 'hc': 5
}

HandMulti = 13*13*13*13*13

def HandAndRankToTotalRank(hand, rank):
 return HandRank[hand]*HandMulti + rank

def TotalRankToHandRank(tr):
 return tr//HandMulti

def TotalRankToHandAndRank(tr):
 return HandFromHandRank[tr//HandMulti], tr % HandMulti

def RankDesc(h, r):
    c =[]
    for _ in range(HandToRankLen[h]):
        c.append(du.CardValToDisplayStr[r % 13])
        r //= 13
    assert r == 0
    return ' '.join(c)

def TotalRankToHandAndRankDesc(tr):
    h, r = TotalRankToHandAndRank(tr)
    return h + ' ' + RankDesc(h, r)


# Translates to cards into a value from TwoCards
def TwoCardsToMeaning(c1,c2):
 if c1[1] == c2[1]:
  c = 's'
 else:
  c = 'o'
 return (min(c1[0], c2[0]), max(c1[0], c2[0]), c)

def GetHandAndRankFrom5(h):
 # h must be sorted by card values, with suit replaced with True (significant suite that could,
 # potentially, form a flush) and False (insignificant suite that cannot form a flush)
 flash = (sum([x[1] for x in h]) == 5)
 vals = [x[0] for x in h]
 vals_count = collections.Counter(vals)

 if len(vals_count) == 5:
  # Straight or flash candidate
  straight = False
  if (vals[4]-vals[0] == 4):
   straight = True
   rank = vals[4]
  elif ((vals[4]==12) and (vals[0]==0) and (vals[3]==3)):
   straight = True
   rank = vals[3]
  if straight:
   ret = 'str' if not flash else 'strfl'
   return  'str' if not flash else 'strfl', rank
  else:
   # Flash or nothing, rank from all 5 cards in both cases
   rank = (((vals[4]*13+vals[3])*13+vals[2])*13+vals[1])*13+vals[0]
   return 'hc' if not flash else 'fl', rank

 elif len(vals_count) == 2:
  # Full house or 4 candidate
  for k,v in vals_count.items():
   if v == 4:
    rank = k
    ret = '4'
   elif v == 3:
    rank = k
    ret = 'fh'
  return ret, rank

 # Now we have 3, 22, or 2 
 keys_by_val = sorted(vals_count.keys(), key=lambda x: vals_count[x])

 if len(vals_count) == 3:
  # 3 or 22
  if vals_count[keys_by_val[2]] == 3:
   rank = keys_by_val[2]
   return '3', rank
  # 22
  maxPair = max(keys_by_val[1], keys_by_val[2])
  minPair = min(keys_by_val[1], keys_by_val[2])
  rank = (maxPair * 13 + minPair) * 13 + keys_by_val[0]
  return '22', rank

 # Only 2, len(vals_count) == 4
 restOfCards = sorted(keys_by_val[:3])
 rank = ((keys_by_val[3]*13+restOfCards[2])*13+restOfCards[1])*13+restOfCards[0]
 return '2', rank
 
def Process7CardsWithSuite(h7):
 h7.sort(key = lambda x: x[0])
 best_rank = -1

 for i in range(7):
  for j in range(i+1,7):

   out = []
   for ind, c in enumerate(h7):
    if ind not in (i,j):
     out.append(c)
   hand, rank = GetHandAndRankFrom5(out)
   total_rank = HandAndRankToTotalRank(hand, rank)
   if total_rank > best_rank:
    best_rank = total_rank
    best_hand = out

 return best_hand, best_rank

