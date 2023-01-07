from melo_fwk.estimators.var_estimator import VaREstimator
from melo_fwk.reporters.var_reporter import VaRReporter
from melo_fwk.utils import quantflow_factory

from melo_fwk.market_data.fs_data_loaders import (
	CommodityDataLoader,
	FxDataLoader
)
from melo_fwk.estimators import (
	ClustersEstimator,
	BacktestEstimator,
	StratOptimEstimator,
	ForecastWeightsEstimator,
	VolTargetEstimator,
)
from melo_fwk.strategies import (
	EWMAStrategy,
	SMAStrategy,
	BuyAndHold,
)

from melo_fwk.pose_size import (
	BaseSizePolicy,
	VolTargetSizePolicy,
	VolTargetInertiaPolicy,
	VolTargetDiscreteSizePolicy
)

from melo_fwk.reporters.backtest_reporter import BacktestReporter
from melo_fwk.reporters.fw_optim_reporter import ForecastWeightsReporter
from melo_fwk.reporters.strat_optim_reporter import StratOptimReporter
from melo_fwk.reporters.vol_target_reporter import VolTargetReporter
from melo_fwk.reporters.clusters_reporter import ClustersReporter

from melo_fwk.loggers.global_logger import GlobalLogger

def register_all():
	log = GlobalLogger.build_composite_for("QuantFactoryRegistry")
	log.info("Registring Estimators...")
	register_estimator()
	log.info("Registring Strategies...")
	register_strats()
	log.info("Registring Strategies Search Spaces...")
	register_search_spaces()
	log.info("Registring Size Policies...")
	register_size_policies()
	log.info("Registring Products/Assets historical data...")
	register_products()

def register_estimator():
	quantflow_factory.QuantFlowFactory.register_estimator("BacktestEstimator", BacktestEstimator)
	quantflow_factory.QuantFlowFactory.register_estimator("ClustersEstimator", ClustersEstimator)
	quantflow_factory.QuantFlowFactory.register_estimator("StratOptimEstimator", StratOptimEstimator)
	quantflow_factory.QuantFlowFactory.register_estimator("ForecastWeightsEstimator", ForecastWeightsEstimator)
	quantflow_factory.QuantFlowFactory.register_estimator("VolTargetEstimator", VolTargetEstimator)
	quantflow_factory.QuantFlowFactory.register_estimator("VaREstimator", VaREstimator)

	quantflow_factory.QuantFlowFactory.register_reporter("BacktestEstimator", BacktestReporter)
	quantflow_factory.QuantFlowFactory.register_reporter("ClustersEstimator", ClustersReporter)
	quantflow_factory.QuantFlowFactory.register_reporter("StratOptimEstimator", StratOptimReporter)
	quantflow_factory.QuantFlowFactory.register_reporter("ForecastWeightsEstimator", ForecastWeightsReporter)
	quantflow_factory.QuantFlowFactory.register_reporter("VolTargetEstimator", VolTargetReporter)
	quantflow_factory.QuantFlowFactory.register_reporter("VaREstimator", VaRReporter)

def register_strats():
	quantflow_factory.QuantFlowFactory.register_strategy("ewma", EWMAStrategy)
	quantflow_factory.QuantFlowFactory.register_strategy("sma", SMAStrategy)

	quantflow_factory.QuantFlowFactory.register_strategy(BuyAndHold.__name__, BuyAndHold)
	quantflow_factory.QuantFlowFactory.register_strategy(EWMAStrategy.__name__, EWMAStrategy)
	quantflow_factory.QuantFlowFactory.register_strategy(SMAStrategy.__name__, SMAStrategy)


def register_search_spaces():
	quantflow_factory.QuantFlowFactory.register_search_space("ewma.search_space", EWMAStrategy.search_space)
	quantflow_factory.QuantFlowFactory.register_search_space("sma.search_space", SMAStrategy.search_space)

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
	commo_loader = CommodityDataLoader()
	for prod_name, prod_hloc in commo_loader.commo_data_registry.items():
		quantflow_factory.QuantFlowFactory.register_product(
			f"Commodities.{prod_name}", prod_hloc
		)

	# -------------------------------------------------------------
	# Fx
	# -------------------------------------------------------------
	fx_loader = FxDataLoader()
	for prod_name, prod_hloc in fx_loader.fx_data_registry.items():
		quantflow_factory.QuantFlowFactory.register_product(
			f"Fx.{prod_name}", prod_hloc
		)

