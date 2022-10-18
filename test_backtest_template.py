import tqdm

from melo_fwk.market_data.commodities import CommodityDataLoader
from melo_fwk.plots.tsar_plots import TsarPlotter

from melo_fwk.rules.ewma import EWMATradingRule
from melo_fwk.rules.sma import SMATradingRule

from melo_fwk.policies.vol_target_policies.vol_target_size_policy import VolTargetSizePolicy
from melo_fwk.policies.vol_target_policies.vol_target import VolTarget

from melo_fwk.trading_systems.trading_system import TradingSystem

import numpy as np

product = CommodityDataLoader.Gold

strat = [
	EWMATradingRule(
		fast_span=16,
		slow_span=64,
		scale=8.,
		cap=20,
	),
	SMATradingRule(
		fast_span=4,
		slow_span=32,
		scale=10.,
		cap=20,
	)
]
fw = [0.4, 0.6]

results = {}

balance = 60000

for year in tqdm.tqdm(range(2015, 2022)):
	vol_target = VolTarget(
		annual_vol_target=1e-1,
		trading_capital=balance)
	size_policy = VolTargetSizePolicy(risk_policy=vol_target)

	trading_subsys = TradingSystem(
		data_source=product.datastream.get_data_by_year(year),
		trading_rules=strat,
		forecast_weights=fw,
		size_policy=size_policy
	)

	trading_subsys.run()
	tsar = trading_subsys.get_tsar()
	results.update({f"Gold_{year}": tsar})
	balance += tsar.annual_delta()

tsar_plotter = TsarPlotter({"pname": results})
tsar_plotter.save_fig(export_folder="data/residual")

