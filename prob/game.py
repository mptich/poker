import random
import collections

from values import Values
import prob
import utils
import ranks

PLAYERS = 6

d = collections.defaultdict(int)
handd = collections.defaultdict(collections.Counter)
totald = collections.defaultdict(int)

for _ in range(300000):

 s = random.sample(Values, PLAYERS*2 + 5)
 best_rank = -1
 for pl in range(PLAYERS):
  c1=s[pl*2]
  c2=s[pl*2+1]
  tc = utils.TwoCardsXlate(c1, c2)
  totald[tc] += 1
  h7 = [c1, c2]+s[-5:]
  bh, br = prob.Process7(h7)
  if br > best_rank:
   best_rank = br
   win_cards = [c1,c2] 

 tc = utils.TwoCardsXlate(win_cards[0], win_cards[1])
 d[tc] += 1
 handd[tc][utils.TotalRankToHandRank(best_rank)] += 1

def DisplayByCard(d, totald):
 for i in reversed(range(13)):
  tc = (i,i)
  print(f"{utils.TwoCardsToDisplayStr(tc)}:", end='')
  if d[tc]:
   print(f"{utils.NiceFraction(d[tc]/totald[tc],4)} ", end='')
  else:
   print(f"0 ", end='')
 print()
 
 for s in ('s', 'o'):
  for i in reversed(range(13)):
   for j in reversed(range(i)):
    tc = (j,i,s)
    print(f"{utils.TwoCardsToDisplayStr(tc)}:", end='')
    if d[tc]:
     print(f"{utils.NiceFraction(d[tc]/totald[tc],4)} ", end='') 
    else:
     print(f"0 ", end='')
  print()

def DisplayByProb(d, totald):
 outd = {}
 for k,v in totald.items():
  outd[k] = d[k] / v

 sorted_dict = dict(sorted(outd.items(),
  key=lambda item: item[1], reverse=True))
 for k,v in sorted_dict.items():
  print(f"{utils.TwoCardsToDisplayStr(k)}:{utils.NiceFraction(v,4)} ", end='')

 print()
  

def DisplayByProbWithHands(d, totald, handd, cutoff=True):
 outd = {}
 for k,v in totald.items():
  outd[k] = d[k] / v
  for hk,hv in handd[k].items():
   handd[k][hk] = hv / v

 sorted_dict = dict(sorted(outd.items(),
  key=lambda item: item[1], reverse=True))

 playable = 0
 for k,v in sorted_dict.items():
  if cutoff and (v < 1/PLAYERS):
   continue
  playable += 1
  print(f"{utils.TwoCardsToDisplayStr(k)}:{utils.NiceFraction(v,4)} ", end='')
  hands_dict = handd[k]
  sorted_hands_dict = dict(sorted(hands_dict.items(),
   key=lambda item: item[1], reverse=True))
  for hk, hv in sorted_hands_dict.items():
   print(f"{ranks.HandFromHandRank[hk]}:{utils.NiceFraction(hv,4)} ", end='')
  print()

 if cutoff:
  print(f"{playable} out of {len(outd)} pairs are playable")


DisplayByProbWithHands(d, totald, handd)
