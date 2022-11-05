# import matplotlib.pyplot as plt
import pandas as pd
import tqdm

from melo_fwk.market_data import MarketDataLoader
from melo_fwk.strategies import EWMAStrategy
from melo_fwk.trading_systems import TradingSystem


strat = [
	EWMAStrategy(
		fast_span=16,
		slow_span=64,
	)
]

products = MarketDataLoader.sample_products_pool(0.5)

results = {}
for product in tqdm.tqdm(products):
	trading_subsys = TradingSystem(
		product=product,
		trading_rules=strat,
		forecast_weights=[1.],
	)

	results.update({
		f"{product.name}.{year}":
			trading_subsys.run_year(year).forecast_series
		for year in product.years()
	})

mean = []
for result in results.values():
	result.apply(abs).apply(mean.append)

mean_ps = pd.Series(mean)
scale_f = 10/mean_ps.mean()
scaled_ps = (scale_f * mean_ps)
print("mean * scale == scaled mean")
print(mean_ps.mean(), scale_f, scaled_ps.mean())

# plt.hist(mean, bins=100)
# plt.hist(scaled_ps.to_numpy(), bins=100, color="red", alpha=0.5)
# plt.show()

