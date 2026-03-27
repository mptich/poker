import random
import collections
from tqdm import tqdm

from values import Values
import disputils as du
import pokutils as pu
import PokerFastutils as pf

PLAYERS = 7
CUTOFF = False

d = collections.defaultdict(float)
handd = collections.defaultdict(lambda: collections.defaultdict(float))
totald = collections.defaultdict(int)

for _ in tqdm(range(3000000)):

 #JUSTATEMP
 gaga=0
 s = random.sample(Values, PLAYERS*2 + 5)
 best_rank = -1
 for pl in range(PLAYERS):
  card1=s[pl*2]
  card2=s[pl*2+1]
  
  mym = pu.TwoCardsTo2Meaning(card1, card2)
  #suim = pu.TwoThreeToSuiteMeaning((card1, card2), s[-3:])
  #valm = pu.TwoThreeToValueMeaning((card1, card2), s[-3:])
  #JUSTATEMP
  #mym=suim
  #JUSTATEMP START
  if mym == "s3A":
      gaga=1
  #JUSTATEMP END

  totald[mym] += 1
  h7 = [card1, card2] + s[-5:]
  btr = pf.Process7CardsWithSuite(h7)
  if btr > best_rank:
   best_rank = btr
   winner_list = [mym]
  elif btr == best_rank:
   winner_list.append(mym)
 
 #JUSTATEMP START
 if gaga:
     if "s3A" not in winner_list:
         print(pu.TotalRankToHandAndRank(best_rank))
         for cc in s:
             print(du.DisplayCardStr(cc), " ", end='')
         print()
 #JUSTATEMP END
 winReward = 1. / len(winner_list)
 for mym in winner_list:
  d[mym] += winReward
  handd[mym][pu.TotalRankToHandRank(best_rank)] += winReward


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
