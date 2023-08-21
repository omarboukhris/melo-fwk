
from dataclasses import dataclass, asdict
from typing import List

@dataclass
class Weights:
	weights: List[float]
	divmult: float

	def to_dict(self):
		return asdict(self)
