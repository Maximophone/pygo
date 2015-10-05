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
		if move is None: return temp_board
		temp_board[move] = color
		return temp_board

class AISimple(AI):
	def __init__(self,name,pruning=4,depth=2):
		self.pruning = pruning
		self.depth = depth
		super(AISimple,self).__init__(name)
	def deep_search(self,heuristic,board,color,depth,color_move=None):
		if debug_ai: print 'board: '
		if debug_ai: print board
		if depth==0: return heuristic(board,color)
		col_int = _COL_TO_INT[color]
		other_color = _INT_TO_COL[(col_int+1)%2]
		if not color_move: color_move = other_color
		col_move_int = _COL_TO_INT[color_move]
		other_color_move = _INT_TO_COL[(col_move_int+1)%2]
		available = [(i,j) for i in range(board.s) for j in range(board.s) if board[i,j]=='']
		optimum_h = -1e30 if color == color_move else 1e30
		if self.pruning:
			if debug_ai: print 'pruning'
			hlist = []
			for c in available:
				try:
					temp_board = self.simulate_move(board,c,color_move)
				except InvalidMoveException:
					continue
				if debug_ai: print 'testing board '
				if debug_ai: print temp_board
				h = heuristic(temp_board,color)
				if debug_ai: print 'heuristic: ' + str(h)
				hlist.append((h,c))
			hlist.sort(reverse=True)
			available = [x[1] for x in hlist][:min(self.pruning,len(hlist))]
			if debug_ai: print 'selecting: '
			if debug_ai: print hlist[:min(self.pruning,len(hlist))]
		for c in available:
			if debug_ai: print 'recursing for move: '
			if debug_ai: print c
			try:
				temp_board = self.simulate_move(board,c,color_move)
			except InvalidMoveException:
				continue
			h = self.deep_search(heuristic,temp_board,color,depth-1,color_move=other_color_move)
			if (h>optimum_h and color == color_move) or (h<optimum_h and color != color_move) :
				optimum_h = h
				if debug_ai: print 'new optimal h: ' + str(h)
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
			depth = self.depth
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

def argmax(function,index,ret_value=False):
	current_max = None
	idx_max = None
	for idx in index[1:]:
		value = function(idx)
		if current_max is None or value > current_max:
			current_max = value
			idx_max = idx
	if ret_value: return idx_max,current_max
	return idx_max

class AIMinimax(AI):
	def __init__(self,name,depth=1,extract_features=extract_features,weights=naive_weights):
		self.depth = depth
		self.extract_features = extract_features
		self.weights = weights
		super(AIMinimax,self).__init__(name)
	def _available(self,board,col):
		available = [(i,j) for i in range(board.s) for j in range(board.s) if board[i,j]=='']
		yield None,self.simulate_move(board,None,_INT_TO_COL[col])
		for c in available:
			try:
				yield c,self.simulate_move(board,c,_INT_TO_COL[col])
			except InvalidMoveException:
				continue
	def _decide(self,board,col,depth):
		ncol = (col+1)%2
		available_moves = list(self._available(board,col))
		best_move = argmax(lambda x: self._score(x[1],col,ncol,depth),available_moves)
		return best_move
	def _score(self,board,col,col_turn,depth):
		if depth==0:
			return heuristic(board,_INT_TO_COL[col],self.extract_features,self.weights)
		ncol_turn = (col_turn+1)%2
		available_moves = self._available(board,col)
		if col==col_turn:
			return max([self._score(b,col,ncol_turn,depth-1) for c,b in available_moves])
		else:
			return min([self._score(b,col,ncol_turn,depth-1) for c,b in available_moves])
	def decide(self,board,color):
		col = _COL_TO_INT[color]
		move = self._decide(board,col,self.depth)
		if move is not None: return move[0]
		return None