import json
import random
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.market_data.product import Product


class BaseMarketLoader(ABC):
	parent_folder = Path(Path(__file__).parent)

	def __init__(self):
		with open(BaseMarketLoader.parent_folder / "config/products_config.json") as fp:
			self.product_config = json.load(fp)

	@abstractmethod
	def load_product_basket(self, product_basket_config: dict) -> ProductBasket:
		...

	@abstractmethod
	def _load_product(self, product: str) -> Product:
		...

	@abstractmethod
	def get(self, category: str, product: str) -> Product:
		...

	@abstractmethod
	def get_fx(self) -> List[Product]:
		...

	@abstractmethod
	def get_commodities(self) -> List[Product]:
		...

	def products_pool(self) -> List[Product]:
		return self.get_commodities() + self.get_fx()

	def shuffled_pool(self) -> List[Product]:
		pool = self.products_pool()
		random.shuffle(pool)
		return pool

	def sample_products(self, n_products: int) -> List[Product]:
		shuffled_pool = self.shuffled_pool()
		assert 0. < n_products < len(shuffled_pool), \
			f"(MarketDataLoader) Invalid sampling ratio provided {n_products} not in [0 ,{len(shuffled_pool)}]"
		return random.sample(shuffled_pool, n_products)

	def sample_products_alpha(self, alpha: float) -> List[Product]:
		assert 0. < alpha <= 1., \
			f"(MarketDataLoader) Invalid sampling ratio provided {alpha} not in [0 ,1]"
		shuffled_pool = self.shuffled_pool()
		return random.sample(shuffled_pool, int(len(shuffled_pool) * alpha))

