
import tqdm

from melo_fwk.market_data.product import Product
from melo_fwk.policies.vol_target_policies.base_size_policy import ConstSizePolicy
from melo_fwk.policies.vol_target_policies.vol_target import VolTarget
from melo_fwk.trading_systems.trading_vect_system import TradingVectSystem

class BacktestEstimator:

	def __init__(
		self,
		products: dict,
		time_period: list,
		strategies: list = None,
		forecast_weights: list = None,
		vol_target: VolTarget = VolTarget(0., 0.),
		size_policy_class_: callable = ConstSizePolicy,
		estimator_params: list = None
	):
		strategies = [] if strategies is None else strategies
		forecast_weights = [] if forecast_weights is None else forecast_weights
		assert len(strategies) == len(forecast_weights), \
			"(BacktestEstimator) Strategies and Forecast weight do not correspond."

		self.products = products
		self.time_period = time_period
		self.strategies = strategies
		self.forecast_weights = forecast_weights
		self.vol_target = vol_target
		self.size_policy_class_ = size_policy_class_
		self.reinvest = "reinvest" in estimator_params

	def run(self):
		out_dict = dict()
		for product_name, product_dataclass in self.products.items():
			out_dict[product_name] = self._trade_product(product_dataclass)
		return out_dict

	def _trade_product(self, product: Product):
		balance = self.vol_target.trading_capital
		results = dict()

		for year in tqdm.tqdm(range(int(self.time_period[0]), int(self.time_period[1]))):
			vol_target = VolTarget(
				annual_vol_target=self.vol_target.annual_vol_target,
				trading_capital=balance if self.reinvest else self.vol_target.trading_capital)
			size_policy = self.size_policy_class_(risk_policy=vol_target)

			trading_subsys = TradingVectSystem(
				data_source=product.datastream.get_data_by_year(year),
				trading_rules=self.strategies,
				forecast_weights=self.forecast_weights,
				size_policy=size_policy
			)

			trading_subsys.trade_vect()
			tsar = trading_subsys.get_tsar()
			# change output file path
			results.update({f"{product.name}_{year}": tsar})
			balance += tsar.annual_delta()

		return results
