class InvalidMoveException(Exception):
	pass

class Board(object):
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
			raise InvalidMoveException()
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
