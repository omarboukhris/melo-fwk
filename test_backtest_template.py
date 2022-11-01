import tqdm

from melo_fwk.market_data import CommodityDataLoader
from melo_fwk.trading_systems import TradingSystem
from melo_fwk.strategies import EWMAStrategy
from melo_fwk.size_policies import VolTargetSizePolicy, VolTargetInertiaPolicy
from melo_fwk.size_policies.vol_target import VolTarget

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

results = {}

balance = 60000

vol_target = VolTarget(
	annual_vol_target=1.,
	trading_capital=balance)
size_policy = VolTargetInertiaPolicy(
	risk_policy=vol_target,
	block_size=product.block_size
)

"""
Trades each year individually
No position is open by the end of the year
"""
for year in tqdm.tqdm(product.years(), leave=True):
	# for year in product.years():

	y_prod = product.get_year(year)

	trading_subsys = TradingSystem(
		product=y_prod,
		trading_rules=strat,
		forecast_weights=fw,
		size_policy=size_policy
	)

	tsar = trading_subsys.run().get_data_by_year(year)
	balance += tsar.annual_delta()
	trading_subsys.size_policy.risk_policy.trading_capital = balance
	print(year, balance, tsar.max_drawdown(), abs(tsar.max_drawdown())/balance, tsar.gar())
	results.update({f"Gold_{year}": tsar})

tsar_plotter = TsarPlotter({"pname": results})
tsar_plotter.save_fig(export_folder="data/residual")
print(balance)
