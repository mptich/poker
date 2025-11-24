import random
import collections
from tqdm import tqdm

from values import Values
import disputils as du
import pokutils as pu

PLAYERS = 6
CUTOFF = False

d = collections.defaultdict(int)
handd = collections.defaultdict(collections.Counter)
totald = collections.defaultdict(int)

for _ in tqdm(range(100000)):

 s = random.sample(Values, PLAYERS*2 + 5)
 suiteCounts = collections.Counter([x[1] for x in s[-5:]])
 signifSuite = None
 for k in suiteCounts.keys():
     if suiteCounts[k] >= 3:
         signifSuite = k;
         break

 # Assing cards with signif / non-signif suite
 sout = []
 for card in s:
     if card[1] != signifSuite:
         sout.append((card[0], False))
     else:
         sout.append((card[0], True)

 best_rank = -1
 for pl in range(PLAYERS):
  card1=s[pl*2]
  card2=s[pl*2+1]
  tc = pu.TwoCardsToMeaning(card1, card2)
  totald[tc] += 1
  h7 = [sout[pl*2], sout[pl*2+1]] + sout[-5:]
  bh, br = pu.Process7Cards(h7)
  if br > best_rank:
   best_rank = br
   winner_list = [tc]
  elif br == best_rank:
   winner_list.append(tc)
 
 winReward = 1. / len(winner_list)
 for tc in winner_list:
  d[tc] += winReward
  handd[tc][pu.TotalRankToHandRank(best_rank)] += winReward

def DisplayByCard(d, totald):
 for i in reversed(range(13)):
  tc = (i,i,'o')
  print(f"{du.TwoCardsMeaningToDisplayStr(tc)}:", end='')
  if d[tc]:
   print(f"{du.NiceFraction(d[tc]/totald[tc],4)} ", end='')
  else:
   print(f"0 ", end='')
 print()
 
 for s in ('s', 'o'):
  for i in reversed(range(13)):
   for j in reversed(range(i)):
    tc = (j,i,s)
    print(f"{du.TwoCardsMeaningToDisplayStr(tc)}:", end='')
    if d[tc]:
     print(f"{du.NiceFraction(d[tc]/totald[tc],4)} ", end='') 
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
  print(f"{du.TwoCardsMeaningToDisplayStr(k)}:{du.NiceFraction(v,4)} ", end='')

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
  print(f"{du.TwoCardsMeaningToDisplayStr(k)}:{du.NiceFraction(v,4)} ", end='')
  hands_dict = handd[k]
  sorted_hands_dict = dict(sorted(hands_dict.items(),
   key=lambda item: item[1], reverse=True))
  for hk, hv in sorted_hands_dict.items():
   print(f"{pu.HandFromHandRank[hk]}:{du.NiceFraction(hv,4)} ", end='')
  print()

 print(f"{playable} out of {len(outd)} pairs are playable")


DisplayByProbWithHands(d, totald, handd, cutoff=CUTOFF)
