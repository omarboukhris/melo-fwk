import tqdm

from melo_fwk.datastreams.commodities import CommodityDataLoader

from melo_fwk.rules.ewma import EWMATradingRule
from melo_fwk.rules.sma import SMATradingRule

from melo_fwk.policies.vol_target_policy import VolTarget, VolTargetSizePolicy

from melo_fwk.trading_systems.trading_vect_system import TradingVectSystem

from melo_fwk.plots.tsar_plots import TsarPlotter

import numpy as np

product = CommodityDataLoader.Gold
# do this by default
product.datastream.parse_date_column()
product.datastream.with_daily_returns()

strat = [
	EWMATradingRule(
		fast_span=16,
		slow_span=64,
		scale=8.,
		cap=20,
	),
	# SMATradingRule(
	# 	fast_span=4,
	# 	slow_span=32,
	# 	scale=10.,
	# 	cap=20,
	# )
]
# fw = [0.4, 0.6]
fw = [1.]

results = {}

balance = 60000

for year in tqdm.tqdm(range(2004, 2008)):
	vol_target = VolTarget(
		annual_vol_target=1e-1,
		trading_capital=balance)
	size_policy = VolTargetSizePolicy(risk_policy=vol_target)

	trading_subsys = TradingVectSystem(
		data_source=product.datastream.get_data_by_year(year),
		trading_rules=strat,
		forecast_weights=fw,
		size_policy=size_policy
	)

	trading_subsys.trade_vect()
	tsar = trading_subsys.get_tsar()
	results.update({f"Gold_{year}": tsar})
	balance += tsar.annual_delta()

tsar_plotter = TsarPlotter({"pname": results})
tsar_plotter.save_fig()
