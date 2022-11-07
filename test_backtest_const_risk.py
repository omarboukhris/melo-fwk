import numpy as np

from melo_fwk.market_data import CommodityDataLoader
from melo_fwk.trading_systems import TradingSystem
from melo_fwk.strategies import EWMAStrategy
from melo_fwk.policies.size import VolTargetInertiaPolicy

from melo_fwk.plots import TsarPlotter


product = CommodityDataLoader.Gold

strat = [
	EWMAStrategy(
		fast_span=16,
		slow_span=64,
		scale=16.,
	),
	EWMAStrategy(
		fast_span=8,
		slow_span=32,
		scale=10.,
	)
]
fw = [0.6, 0.4]

balance = 60000

size_policy = VolTargetInertiaPolicy(
	annual_vol_target=0.25,
	trading_capital=balance)

trading_subsys = TradingSystem(
	product=product,
	trading_rules=strat,
	forecast_weights=fw,
	size_policy=size_policy
)


# tsar = trading_subsys.run()
# print(balance + tsar.balance_delta())
# results = {f"Gold_{year}_it": tsar.get_year(year) for year in product.years()}

results = {f"Gold_{year}_it": trading_subsys.run_year(year) for year in product.years()}
print(balance + np.sum([r.balance_delta() for r in results.values()]))

tsar_plotter = TsarPlotter({"pname": results})
tsar_plotter.save_fig(export_folder="data/residual", mute=True)
