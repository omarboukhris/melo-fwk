from melo_fwk.utils import quantflow_factory

# Assets
from melo_fwk.market_data.commodities import CommodityDataLoader
from melo_fwk.market_data.fx import FxDataLoader

# Estimators
from melo_fwk.melo_estimators.backtest_estimator import BacktestEstimator
from melo_fwk.melo_estimators.strat_optim_estimator import StratOptimEstimator
from melo_fwk.melo_estimators.fw_optim_estimator import ForecastWeightsEstimator
from melo_fwk.melo_estimators.vol_target_estimator import VolTargetEstimator

# Reporters
from melo_fwk.reporters.backtest_reporter import BacktestReporter

# Strategies
from melo_fwk.strategies import ewma, sma

# Position Sizing
from melo_fwk.position_size_policies import (
	BaseSizePolicy,
	VolTargetSizePolicy,
	VolTargetInertiaPolicy,
	VolTargetDiscreteSizePolicy
)


def register_all():
	register_estimator()
	register_strats()
	register_search_spaces()
	register_size_policies()
	register_products()

def register_estimator():
	quantflow_factory.QuantFlowFactory.register_estimator("BacktestEstimator", BacktestEstimator)
	quantflow_factory.QuantFlowFactory.register_reporter("BacktestEstimator", BacktestReporter)

	quantflow_factory.QuantFlowFactory.register_estimator("StratOptimEstimator", StratOptimEstimator)

	quantflow_factory.QuantFlowFactory.register_estimator("ForecastWeightsEstimator", ForecastWeightsEstimator)

	quantflow_factory.QuantFlowFactory.register_estimator("VolTargetEstimator", VolTargetEstimator)

def register_strats():
	quantflow_factory.QuantFlowFactory.register_strategy("ewma", ewma.EWMAStrategy)
	quantflow_factory.QuantFlowFactory.register_strategy("sma", sma.SMAStrategy)

def register_search_spaces():
	quantflow_factory.QuantFlowFactory.register_search_space("ewma.search_space", ewma.EWMAStrategy.search_space)
	quantflow_factory.QuantFlowFactory.register_search_space("sma.search_space", sma.SMAStrategy.search_space)

def register_size_policies():
	quantflow_factory.QuantFlowFactory.register_size_policy("default", BaseSizePolicy)
	quantflow_factory.QuantFlowFactory.register_size_policy("VolTargetSizePolicy", VolTargetSizePolicy)
	quantflow_factory.QuantFlowFactory.register_size_policy("VolTargetInertiaPolicy", VolTargetInertiaPolicy)
	quantflow_factory.QuantFlowFactory.register_size_policy("VolTargetDiscreteSizePolicy", VolTargetDiscreteSizePolicy)

def register_products():
	# =============================================================
	# Products Factory Registration
	# =============================================================
	# Commodities
	# -------------------------------------------------------------
	for prod_name in CommodityDataLoader.get_product_pool():
		quantflow_factory.QuantFlowFactory.register_product(
			f"Commodities.{prod_name}",
			CommodityDataLoader.get_product_by_name(prod_name)
		)

	# -------------------------------------------------------------
	# Fx
	# -------------------------------------------------------------
	for prod_name in FxDataLoader.get_product_pool():
		quantflow_factory.QuantFlowFactory.register_product(
			f"Fx.{prod_name}",
			FxDataLoader.get_product_by_name(prod_name)
		)

