import numpy as np
from scipy.optimize import minimize, Bounds


class WeightsOptim:
	divMultiplier: float = 2.

	@staticmethod
	def objective(W, exp_ret, covmat):
		return -(W.T @ exp_ret) * ((W.T @ covmat @ W) ** -0.5)


	@staticmethod
	def get_div_mult(corrmat_ret, opt_result):
		opt_params = np.array(opt_result.x)
		corrmat_ret[corrmat_ret < 0] = 0.
		raw_div_mult = (opt_params.T @ corrmat_ret @ opt_params) ** -0.5
		div_mult = min(WeightsOptim.divMultiplier, raw_div_mult)
		return div_mult


	@staticmethod
	def optimize_weights(mean_returns, returns, weights):
		opt_bounds = Bounds(0., 1.)
		opt_cst = {'type': 'eq', 'fun': lambda W: 1.0 - np.sum(W)}

		opt_result = minimize(
			WeightsOptim.objective,
			np.array(weights),
			args=(mean_returns, returns.cov()),
			method='SLSQP',
			bounds=opt_bounds,
			constraints=opt_cst,
			tol=1e-5
		)
		div_mult = WeightsOptim.get_div_mult(returns.corr(), opt_result)
		return opt_result, div_mult
