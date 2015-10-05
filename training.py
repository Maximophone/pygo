import pygo
from core._features import naive_weights
from core._ai import AIMinimax
import random

class Trainer(object):
	def __init__(self):
		self.trained_weights = None
	def train(self,max_iterations):
		pass

class PseudoGenetic(Trainer):
	def _copy_weights(self,weights):
		return {k:v[:] for k,v in weights.iteritems()}
	def _mutate_one(self,weights,amplitude=2):
		wkey = random.choice(weights.keys())
		col = random.choice([0,1])
		variation = random.gauss(0,amplitude)
		new_weights = self._copy_weights(weights)
		new_weights[wkey][col] += variation
		return new_weights
	def _mutate(self,weights,n,random_n=True):
		if random_n:
			n_mutations = random.choice(range(1,n))
		else:
			n_mutations = n
		mutated_weights = self._copy_weights(weights)
		for _ in range(n-1):
			mutated_weights = self._mutate_one(mutated_weights)
		return mutated_weights
	def train(self,max_iterations):
		weights_origin = naive_weights
		for _ in range(max_iterations):
			weights_mutated = self._mutate(weights_origin,3)
			AI_origin = AIMinimax('origin',depth=0,weights=weights_origin)
			AI_mutated = AIMinimax('mutated',depth=0,weights=weights_mutated)
			go = pygo.Go(5,player1=AI_origin,player2=AI_mutated,display_on=False,auto_start=False)
			result = go.start()
			if result[0] == 'w': weights_origin = weights_mutated
		self.trained_weights = weights_origin
	def play(self):
		if not self.trained_weights: return 'Not trained'
		AI = AIMinimax('trained',depth=1,weights=self.trained_weights)
		pygo.Go(5,player2=AI)