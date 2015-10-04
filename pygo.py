from core._board import Board, InvalidMoveException
from AI._features import extract_features

class PassException(Exception):
	pass
class ExitException(Exception):
	pass
class GameOverException(Exception):
	pass

import random

COL_TO_INT = {'b':0,'w':1}
INT_TO_COL = {0:'b',1:'w'}

debug_ai = False

def scal(x,y):
	return sum([a*b for a,b in zip(x,y)])

WEIGHTS = {
	'n_clusters':[-1.5,1.5],
	'n_loose_clusters':[-1.5,1.5],
	'n_stones':[1.,-1.],
	'n_liberties':[1.5,-1.5],
	'n_eyes':[6.,-6.],
	'low_liberty_clusters':[-3.,4.]
}

#TODO: add feature corresponding to number of clusters with only one liberty


def heuristic(board,col,extract_features=extract_features,weights = WEIGHTS,ret_features=False):
	col_int = COL_TO_INT[col]
	other_col = INT_TO_COL[(col_int+1)%2]
	
	features = extract_features(board)
	
	result = sum([f[col]*weights[k][0] for k,f in features.items()]) + sum([f[other_col]*weights[k][1] for k,f in features.items()])
	if ret_features:
		return (result,features)
	return result

class Player(object):
	def __init__(self,name):
		self.name=name

class Human(Player):
	def decide(self,board,color):
		coords = raw_input()
		if coords == 'pass': return None
		if coords == 'exit': raise ExitException()
		i,j = self._parse_coords(coords)
		i=int(i)
		j=int(j)
		return (i,j)
	def _parse_coords(self,coords):
		i,j = coords.split(',')
		return (i,j)

class AI(Player):
	def decide(self,board,color):
		available = [(i,j) for i in range(board.s) for j in range(board.s) if board[i,j]=='']
		return random.choice(available)
	def simulate_move(self,board,move,color):
		temp_board = Board(board.s)
		temp_board.b = board.b[:]
		temp_board.history = board.history[:]
		temp_board[move] = color
		return temp_board

class AISimple(AI):
	def __init__(self,name,pruning=4,depth=2):
		self.pruning = pruning
		self.depth = depth
		super(AISimple,self).__init__(name)
	def deep_search(self,heuristic,board,color,depth,color_move=None):
		if depth==0: return heuristic(board,color)
		col_int = COL_TO_INT[color]
		other_color = INT_TO_COL[(col_int+1)%2]
		if not color_move: color_move = other_color
		col_move_int = COL_TO_INT[color_move]
		other_color_move = INT_TO_COL[(col_move_int+1)%2]
		available = [(i,j) for i in range(board.s) for j in range(board.s) if board[i,j]=='']
		optimum_h = -1e30 if color == color_move else 1e30
		if self.pruning:
			hlist = []
			for c in available:
				try:
					temp_board = self.simulate_move(board,c,color_move)
				except InvalidMoveException:
					continue
				h = heuristic(temp_board,color)
				hlist.append((h,c))
			hlist.sort(reverse=True)
			available = [x[1] for x in hlist][:min(self.pruning,len(hlist))]
		for c in available:
			try:
				temp_board = self.simulate_move(board,c,color_move)
			except InvalidMoveException:
				continue
			h = self.deep_search(heuristic,temp_board,color,depth-1,color_move=other_color_move)
			if (h>optimum_h and color == color_move) or (h<optimum_h and color != color_move) :
				optimum_h = h
		return optimum_h
	def decide(self,board,color):
		available = [(i,j) for i in range(board.s) for j in range(board.s) if board[i,j]=='']
		best_move = None
		current_h = heuristic(board,color)
		max_h = -1e30
		for c in available:
			try:
				temp_board = self.simulate_move(board,c,color)
			except InvalidMoveException:
				continue
			depth = 2
			h = self.deep_search(heuristic,temp_board,color,depth)
			# h,features = heuristic(temp_board,color,ret_features=True)
			# if debug_ai:
			# 	print 'Evaluating move:'
			# 	print temp_board
			# 	print 'Heuristic:'
			# 	print h,features
			if h>max_h:
				max_h = h
				best_move = c
		print max_h
		if max_h < current_h:
			return
		return best_move


class Go(object):
	def __init__(self,size=19,player1=Human('Bob'),player2=AISimple('Bill'),board=None,display_on=True):
		self.players = [player1,player2]
		self.display_on = display_on
		self.b = Board(size) if not board else board
		self.color_lookup = {0:'b',1:'w'}
		self.pid_lookup = {'b':0,'w':1}
		self.start()
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
			print 'Game is Over'
			if result[0] == '': self.display('Draw')
			else: self.display('Winner: ' + self.players[self.pid_lookup[result[0]]].name)
			self.display('Score: ' + str(result[1]))
			return result

# The following is for debug
study_case = Board(5)
study_case.b = ['','w','b','b','b','w','','b','','b','','b','b','b','b','w','b','w','b','w','','w','','w','']