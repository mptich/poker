import pokutils as pyutils
import disputils as du
import PokerFastutils as pfu

h = [(3,1), (4,1), (7,1), (3,2), (6,1), (5,0), (5,1)]
tr = pfu.Process7CardsWithSuite(h)
print(pyutils.TotalRankToHandAndRankDesc(tr))

h = [(3,1), (4,3), (7,1), (3,2), (6,1), (5,0), (5,1)]
tr = pfu.Process7CardsWithSuite(h)
print(pyutils.TotalRankToHandAndRankDesc(tr))

h = [(12,1), (10,1), (0,0), (1,2), (2,1), (12,0), (3,1)]
tr = pfu.Process7CardsWithSuite(h)
print(pyutils.TotalRankToHandAndRankDesc(tr))

h = [(3,1), (10,1), (7,1), (7,2), (10,1), (5,0), (7,1)]
tr = pfu.Process7CardsWithSuite(h)
print(pyutils.TotalRankToHandAndRankDesc(tr))

h = [(9,1), (10,1), (7,1), (7,2), (10,1), (9,0), (7,1)]
tr = pfu.Process7CardsWithSuite(h)
print(pyutils.TotalRankToHandAndRankDesc(tr))

h = [(3,1), (10,1), (7,3), (7,2), (10,1), (7,0), (7,1)]
tr = pfu.Process7CardsWithSuite(h)
print(pyutils.TotalRankToHandAndRankDesc(tr))

h = [(12,1), (10,1), (7,3), (7,2), (10,1), (7,0), (7,1)]
tr = pfu.Process7CardsWithSuite(h)
print(pyutils.TotalRankToHandAndRankDesc(tr))

h = [(12,1), (10,1), (12,3), (7,2), (12,2), (7,0), (7,1)]
tr = pfu.Process7CardsWithSuite(h)
print(pyutils.TotalRankToHandAndRankDesc(tr))

h = [(12,1), (10,1), (12,3), (7,2), (10,2), (7,0), (7,1)]
tr = pfu.Process7CardsWithSuite(h)
print(pyutils.TotalRankToHandAndRankDesc(tr))

h = [(12,1), (10,1), (12,3), (7,2), (10,2), (1,0), (7,1)]
tr = pfu.Process7CardsWithSuite(h)
print(pyutils.TotalRankToHandAndRankDesc(tr))

h = [(12,1), (10,1), (12,3), (7,2), (10,2), (8,0), (7,1)]
tr = pfu.Process7CardsWithSuite(h)
print(pyutils.TotalRankToHandAndRankDesc(tr))

h = [(12,1), (10,1), (9,3), (7,2), (10,2), (8,0), (7,1)]
tr = pfu.Process7CardsWithSuite(h)
print(pyutils.TotalRankToHandAndRankDesc(tr))

h = [(12,1), (10,1), (9,3), (7,2), (11,2), (8,0), (7,1)]
tr = pfu.Process7CardsWithSuite(h)
print(pyutils.TotalRankToHandAndRankDesc(tr))

h = [(2,1), (10,1), (9,3), (7,2), (11,2), (8,0), (7,1)]
tr = pfu.Process7CardsWithSuite(h)
print(pyutils.TotalRankToHandAndRankDesc(tr))

h = [(2,1), (10,1), (9,3), (6,2), (2,2), (8,0), (7,1)]
tr = pfu.Process7CardsWithSuite(h)
print(pyutils.TotalRankToHandAndRankDesc(tr))

h = [(2,1), (10,1), (9,3), (5,2), (2,2), (8,0), (7,1)]
tr = pfu.Process7CardsWithSuite(h)
print(pyutils.TotalRankToHandAndRankDesc(tr))

h = [(2,3), (10,1), (9,3), (2,0), (2,3), (8,0), (7,3)]
tr = pfu.Process7CardsWithSuite(h)
print(pyutils.TotalRankToHandAndRankDesc(tr))

h = [(2,3), (10,3), (9,3), (2,0), (2,0), (8,3), (7,3)]
tr = pfu.Process7CardsWithSuite(h)
print(pyutils.TotalRankToHandAndRankDesc(tr))

h = [(4, 3), (11, 2), (0, 2), (1, 2), (4, 2), (2, 2), (12, 2)]
tr = pfu.Process7CardsWithSuite(h)
print(pyutils.TotalRankToHandAndRankDesc(tr))









