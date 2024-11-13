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

CardValToDisplayStr = {0:'2', 1:'3', 2:'4', 3:'5', 4:'6', 5:'7', 6:'8',
 7:'9', 8:'T', 9:'J', 10:'Q', 11:'K', 12:'A'} 

CardSuiteToDisplayStr = {0:'s', 1:'c', 2:'h', 3:'d'}


