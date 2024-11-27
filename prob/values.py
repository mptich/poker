Values = []

for i in range(13):
 for j in range(4):
  Values.append((i,j))

TwoCards = []
for i in range(13):
 for j in range(i):
  TwoCards.append((j,i,'o'))
  TwoCards.append((j,i,'s'))
 TwoCards.append((i,i))

