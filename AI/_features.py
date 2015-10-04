def get_clusters(board,col,loose=False):
	clusters = []
	remaining_cells = [(i,j) for i in range(board.s) for j in range(board.s)]
	while remaining_cells:
		curr = remaining_cells[0]
		if board[curr] != col:
			remaining_cells.pop(0)
			continue
		conn = board._get_conn_rec(curr[0],curr[1],col,loose=loose) #._get_connections(*curr,loose=loose)
		for c in conn:
			remaining_cells.pop(remaining_cells.index(c))
		clusters.append(conn)
	return clusters

def get_eyes(board,col,loose=False):
	empty_clusters = get_clusters(board,'')
	small_empty_clusters = [c for c in empty_clusters if len(c)<=3]
	cluster_neighbours = [set([board[n] for n in board._get_cluster_neighbours(c)]) for c in small_empty_clusters]
	eyes = [c for c,n in zip(small_empty_clusters,cluster_neighbours) if len(n)==1 and n.pop()==col]
	return eyes

def extract_features(board):
	clusters = {'b':get_clusters(board,'b'),'w':get_clusters(board,'w')}
	loose_clusters = {'b':get_clusters(board,'b',loose=True),'w':get_clusters(board,'w',loose=True)}
	cluster_neighbours = {
		'b':[set(board._get_cluster_neighbours(c)) for c in clusters['b']],
		'w':[set(board._get_cluster_neighbours(c)) for c in clusters['w']]
		}
	neighbours = {
		'b':set([item for sublist in [board._get_cluster_neighbours(c) for c in clusters['b']] for item in sublist]),
		'w':set([item for sublist in [board._get_cluster_neighbours(c) for c in clusters['w']] for item in sublist])
		}
	eyes = {'b':get_eyes(board,'b'),'w':get_eyes(board,'w')}
	n_clusters = {'b':float(len(clusters['b'])),'w':float(len(clusters['w']))}
	n_loose_clusters = {'b':float(len(loose_clusters['b'])),'w':float(len(loose_clusters['b']))}
	n_stones = {'b':float(len(reduce(lambda x,y:x+y,clusters['b'],[]))),'w':float(len(reduce(lambda x,y:x+y,clusters['w'],[])))}
	n_liberties = {'b':float(len(neighbours['b'])),'w':float(len(neighbours['w']))}
	n_eyes = {'b':float(len(eyes['b'])),'w':float(len(eyes['w']))}
	low_liberty_clusters = {'b':sum([len(c)*1./len(n) for c,n in zip(clusters['b'],cluster_neighbours['b'])]),'w':sum([len(c)*1./len(n) for c,n in zip(clusters['w'],cluster_neighbours['w'])])}
	features = {
		'n_clusters':n_clusters,
		'n_loose_clusters':n_loose_clusters,
		'n_stones':n_stones,
		'n_liberties':n_liberties,
		'n_eyes':n_eyes,
		'low_liberty_clusters':low_liberty_clusters
	}
	return features