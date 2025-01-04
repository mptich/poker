import random
import collections
from tqdm import tqdm

from values import Values
import pokutils as pu

PLAYERS = 8
CUTOFF = False

d = collections.defaultdict(int)
handd = collections.defaultdict(collections.Counter)
totald = collections.defaultdict(int)

for _ in tqdm(range(200000)):

 s = random.sample(Values, PLAYERS*2 + 5)
 best_rank = -1
 for pl in range(PLAYERS):
  c1=s[pl*2]
  c2=s[pl*2+1]
  tc = pu.TwoCardsXlate(c1, c2)
  totald[tc] += 1
  h7 = [c1, c2]+s[-5:]
  bh, br = pu.Process7Cards(h7)
  if br > best_rank:
   best_rank = br
   win_cards = [c1,c2] 

 tc = pu.TwoCardsXlate(win_cards[0], win_cards[1])
 d[tc] += 1
 handd[tc][pu.TotalRankToHandRank(best_rank)] += 1

def DisplayByCard(d, totald):
 for i in reversed(range(13)):
  tc = (i,i)
  print(f"{pu.TwoCardsToDisplayStr(tc)}:", end='')
  if d[tc]:
   print(f"{pu.NiceFraction(d[tc]/totald[tc],4)} ", end='')
  else:
   print(f"0 ", end='')
 print()
 
 for s in ('s', 'o'):
  for i in reversed(range(13)):
   for j in reversed(range(i)):
    tc = (j,i,s)
    print(f"{pu.TwoCardsToDisplayStr(tc)}:", end='')
    if d[tc]:
     print(f"{pu.NiceFraction(d[tc]/totald[tc],4)} ", end='') 
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
  print(f"{pu.TwoCardsToDisplayStr(k)}:{pu.NiceFraction(v,4)} ", end='')

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
 barrier_displayed = False
 for k,v in sorted_dict.items():
  if v >= 1/PLAYERS:
   playable += 1
  elif cutoff:
   continue
  elif not barrier_displayed:
   barrier_displayed = True
   print("-------------------------------------------------------------")
  print(f"{pu.TwoCardsToDisplayStr(k)}:{pu.NiceFraction(v,4)} ", end='')
  hands_dict = handd[k]
  sorted_hands_dict = dict(sorted(hands_dict.items(),
   key=lambda item: item[1], reverse=True))
  for hk, hv in sorted_hands_dict.items():
   print(f"{pu.HandFromHandRank[hk]}:{pu.NiceFraction(hv,4)} ", end='')
  print()

 print(f"{playable} out of {len(outd)} pairs are playable")


DisplayByProbWithHands(d, totald, handd, cutoff=CUTOFF)
