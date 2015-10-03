class InvalidMove(Exception):
	pass

class B(object):
	def __init__(self,s):
		self.s = s
		self.b = ['']*s*s
		self.history = [tuple(self.b[:])]
		self._VALUES = ('b','w')
		self._last_move = None
		self._is_over = False
	def _getij(self,i,j):
		assert i<self.s
		assert j<self.s
		return self.b[i*self.s+j]
	def _setij(self,i,j,value=''):
		assert i<self.s
		assert j<self.s
		self.b[i*self.s+j] = value
	def __getitem__(self,t):
		assert len(t)==2
		return self._getij(*t)
	def __setitem__(self,t,value):
		assert self._getij(*t)==''
		assert value in self._VALUES
		self._setij(*t,value=value)
		self._last_move = t
		self._update()
	def _get_connections(self,i,j,loose=False):
		col = self._getij(i,j)
		if col=='': return None
		return self._get_conn_rec(i,j,col,loose=loose)
	def _get_conn_rec(self,i,j,col,checked=None,loose=False):
		if not checked: checked=[]
		curr = self._getij(i,j)
		conn = []
		if curr in checked: return []
		checked.append((i,j))
		if curr!=col: return []
		conn.append((i,j))
		neighbours = self._get_neighbours_loose(i,j) if loose else self._get_neighbours(i,j)
		for n in neighbours:
			if n in checked: continue
			if self._getij(*n)==curr:
				conn+=self._get_conn_rec(n[0],n[1],col,checked=checked,loose=loose)
		return conn
	def _get_neighbours(self,i,j):
		neighbours = []
		if i>0: neighbours.append((i-1,j))
		if i<self.s-1: neighbours.append((i+1,j))
		if j>0: neighbours.append((i,j-1))
		if j<self.s-1: neighbours.append((i,j+1))
		return neighbours
	def _get_neighbours_loose(self,i,j):
		neighbours = []
		neighbours += self._get_neighbours(i,j)
		if i>0 and j>0: neighbours.append((i-1,j-1))
		if i<self.s-1 and j>0: neighbours.append((i+1,j-1))
		if i<self.s-1 and j<self.s-1: neighbours.append((i+1,j+1))
		if i> 0 and j<self.s-1: neighbours.append((i-1,j+1))
		return neighbours
	def _get_cluster_neighbours(self,cluster):
		n = []
		for c in cluster:
			n+=[x for x in self._get_neighbours(*c) if x not in cluster]
		return n
	def _is_cornered(self,cluster):
		neighbours = self._get_cluster_neighbours(cluster)
		uniq = set([self._getij(*n) for n in neighbours])
		if len(uniq)!=1 or uniq.pop()=='': return False
		return True
	def _remove_cluster(self,cluster):
		for c in cluster:
			self._setij(*c)
	def _pass(self):
		if not self._last_move:
			self._is_over = True
		self._last_move = None
	def assess(self,full_result=False):
		"""Decides winner
		Returns winner and dictionary with score for each player if :full_result is true
		{'b':10,'w':0}"""
		b_score = sum([x=='b' for x in self.b])
		w_score = sum([x=='w' for x in self.b])
		winner = ''
		if b_score>w_score: winner = 'b'
		elif w_score>b_score: winner = 'w'
		if full_result: winner = (winner,{'b':b_score,'w':w_score})
		return winner
	def _update(self):
		board_save = self.b[:]
		remaining_cells = [(i,j) for i in range(self.s) for j in range(self.s)]
		last_move_clust = []
		while remaining_cells:
			curr = remaining_cells[0]
			conn = self._get_connections(*curr)
			if conn == None:
				remaining_cells.pop(0)
				continue
			for c in conn:
				remaining_cells.pop(remaining_cells.index(c))
			if self._last_move in conn:
				last_move_clust = conn
				continue
			if self._is_cornered(conn):
				self._remove_cluster(conn)
		if self._is_cornered(last_move_clust):
			self._remove_cluster(last_move_clust)
		if tuple(self.b) in self.history:
			self.b = board_save
			raise InvalidMove()
		self.history.append(tuple(self.b[:]))
	def __str__(self):
		lookup = {'':' ','b':'x','w':'o'}
		table = [[lookup[self._getij(i,j)] for j in range(self.s)] for i in range(self.s)]
		string = '  '+' '.join([str(x%10) for x in range(self.s)])+'\n'
		string += '%s|'+'|\n%s|'.join(['|'.join(x) for x in table])+'|'
		string = string%tuple([x%10 for x in range(self.s)])
		return string
	def __repr__(self):
		return self.__str__()

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

def get_clusters(b,col,loose=False):
	clusters = []
	remaining_cells = [(i,j) for i in range(b.s) for j in range(b.s)]
	while remaining_cells:
		curr = remaining_cells[0]
		if b[curr] != col:
			remaining_cells.pop(0)
			continue
		conn = b._get_conn_rec(curr[0],curr[1],col,loose=loose) #._get_connections(*curr,loose=loose)
		for c in conn:
			remaining_cells.pop(remaining_cells.index(c))
		clusters.append(conn)
	return clusters

