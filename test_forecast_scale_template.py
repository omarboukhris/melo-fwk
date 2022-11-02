import matplotlib.pyplot as plt
import pandas as pd
import tqdm

from melo_fwk.market_data import MarketDataLoader

from melo_fwk.strategies import EWMAStrategy

from melo_fwk.trading_systems import TradingSystem

import random

strat = [
	EWMAStrategy(
		fast_span=16,
		slow_span=64,
	)
]
fw = [0.4, 0.6]

products_loc = MarketDataLoader.get_commodities() + MarketDataLoader.get_fx()
products = [MarketDataLoader.load_datastream(prod) for prod in products_loc ]
random.shuffle(products)
sample_products = random.sample(products, int(len(products)*0.5))

results = {}

for product in tqdm.tqdm(sample_products):
	for year in product.years():

		y_prod = product.get_year(year)

		for s in strat:
			s.scale = 1.
			trading_subsys = TradingSystem(
				product=y_prod,
				trading_rules=[s],
				forecast_weights=[1.],
			)

			tsar = trading_subsys.run()
			results.update({f"{product.name}.{year}": tsar.forecast_series})

mean = []
for key, result in results.items():
	result.apply(abs).apply(mean.append)

mean_ps = pd.Series(mean)
scale_f = 10/mean_ps.mean()
scaled_ps = (scale_f * mean_ps)

print(mean_ps.mean(), scale_f, scaled_ps.mean())

plt.hist(mean, bins=100)
plt.hist(scaled_ps.to_numpy(), bins=100, color="red", alpha=0.5)
plt.show()


