from tqdm import tqdm
import collections
import random
from numba import prange

from values import Values
import pokutils as pyutils
import PokerFastutils as pu

d = collections.Counter()

COUNT = 1000000

for _ in tqdm(prange(COUNT)):

 s = random.sample(Values, 7)
 tr = pu.Process7CardsWithSuite(s)
 h, r = pyutils.TotalRankToHandAndRank(tr)
 # Just for its assert
 pyutils.RankDesc(h, r)
 d[h] += 1

for k,v in d.items():
    print(k, v/COUNT)