def get_eyes(b,col,loose=False):
	empty_clusters = get_clusters(b,'')
	small_empty_clusters = [c for c in empty_clusters if len(c)<=3]
	cluster_neighbours = [set([b[n] for n in b._get_cluster_neighbours(c)]) for c in small_empty_clusters]
	eyes = [c for c,n in zip(small_empty_clusters,cluster_neighbours) if len(n)==1 and n.pop()==col]
	return eyes

def scal(x,y):
	return sum([a*b for a,b in zip(x,y)])

WEIGHTS = {
	'n_clusters_own':-1.5,
	'n_clusters_other':1.5,
	'n_loose_clusters_own':-1.5,
	'n_loose_clusters_other':1.5,
	'n_own':1.,
	'n_other':-1.,
	'n_liberties_own':1.5,
	'n_liberties_other':-1.5,
	'n_own_eyes':6.,
	'n_other_eyes':-6.,
	'own_low_liberty_clusters':-3.,
	'other_low_liberty_clusters':4.
}

#TODO: add feature corresponding to number of clusters with only one liberty

def heuristic(b,col,weights = WEIGHTS,ret_features=False):
	col_int = COL_TO_INT[col]
	other_col = INT_TO_COL[(col_int+1)%2]
	own_clusters = get_clusters(b,col)
	other_clusters = get_clusters(b,other_col)
	own_loose_clusters = get_clusters(b,col,loose=True)
	other_loose_clusters = get_clusters(b,other_col,loose=True)
	own_cluster_neighbours = [set(b._get_cluster_neighbours(c)) for c in own_clusters]
	other_cluster_neighbours = [set(b._get_cluster_neighbours(c)) for c in other_clusters]
	own_neighbours = set([item for sublist in [b._get_cluster_neighbours(c) for c in own_clusters] for item in sublist])
	other_neighbours = set([item for sublist in [b._get_cluster_neighbours(c) for c in other_clusters] for item in sublist])
	own_eyes = get_eyes(b,col)
	other_eyes = get_eyes(b,other_col)
	n_clusters_own = float(len(own_clusters))
	n_clusters_other = float(len(other_clusters))
	n_loose_clusters_own = float(len(own_loose_clusters))
	n_loose_clusters_other = float(len(other_loose_clusters))
	n_own = float(len(reduce(lambda x,y:x+y,own_clusters,[])))
	n_other = float(len(reduce(lambda x,y:x+y,other_clusters,[])))
	n_liberties_own = float(len(own_neighbours))
	n_liberties_other = float(len(other_neighbours))
	n_own_eyes = float(len(own_eyes))
	n_other_eyes = float(len(other_eyes))
	own_low_liberty_clusters = sum([len(c)*1./len(n) for c,n in zip(own_clusters,own_cluster_neighbours)])
	other_low_liberty_clusters = sum([len(c)*1./len(n) for c,n in zip(other_clusters,other_cluster_neighbours)])
	features = {
		'n_clusters_own':n_clusters_own,
		'n_clusters_other':n_clusters_other,
		'n_loose_clusters_own':n_loose_clusters_own,
		'n_loose_clusters_other':n_loose_clusters_other,
		'n_own':n_own,
		'n_other':n_other,
		'n_liberties_own':n_liberties_own,
		'n_liberties_other':n_liberties_other,
		'n_own_eyes':n_own_eyes,
		'n_other_eyes':n_other_eyes,
		'own_low_liberty_clusters':own_low_liberty_clusters,
		'other_low_liberty_clusters':other_low_liberty_clusters
	}
	# features = [n_clusters_other/n_clusters_own,n_loose_clusters_other/n_loose_clusters_own,n_own/n_other,n_liberties_own/n_liberties_other,n_own_eyes,n_other_eyes]

	# features = [n_clusters_other,n_clusters_own,n_loose_clusters_other,n_loose_clusters_own,n_own,n_other,n_liberties_own,n_liberties_other,n_own_eyes,n_other_eyes]
	# result = scal(weights,features)
	result = sum([f*weights[k] for k,f in features.items()])
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
		temp_board = B(board.s)
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
				except InvalidMove:
					continue
				h = heuristic(temp_board,color)
				hlist.append((h,c))
			hlist.sort(reverse=True)
			available = [x[1] for x in hlist][:min(self.pruning,len(hlist))]
		for c in available:
			try:
				temp_board = self.simulate_move(board,c,color_move)
			except InvalidMove:
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
			except InvalidMove:
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
		self.b = B(size) if not board else board
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
		color_lookup = {0:'b',1:'w'}
		try:
			while(True):
				print self.b
				not_moved = True
				print '\nPlayer %s?'%str(curr_player+1)
				while(True):
					try:
						i,j = self._play(curr_player)
					except ValueError:
						print 'Invalid entry. Use the format: x,y'
						continue
					except PassException:
						self.b._pass()
						break
					try:
						self.b[i,j] = color_lookup[curr_player]
						break
					except (AssertionError, InvalidMove):
						print 'Invalid move'
						continue
				print '\n'
				if self.b._is_over:
					raise GameOverException()
				curr_player=(curr_player+1)%2
		except ExitException:
			print 'Game exited by user'
		except GameOverException:
			result = self.b.assess(full_result=True)
			print 'Game is Over'
			print 'Winner: ' + result[0]
			print 'Score: ' + str(result[1])
			return result

# The following is for debug
study_case = B(5)
study_case.b = ['','w','b','b','b','w','','b','','b','','b','b','b','b','w','b','w','b','w','','w','','w','']