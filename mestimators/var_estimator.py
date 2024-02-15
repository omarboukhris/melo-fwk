from melo_fwk.basket.strat_basket import StratBasket
from mestimators.base_estimator import MeloBaseEstimator
from mestimators.utils.var_utils import VaRUtils
from melo_fwk.trading_systems import TradingSystem


class VaREstimator(MeloBaseEstimator):

	def __init__(self, **kwargs):
		super(VaREstimator, self).__init__(**kwargs)
		self.n_days = self.estimator_params_dict.get("n_days", 1)
		self.method = self.estimator_params_dict.get("method", "mc")
		self.sim_param = self.estimator_params_dict.get("sim_param", 1000) \
			if self.method == "mc" else \
			self.estimator_params_dict.get("sim_param", 0.8)
		self.gen_path = self.estimator_params_dict.get("gen_path", 0) != 0
		self.logger.info("VaREstimator Initialized")


	def run(self):
		self.logger.info(f"Running Estimatior on {len(self.products)} Products")
		strat_basket = StratBasket(
			strat_list=self.strategies,
			weights=self.forecast_weights,
		)
		trading_subsys = TradingSystem(
			strat_basket=strat_basket,
			size_policy=self.size_policy
		)

		var_utils = VaRUtils(trading_subsys, self.products)
		var_utils.set_VaR_params(self.n_days, self.method, self.sim_param, self.gen_path)
		return var_utils.run_full_VaR_sim(self.begin, self.end)
