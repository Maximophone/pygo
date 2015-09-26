class B(object):
	def __init__(self,s):
		self.s = s
		self.b = ['']*s*s
		self._VALUES = ('b','w')
		self._last_move = None
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
	def _get_connections(self,i,j):
		col = self._getij(i,j)
		if col=='': return None
		return self._get_conn_rec(i,j,col)
	def _get_conn_rec(self,i,j,col,checked=None):
		if not checked: checked=[]
		curr = self._getij(i,j)
		conn = []
		if curr in checked: return []
		checked.append((i,j))
		if curr!=col: return []
		conn.append((i,j))
		neighbours = self._get_neighbours(i,j)
		for n in neighbours:
			if n in checked: continue
			if self._getij(*n)==curr:
				conn+=self._get_conn_rec(n[0],n[1],col,checked=checked)
		return conn
	def _get_neighbours(self,i,j):
		neighbours = []
		if i>0: neighbours.append((i-1,j))
		if i<self.s-1: neighbours.append((i+1,j))
		if j>0: neighbours.append((i,j-1))
		if j<self.s-1: neighbours.append((i,j+1))
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
	def _update(self):
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
	def __str__(self):
		lookup = {'':' ','b':'x','w':'o'}
		table = [[lookup[self._getij(i,j)] for j in range(self.s)] for i in range(self.s)]
		string = '  '+' '.join([str(x%10) for x in range(self.s)])+'\n'
		string += '%s|'+'|\n%s|'.join(['|'.join(x) for x in table])+'|'
		string = string%tuple([x%10 for x in range(self.s)])
		return string
	def __repr__(self):
		return self.__str__()

class Go(object):
	def __init__(self,size=19,ai=False):
		self.ai = ai
		self.b = B(size)
		if ai: self._ai = AISimple(self.b)
		self.start()
	def _play(self,ai):
		if not ai:
			coords = raw_input()
			i,j = self._parse_coords(coords)
			i=int(i)
			j=int(j)
			return (i,j)
		else:
			decision = self._ai.decide('w')
			print 'AI plays %s,%s'%decision
			return decision
	def _parse_coords(self,coords):
		i,j = coords.split(',')
		return (i,j)
	def start(self):
		print 'GO'
		curr_player = 0
		player_lookup = {0:'b',1:'w'}
		while(True):
			print self.b
			not_moved = True
			print '\nPlayer %s?'%str(curr_player+1)
			while(True):
				try:
					i,j = self._play(self.ai and curr_player)
				except ValueError:
					print 'Invalid entry. Use the format: x,y'
					continue
				try:
					self.b[i,j] = player_lookup[curr_player]
					break
				except AssertionError:
					print 'Invalid move'
					continue

			print '\n'
			curr_player=(curr_player+1)%2

import random

COL_TO_INT = {'b':0,'w':1}
INT_TO_COL = {0:'b',1:'w'}

debug_ai = False

def get_clusters(b,col):
	clusters = []
	remaining_cells = [(i,j) for i in range(b.s) for j in range(b.s)]
	while remaining_cells:
		curr = remaining_cells[0]
		if b[curr] != col:
			remaining_cells.pop(0)
			continue
		conn = b._get_connections(*curr)
		for c in conn:
			remaining_cells.pop(remaining_cells.index(c))
		clusters.append(conn)
	return clusters

def heuristic(b,col,weights = [1.,1.,2.]):
	col_int = COL_TO_INT[col]
	own_clusters = get_clusters(b,col)
	other_clusters = get_clusters(b,INT_TO_COL[(col_int+1)%2])
	own_neighbours = set([item for sublist in [b._get_cluster_neighbours(c) for c in own_clusters] for item in sublist])
	other_neighbours = set([item for sublist in [b._get_cluster_neighbours(c) for c in other_clusters] for item in sublist])
	n_clusters_own = float(len(own_clusters))
	n_clusters_other = float(len(other_clusters))
	n_own = float(len(reduce(lambda x,y:x+y,own_clusters,[])))
	n_other = float(len(reduce(lambda x,y:x+y,other_clusters,[])))
	n_liberties_own = float(len(own_neighbours))
	n_liberties_other = float(len(other_neighbours))
	return weights[0]*n_clusters_other/n_clusters_own + weights[1]*n_own/n_other + weights[2]*n_liberties_own/n_liberties_other

class AI(object):
	def __init__(self,board):
		self._board = board
	def decide(self,color):
		available = [(i,j) for i in range(self._board.s) for j in range(self._board.s) if self._board[i,j]=='']
		return random.choice(available)

class AISimple(AI):
	def decide(self,color):
		available = [(i,j) for i in range(self._board.s) for j in range(self._board.s) if self._board[i,j]=='']
		best_move = available[0]
		max_h = -1
		for c in available:
			temp_board = B(self._board.s)
			temp_board.b = self._board.b[:]
			temp_board[c] = color
			h = heuristic(temp_board,color)
			if debug_ai:
				print 'Evaluating move:'
				print temp_board
				print 'Heuristic:'
				print h
			if h>max_h:
				max_h = h
				best_move = c
		print max_h
		return best_move