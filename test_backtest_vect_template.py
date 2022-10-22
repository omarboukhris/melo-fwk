import tqdm

from melo_fwk.market_data import CommodityDataLoader
from melo_fwk.market_data.product import Product
from melo_fwk.trading_systems import TradingSystem
from melo_fwk.strategies import EWMAStrategy
from melo_fwk.size_policies import (
	VolTargetInertiaPolicy,
	VolTarget
)
from melo_fwk.plots import TsarPlotter

product = CommodityDataLoader.Gold

strat = [
	EWMAStrategy(
		fast_span=16,
		slow_span=64,
		scale=16.,
	),
	EWMAStrategy(
		fast_span=4,
		slow_span=32,
		scale=10.,
	)
]
fw = [0.4, 0.6]

results = {}

balance = 60000

y_prod = Product(
	name=product.name,
	block_size=product.block_size,
	datastream=product.datastream
)

vol_target = VolTarget(
	annual_vol_target=5e-1,
	trading_capital=balance)
size_policy = VolTargetInertiaPolicy(
	risk_policy=vol_target,
	block_size=product.block_size
)

trading_subsys = TradingSystem(
	product=y_prod,
	trading_rules=strat,
	forecast_weights=fw,
	size_policy=size_policy
)

tsar = trading_subsys.run()
for year in tqdm.tqdm(product.years()):
	y_tsar = tsar.get_data_by_year(year)
	results.update({f"Gold_{year}": y_tsar})

tsar_plotter = TsarPlotter({"pname": results})
tsar_plotter.save_fig(export_folder="data/residual")
print(tsar.annual_delta())
