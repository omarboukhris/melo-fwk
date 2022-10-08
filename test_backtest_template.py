import tqdm

from melo_tf.datastreams.commodities import CommodityDataLoader

from melo_tf.rules.ewma_rule import EWMATradingRule

from melo_tf.policies.vol_target_policy import VolTarget, VolTargetSizePolicy

from melo_tf.trading_system import TradingSystem

import pandas as pd
import numpy as np

from dataclasses import dataclass

@dataclass(frozen=True)
class TradingSystemAnnualResult:
	final_balance: float
	sharpe_ratio: float
	forecast_df: pd.DataFrame
	size_df: pd.DataFrame
	account_df: pd.DataFrame
	vol_target: VolTarget


product = CommodityDataLoader.Gold
product.datastream.parse_date_column()
product.datastream.with_daily_returns()

strat = [
	EWMATradingRule(
		fast_span=16,
		slow_span=64,
		scale=8.,
		cap=20,
	)
]
fw = [1.]

results = []

trading_subsys = TradingSystem.start(60000)

for year in tqdm.tqdm(range(2004, 2020)):
	vol_target = VolTarget(
		annual_vol_target=0.3,
		trading_capital=trading_subsys.balance())
	size_policy = VolTargetSizePolicy(risk_policy=vol_target)

	trading_subsys = TradingSystem(
		balance=trading_subsys.balance(),
		data_source=product.datastream.get_data_by_year(year),
		trading_rules=strat,
		forecast_weights=fw,
		size_policy=size_policy
	)

	trading_subsys.run()

	results.append(TradingSystemAnnualResult(
		vol_target=vol_target,
		final_balance=trading_subsys.balance(),
		sharpe_ratio=trading_subsys.volatility_normalized_PnL(),
		forecast_df=trading_subsys.forecast_dataframe(),
		size_df=trading_subsys.position_dataframe(),
		account_df=trading_subsys.account_dataframe()
	))

sr = [r.sharpe_ratio for r in results]
balance = [r.final_balance for r in results]
print(sr)
print(np.array(sr).mean())
print(balance)
