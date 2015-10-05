from core._board import Board, InvalidMoveException
from core._features import extract_features
from core._player import Human, ExitException
from core._ai import AISimple, AIMinimax

class PassException(Exception):
	pass
class GameOverException(Exception):
	pass

class Go(object):
	def __init__(self,size=19,player1=Human('Bob'),player2=AIMinimax('Bill'),board=None,display_on=True,auto_start=True):
		self.players = [player1,player2]
		self.display_on = display_on
		self.b = Board(size) if not board else board
		self.color_lookup = {0:'b',1:'w'}
		self.pid_lookup = {'b':0,'w':1}
		if auto_start: self.start()
	def display(self,text):
		if self.display_on: print text
	def _play(self,pid):
		player = self.players[pid]
		decision = player.decide(self.b,'w')
		if not decision:
			self.display('%s pass'%player.name)
			raise PassException()
		self.display('%s plays %s,%s'%(player.name,decision[0],decision[1]))
		return decision
	def start(self):
		self.display('GO')
		curr_player = 0
		try:
			while(True):
				self.display(self.b)
				not_moved = True
				self.display('\nPlayer %s?'%str(curr_player+1))
				while(True):
					try:
						i,j = self._play(curr_player)
					except ValueError:
						self.display('Invalid entry. Use the format: x,y')
						continue
					except PassException:
						self.b._pass()
						break
					try:
						self.b[i,j] = self.color_lookup[curr_player]
						break
					except (AssertionError, InvalidMoveException):
						self.display('Invalid move')
						continue
				self.display('\n')
				if self.b._is_over:
					raise GameOverException()
				curr_player=(curr_player+1)%2
		except ExitException:
			self.display('Game exited by user')
		except GameOverException:
			result = self.b.assess(full_result=True)
			self.display('Game is Over')
			if result[0] == '': self.display('Draw')
			else: self.display('Winner: ' + self.players[self.pid_lookup[result[0]]].name)
			self.display('Score: ' + str(result[1]))
			return result

# The following is for debug
study_case = Board(5)
study_case.b = ['','w','b','b','b','w','','b','','b','','b','b','b','b','w','b','w','b','w','','w','','w','']