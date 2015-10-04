class ExitException(Exception):
	pass

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