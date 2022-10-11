
import tqdm

from melo_fwk.datastreams.product import Product
from melo_fwk.policies.vol_target_policy import ConstSizePolicy, VolTarget
from melo_fwk.trading_system import TradingSystem

class BacktestEstimator:

	def __init__(
		self,
		balance: float,
		products: dict,
		time_period: list,
		strategies: list = None,  # change to buy and hold
		forecast_weights: list = None,  # change to [1.0] by default
		size_policy_class_: callable = ConstSizePolicy,
		estimator_params: list = None
	):
		assert len(strategies) == len(forecast_weights), \
			"(BacktestEstimator) Strategies and Forecast weight do not correspond."

		self.products = products
		self.balance = balance
		self.time_period = time_period
		self.strategies = strategies
		self.forecast_weights = forecast_weights
		self.size_policy_class_ = size_policy_class_
		self.reinvest = "reinvest" in estimator_params

	def run(self):
		out_dict = dict()
		for product_name, product_dataclass in self.products.items():
			out_dict[product_name] = self._trade_product(product_dataclass)
		return out_dict

	def _trade_product(self, product: Product):
		balance = self.balance
		results = []
		product.datastream.with_daily_returns()
		product.datastream.parse_date_column()

		for year in tqdm.tqdm(range(int(self.time_period[0]), int(self.time_period[1]))):
			vol_target = VolTarget(
				annual_vol_target=1e-1,
				trading_capital=balance if self.reinvest else self.balance)
			size_policy = self.size_policy_class_(risk_policy=vol_target)

			trading_subsys = TradingSystem(
				data_source=product.datastream.get_data_by_year(year),
				trading_rules=self.strategies,
				forecast_weights=self.forecast_weights,
				size_policy=size_policy
			)

			trading_subsys.run()
			tsar = trading_subsys.get_tsar()
			results.append(tsar)
			balance += tsar.annual_delta()

		return results
