from _features import extract_features, naive_weights
from _player import Player
from _board import Board, InvalidMoveException
import random

_COL_TO_INT = {'b':0,'w':1}
_INT_TO_COL = {0:'b',1:'w'}

debug_ai = False

def heuristic(board,col,extract_features=extract_features,weights = naive_weights,ret_features=False):
	col_int = _COL_TO_INT[col]
	other_col = _INT_TO_COL[(col_int+1)%2]
	
	features = extract_features(board)
	
	result = sum([f[col]*weights[k][0] for k,f in features.items()]) + sum([f[other_col]*weights[k][1] for k,f in features.items()])
	if ret_features:
		return (result,features)
	return result

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
		col_int = _COL_TO_INT[color]
		other_color = _INT_TO_COL[(col_int+1)%2]
		if not color_move: color_move = other_color
		col_move_int = _COL_TO_INT[color_move]
		other_color_move = _INT_TO_COL[(col_move_int+1)%2]
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