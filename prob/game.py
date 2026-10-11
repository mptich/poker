import sys
import random
import collections
from tqdm import tqdm
import dill

from values import Values
import disputils as du
import pokutils as pu
import PokerFastutils as pf

from numba import prange, njit
from numba.typed import Dict


PLAYERS = 7
CUTOFF = False

d = collections.defaultdict(float)
handd = collections.defaultdict(lambda: collections.defaultdict(float))
totald = collections.defaultdict(int)

#@njit(parallel=True)
def RunMainLoop(count):
 for _ in tqdm(range(count)):

  s = random.sample(Values, PLAYERS*2 + 5)
  flopCommunalStr, suitDict = pu.FlopCommunalToMeaningPreproc(s[-5:-2])

  best_rank = -1
  for pl in range(PLAYERS):
   card1=s[pl*2]
   card2=s[pl*2+1]
  
   #mym = pu.TwoCardsTo2Meaning(card1, card2)
   mym = pu.FlopToMeaning([card1, card2], flopCommunalStr, suitDict)
 
   totald[mym] += 1
   h7 = [card1, card2] + s[-5:]
   btr = pf.Process7CardsWithSuite(h7)
   if btr > best_rank:
    best_rank = btr
    winner_list = [mym]
   elif btr == best_rank:
    winner_list.append(mym)
  
  winReward = 1. / len(winner_list)
  for mym in winner_list:
   d[mym] += winReward
   handd[mym][pu.TotalRankToHandRank(best_rank)] += winReward
 
RunMainLoop(1000000)
with open("totald_" + sys.argv[1] + ".pkl", "wb") as fout:
    dill.dump(totald, fout)
with open("d_" + sys.argv[1] + ".pkl", "wb") as fout:
    dill.dump(d, fout)
with open("handd_" + sys.argv[1] + ".pkl", "wb") as fout:
    dill.dump(handd, fout)
sys.exit()
 
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
  print(f"{k}:{du.NiceFraction(v,4)} ", end='')
  hands_dict = handd[k]
  sorted_hands_dict = dict(sorted(hands_dict.items(),
   key=lambda item: item[1], reverse=True))
  for hk, hv in sorted_hands_dict.items():
   print(f"{pu.HandFromHandRank[hk]}:{du.NiceFraction(hv,4)} ", end='')
  print()

 print(f"{playable} out of {len(outd)} pairs are playable")


DisplayByProbWithHands(d, totald, handd, cutoff=CUTOFF)
