import tqdm

from melo_fwk.market_data import CommodityDataLoader, FxDataLoader
from melo_fwk.market_data.product import Product
from melo_fwk.trading_systems import TradingSystem
from melo_fwk.strategies import EWMAStrategy
from melo_fwk.size_policies import VolTargetInertiaPolicy
from melo_fwk.size_policies.vol_target import VolTarget
from melo_fwk.plots import TsarPlotter

product = CommodityDataLoader.Gold
# product = FxDataLoader.EURUSD

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
	annual_vol_target=25e-2,
	trading_capital=balance)
size_policy = VolTargetInertiaPolicy(
	risk_policy=vol_target,
	block_size=product.block_size
)

trading_subsys = TradingSystem(
	product=product,
	trading_rules=strat,
	forecast_weights=fw,
	size_policy=size_policy
)

tsar = None
for year in tqdm.tqdm(product.years(), leave=True):
	tsar = trading_subsys.run()
	y_tsar = tsar.get_data_by_year(year)
	results.update({f"Gold_{year}_i": y_tsar})
	balance += y_tsar.annual_delta()
	trading_subsys.size_policy.risk_policy.trading_capital = balance
	print(year, balance, y_tsar.max_drawdown())

tsar_plotter = TsarPlotter({"pname": results})
tsar_plotter.save_fig(export_folder="data/residual")
print(balance)
