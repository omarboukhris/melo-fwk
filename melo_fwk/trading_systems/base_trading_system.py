import uuid
from dataclasses import dataclass

from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.basket.results_basket import ResultsBasket
from melo_fwk.basket.strat_basket import StratBasket
from melo_fwk.market_data.base_market_loader import BaseMarketLoader
from melo_fwk.market_data.product import Product

from melo_fwk.pose_size import BaseSizePolicy

from melo_fwk.datastreams import TsarDataStream

import pandas as pd

from mutils.quantflow_factory import QuantFlowFactory


@dataclass
class BaseTradingSystem:
	name: str = str(uuid.uuid4())
	strat_basket: StratBasket = StratBasket.empty()
	product_basket: ProductBasket = ProductBasket([])
	size_policy: BaseSizePolicy = BaseSizePolicy(0., 0.)

	def update_trading_capital(self, delta: float):
		self.size_policy.update_trading_capital(delta)

	def run_product(self, product: Product) -> TsarDataStream:
		pass

	def run(self) -> ResultsBasket:
		pass

	def run_year(self, year: int, stitch: bool = False) -> ResultsBasket:
		product_basket = self.product_basket
		self.product_basket = self.product_basket.get_year(year, stitch)
		self.size_policy.setup_product_basket(self.product_basket)
		try:
			results = self.run()
			return results if stitch else results.get_year(year)
		finally:
			self.product_basket = product_basket

	def run_product_year(self, product: Product, year: int, stitch: bool = False):
		product = product.get_year(year, stitch)
		self.size_policy.setup_product(product)
		return self.run_product(product).get_year(year) if stitch else self.run_product(product)

	def compound_product_by_year(self, product: Product, stitch: bool = False):
		output = []
		for year in product.years():
			tsar = self.run_product_year(product, year, stitch)
			self.update_trading_capital(tsar.balance_delta())
			output.append(tsar)
		return output

	@staticmethod
	def build_tsar(
		product: Product,
		forecast_series: pd.Series,
		pose_series: pd.Series,
		daily_pnl_series: pd.Series
	) -> TsarDataStream:
		return TsarDataStream(
			name=product.name,
			dataframe=pd.DataFrame({
				"Date": product.get_date_series().reset_index(drop=True),
				"Price": product.get_close_series().reset_index(drop=True),
				"Forecast": forecast_series.reset_index(drop=True),
				"Size": pose_series.reset_index(drop=True),
				"Account": daily_pnl_series.expanding(1).sum().reset_index(drop=True),
				"Daily_PnL": daily_pnl_series.reset_index(drop=True)
			})
		)

	def build_tsar_basket(
		self,
		forecast_df: pd.DataFrame,
		pose_df: pd.DataFrame,
		daily_pnl_df: pd.DataFrame
	) -> ResultsBasket:
		results_list = []
		for product in self.product_basket.products.values():
			results_list.append(TsarDataStream(
				name=product.name,
				dataframe=pd.DataFrame({
					"Date": product.get_date_series(),
					"Price": product.get_close_series(),
					"Forecast": forecast_df[product.name],
					"Size": pose_df[product.name],
					"Account": daily_pnl_df[product.name].expanding(1).sum(),
					"Daily_PnL": daily_pnl_df[product.name]
				})
			))
		return ResultsBasket(results_list)

	def asdict(self):
		return {
			"name": self.name,  # add trading sys name ??
			"product_basket": self.product_basket.to_dict(),
			"strat_basket": self.strat_basket.to_dict(),
			"size_policy": type(self.size_policy).__name__,
			"vol_target": self.size_policy.vol_target.to_dict(),
		}

	@staticmethod
	def from_dict(config: dict, market_mgr: BaseMarketLoader):
		BaseTradingSystem(
			name=config["name"],
			product_basket=market_mgr.load_product_basket(config["product_basket"]),
			strat_basket=QuantFlowFactory.build_strat_basket(config["strat_basket"]),
			size_policy=QuantFlowFactory.get_size_policy(config["size_policy"])(
				**config["vol_target"])
		)

