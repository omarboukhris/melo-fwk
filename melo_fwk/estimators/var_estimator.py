
import tqdm

from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.basket.start_basket import StratBasket
from melo_fwk.basket.var_basket import VaRBasket
from melo_fwk.estimators.base_estimator import MeloBaseEstimator
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem
from melo_fwk.trading_systems import TradingSystem
from melo_fwk.var.CVaR import CVaR
from melo_fwk.var.VaR import VaR99


class VaREstimator(MeloBaseEstimator):

	def __init__(self, **kwargs):
		super(VaREstimator, self).__init__(**kwargs)
		self.logger.info("VaREstimator Initialized")

		self.var_process = self.next_str_param("all")  # all is VaR99 and ES
		self.n_days = self.next_int_param(1)
		self.method = self.next_str_param("mc")
		self.sim_param = self.next_int_param(1000) if self.method == "mc" else self.next_float_param(0.8)
		self.gen_path = self.next_int_param(0) != 0

	def run(self):
		out_dict = dict()

		self.logger.info(f"Running Estimatior on {len(self.products)} Products")
		strat_basket = StratBasket(
			strat_list=self.strategies,
			weights=self.forecast_weights,
		)
		trading_subsys = TradingSystem(
			strat_basket=strat_basket,
			size_policy=self.size_policy
		)

		prd_list, tsar_list = [], []
		for i, (product_name, product) in tqdm.tqdm(enumerate(self.products.items()), leave=False):
			y_prod = product.get_years(list(range(self.begin, self.end)))
			tsar = trading_subsys.run_product(y_prod)
			prd_list.append(y_prod)
			tsar_list.append(tsar)

		self.logger.info(f"Simulation Done, Computing VaR...")
		params = f"Params = [ndays={self.n_days}, sim_param={self.sim_param}, method={self.method}, gen_path={self.gen_path}"
		self.logger.info(params)

		var_basket = VaRBasket(tsar_list, prd_list)
		if self.var_process == "all":
			out_dict["var99"] = VaR99(var_basket, self.n_days, self.sim_param, self.method, self.gen_path)
			out_dict["cvar"] = CVaR(var_basket, self.n_days, self.sim_param, self.method, self.gen_path)
			out = f"VaR99 = {out_dict['var99']} | {params}\n"
			out += f"CVaR = {out_dict['cvar']} | {params}"
		elif self.var_process == "var99":
			out_dict["var99"] = VaR99(var_basket, self.n_days, self.sim_param, self.method, self.gen_path)
			out = f"VaR99 = {out_dict['var99']} | {params}"
		else:  # if self.var_process == "cvar":
			out_dict["cvar"] = CVaR(var_basket, self.n_days, self.sim_param, self.method, self.gen_path)
			out = f"CVaR = {out_dict['cvar']} | {params}"

		self.logger.info(out)

		self.logger.info("Finished running estimator")
		return out_dict, var_basket

