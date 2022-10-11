import tqdm

from melo_fwk.datastreams.commodities import CommodityDataLoader

from melo_fwk.rules.ewma_rule import EWMATradingRule
from melo_fwk.rules.sma_rule import SMATradingRule

from melo_fwk.policies.vol_target_policy import VolTarget, VolTargetSizePolicy

from melo_fwk.utils.trading_system import TradingSystem

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
	SMATradingRule(
		fast_span=4,
		slow_span=32,
		scale=10.,
		cap=20,
	)
]
fw = [0.4, 0.6]

results = []

balance = 60000

for year in tqdm.tqdm(range(2004, 2008)):
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
	results.append(tsar)
	balance += tsar.annual_delta()

sr = [r.account_metrics.sharpe_ratio() for r in results]
balance = [(r.account_metrics.sharpe_ratio(), r.annual_delta()) for r in results]
print(sr)
print(np.array(sr).mean())
print(balance)
print([r.annual_delta() + r.vol_target.trading_capital for r in results])
