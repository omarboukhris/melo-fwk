from melo_fwk.estimators.var_estimator import VaREstimator
from melo_fwk.estimators.pf_allocation_estimator import PFAllocationEstimator
from melo_fwk.market_data.market_data_loader import MarketDataLoader
from melo_fwk.market_data.market_data_mongo_loader import MarketDataMongoLoader
from melo_fwk.portfolio.portfolio_db_mgr import PortfolioMongoManager
from melo_fwk.portfolio.portfolio_fs_mgr import PortfolioFsManager
from melo_fwk.reporters.pf_alloc_reporter import PFAllocationReporter
from melo_fwk.reporters.var_reporter import VaRReporter
from melo_fwk.utils.quantflow_factory import QuantFlowFactory

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
	log.info("Registring PF Loaders...")
	register_pf_loaders()
	log.info("Registring Market Priveders Components...")
	register_markets()
	log.info("Registring Products/Assets historical data...")
	register_products()

def register_estimator():
	QuantFlowFactory.register_estimator("BacktestEstimator", BacktestEstimator)
	QuantFlowFactory.register_estimator("ClustersEstimator", ClustersEstimator)
	QuantFlowFactory.register_estimator("StratOptimEstimator", StratOptimEstimator)
	QuantFlowFactory.register_estimator("ForecastWeightsEstimator", ForecastWeightsEstimator)
	QuantFlowFactory.register_estimator("VolTargetEstimator", VolTargetEstimator)
	QuantFlowFactory.register_estimator("VaREstimator", VaREstimator)

	QuantFlowFactory.register_reporter("BacktestEstimator", BacktestReporter)
	QuantFlowFactory.register_reporter("ClustersEstimator", ClustersReporter)
	QuantFlowFactory.register_reporter("StratOptimEstimator", StratOptimReporter)
	QuantFlowFactory.register_reporter("ForecastWeightsEstimator", ForecastWeightsReporter)
	QuantFlowFactory.register_reporter("VolTargetEstimator", VolTargetReporter)
	QuantFlowFactory.register_reporter("VaREstimator", VaRReporter)
	QuantFlowFactory.register_estimator("PFAllocationEstimator", PFAllocationEstimator)

	QuantFlowFactory.register_reporter("PFAllocationEstimator", PFAllocationReporter)


def register_strats():
	QuantFlowFactory.register_strategy("ewma", EWMAStrategy)
	QuantFlowFactory.register_strategy("sma", SMAStrategy)

	QuantFlowFactory.register_strategy(BuyAndHold.__name__, BuyAndHold)
	QuantFlowFactory.register_strategy(EWMAStrategy.__name__, EWMAStrategy)
	QuantFlowFactory.register_strategy(SMAStrategy.__name__, SMAStrategy)


def register_search_spaces():
	QuantFlowFactory.register_search_space("ewma.search_space", EWMAStrategy.search_space)
	QuantFlowFactory.register_search_space("sma.search_space", SMAStrategy.search_space)

def register_size_policies():
	QuantFlowFactory.register_size_policy("default", BaseSizePolicy)
	QuantFlowFactory.register_size_policy("VolTargetSizePolicy", VolTargetSizePolicy)
	QuantFlowFactory.register_size_policy("VolTargetInertiaPolicy", VolTargetInertiaPolicy)
	QuantFlowFactory.register_size_policy("VolTargetDiscreteSizePolicy", VolTargetDiscreteSizePolicy)

def register_markets():
	QuantFlowFactory.register_market("MarketDataLoader", MarketDataLoader)
	QuantFlowFactory.register_market("MarketDataMongoLoader", MarketDataMongoLoader)

def register_pf_loaders():
	QuantFlowFactory.register_pf_loader("PortfolioFsManager", PortfolioFsManager)
	QuantFlowFactory.register_pf_loader("PortfolioMongoManager", PortfolioMongoManager)

def register_products():
	# =============================================================
	# Products Factory Registration
	# =============================================================
	# Commodities
	# -------------------------------------------------------------
	commo_loader = CommodityDataLoader()
	for prod_name, prod_hloc in commo_loader.commo_data_registry.items():
		QuantFlowFactory.register_product(
			f"Commodities.{prod_name}", prod_hloc
		)

	# -------------------------------------------------------------
	# Fx
	# -------------------------------------------------------------
	fx_loader = FxDataLoader()
	for prod_name, prod_hloc in fx_loader.fx_data_registry.items():
		QuantFlowFactory.register_product(
			f"Fx.{prod_name}", prod_hloc
		)

