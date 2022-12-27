
from dataclasses import dataclass
from typing import List

@dataclass
class Weights:
	weights: List[float]
	divmult: float

	def to_dict(self):
		return {
			"weights": self.weights,
			"divmult": self.divmult
		}
