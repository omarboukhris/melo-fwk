from dataclasses import dataclass
from typing import List

from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.pose_size import BaseSizePolicy
from melo_fwk.strategies import BaseStrategy
from melo_fwk.utils.weights import Weights

@dataclass(frozen=True)
class MeloClustersConfig:
	product_baskets: List[ProductBasket]
	strats_list: List[StratBasket]
	pose_size_list: List[BaseSizePolicy]

