import pygo

AI1 = pygo.AISimple('Bob',pruning=4,depth=3)
AI2 = pygo.AISimple('Jeff',pruning=3,depth=6)

go = pygo.Go(5,player1=AI1,player2=AI2)