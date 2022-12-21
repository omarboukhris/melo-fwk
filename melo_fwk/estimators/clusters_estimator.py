
import tqdm

from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.datastreams import HLOCDataStream
from melo_fwk.estimators.base_estimator import MeloBaseEstimator
from melo_fwk.estimators.utils.cluster import ClusterUtils
from melo_fwk.trading_systems import TradingSystem
from melo_fwk.market_data.product import Product


class ClustersEstimator(MeloBaseEstimator):

	def __init__(self, **kwargs):
		super(ClustersEstimator, self).__init__(**kwargs)
		self.sampling_ratio = self.next_float_param(0.7)
		self.logger.info("Estimator Initialized")

	def run(self):
		self.logger.info(f"Fetching {len(self.products)} Products returns")

		results = self.get_rolling_results()

		# check sizes
		# flag = pd.Series([len(v) for v in results.values()]).diff().sum() != 0
		# run diagnosis if flag is true
		# search for maximum sampling period
		# or kick out outlier

		# sample to compute correlation after notifying potential missing data
		self.logger.info("Computing correlations")
		raw_avg_corr, correlations = ClusterUtils.get_corr_sample(results, self.sampling_ratio)

		self.logger.info("Clustering Heatmap")
		avg_corr = ClusterUtils.cluster_products(raw_avg_corr)

		self.logger.info("Building correlations Histogram")
		corr_hist = ClusterUtils.build_corr_hist(correlations)

		self.logger.info("Finished building Heatmap")
		return avg_corr, corr_hist

	def get_rolling_results(self):
		results = {}
		years = [year for year in range(self.begin, self.end)]
		for product_name, product in tqdm.tqdm(self.products.items(), leave=False):
			rolling_dataframe = product.rolling_dataframe(years)
			results[product_name] = []
			for subset_prod_df in tqdm.tqdm(rolling_dataframe, leave=False):
				trading_subsys = TradingSystem(
					trading_rules=self.strategies,
					forecast_weights=self.forecast_weights,
					size_policy=self.size_policy
				)

				y_return = trading_subsys.run_product(Product(
					name=product.name,
					block_size=product.block_size,
					cap=product.cap,
					datastream=HLOCDataStream(dataframe=subset_prod_df)
				))
				results[product_name].append(y_return)
		return results
