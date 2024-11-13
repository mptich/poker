import collections
import random

from ranks import HandRank, HandFromHandRank
from values import Values
import utils

def GetHandAndRank(h):
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
 

def Process7(h7):
 h7.sort(key = lambda x: x[0])
 best_rank = -1

 for i in range(7):
  for j in range(7):
   if i!=j:

    out = []
    for ind, card in enumerate(h7):
     if ind not in (i,j):
      out.append(card)
    val, rank = GetHandAndRank(out)
    hand_rank = HandRank[val]
    total_rank = utils.HandRankToTotalRank(hand_rank, rank)
    if total_rank > best_rank:
     best_rank = total_rank
     best_hand = out

 return best_hand, best_rank

def main():
 d=collections.defaultdict(int)
 for _ in range(100000):
  hand7 = random.sample(Values, 7)
  bh, br = Process7(hand7)
  hand_rank = utils.TotalRankToHandRank(br)
  hand = HandFromHandRank[hand_rank]
  d[hand] += 1
 
 d=dict(sorted(d.items(), key=lambda item: item[1]))
 print(d)

if __name__ == 'main':
 main()
 
