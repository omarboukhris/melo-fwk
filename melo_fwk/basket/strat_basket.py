from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd

from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.market_data.product import Product
from melo_fwk.strategies import BaseStrategy
from melo_fwk.utils.weights import Weights


@dataclass
class StratBasket:
	strat_list: List[BaseStrategy]
	weights: Weights

	def __post_init__(self):
		assert len(self.strat_list) == len(self.weights.weights), \
			f"(StratBasket) len(strats) != len(weights) [{len(self.strat_list)} != {len(self.weights.weights)}]"

	def forecast_cumsum_product(self, product: Product) -> pd.Series:
		f_series = np.array([0.] * len(product.get_close_series()))

		for trading_rule, forecast_weight in zip(self.strat_list, self.weights.weights):
			f_series += forecast_weight * trading_rule.forecast_vect_cap(product.get_close_series()).to_numpy()

		return pd.Series(f_series * self.weights.divmult)

	def forecast_cumsum(self, product_basket: ProductBasket) -> pd.DataFrame:
		prod_basket_close_df = product_basket.close_df()
		len_df = len(prod_basket_close_df)
		f_df = pd.DataFrame({
			p.name: np.zeros(shape=len_df)
			for p in product_basket.products.values()
		}, index=prod_basket_close_df.index)

		# add div mult at some point
		for trading_rule, forecast_weight in zip(self.strat_list, self.weights.weights):
			f_df += forecast_weight * trading_rule.forecast_df_cap(prod_basket_close_df)

		return f_df * self.weights.divmult

	@classmethod
	def empty(cls):
		return StratBasket(
			strat_list=[],
			weights=Weights([], 0.)
		)

	def to_dict(self):
		# add weights export
		return {
			"strat_list": {
				type(s).__name__: s.to_dict()
				for s in self.strat_list
			},
			"weights": self.weights.to_dict()
		}
