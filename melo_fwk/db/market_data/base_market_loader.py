import json
import random
from pathlib import Path
from typing import List, Tuple

from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.db.market_data.product import Product


class BaseMarketLoader:
	parent_folder = Path(Path(__file__).parent)

	def __init__(self):
		with open(BaseMarketLoader.parent_folder / "config/products_config.json") as fp:
			self.product_config = json.load(fp)

	def load_product_basket(self, product_basket_config: dict) -> ProductBasket:
		raise NotImplemented

	def _load_product(self, product: str) -> Product:
		raise NotImplemented

	def get_fx(self) -> List[Product]:
		raise NotImplemented

	def get_commodities(self) -> List[Product]:
		raise NotImplemented

	def products_pool(self) -> List[Product]:
		return self.get_commodities() + self.get_fx()

	def shuffled_pool(self) -> List[Product]:
		pool = self.products_pool()
		random.shuffle(pool)
		return pool

	def sample_products(self, n_products: int) -> List[Product]:
		shuffled_pool = self.shuffled_pool()
		assert 0. < n_products < len(shuffled_pool), \
			f"(MarketDataLoader) Invalid sampling ratio provided {n_products} not in [0 ,{size}]"
		return random.sample(shuffled_pool, n_products)

	def sample_products_alpha(self, alpha: float) -> List[Product]:
		assert 0. < alpha <= 1., \
			f"(MarketDataLoader) Invalid sampling ratio provided {alpha} not in [0 ,1]"
		shuffled_pool = self.shuffled_pool()
		return random.sample(shuffled_pool, int(len(shuffled_pool) * alpha))

