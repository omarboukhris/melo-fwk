
import scipy.optimize as opt
import numpy as np

class ForecastWeightsEstimator:
	"""
	Should contain any attribute needed by trading sub sys to run:
	product
	strategies[] (+ stratconfig[] from strat build from config - mql)
	sizepolicy: default

	trading_subsys = (product, strategies[], sizepolicy)
	Note: Could be a Trading subsys decorator
	"""

	def run(self, weights, metric):
		"""
		Run trading sub sytem with weights as forecast weights
		Return the metric we want to optimize (sharpe, sortino, PnL ...)

		:param weights: forecast weights
		:param metric: metric to optimize
		:return: Trading SubSys's annual result
		"""
		pass


if __name__ == "__main__":
	n = 420  # len (Strategies from conf)
	forecast_weights_estimator = ForecastWeightsEstimator()

	w = np.array([1/n for _ in range(n)])
	opt.minimize(forecast_weights_estimator.run, w)

