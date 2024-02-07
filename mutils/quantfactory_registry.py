from mestimators.var_estimator import VaREstimator
from mestimators.pf_allocation_estimator import PFAllocationEstimator
from melo_fwk.market_data.market_data_loader import MarketDataLoader
from melo_fwk.market_data.market_data_mongo_loader import MarketDataMongoLoader
from melo_fwk.pfio.portfolio_db_mgr import PortfolioMongoManager
from melo_fwk.pfio.portfolio_fs_mgr import PortfolioFsManager
from mreport.pf_alloc_reporter import PFAllocationReporter
from mreport.var_reporter import VaRReporter
from mutils.quantflow_factory import QuantFlowFactory

from mestimators import (
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

from mreport.backtest_reporter import BacktestReporter
from mreport.fw_optim_reporter import ForecastWeightsReporter
from mreport.strat_optim_reporter import StratOptimReporter
from mreport.vol_target_reporter import VolTargetReporter
from mreport.clusters_reporter import ClustersReporter

from mutils.loggers.global_logger import GlobalLogger

class QuantFlowRegistry:
	pf_loaders = {
		PortfolioFsManager.__name__: PortfolioFsManager,
		PortfolioMongoManager.__name__: PortfolioMongoManager,
	}
	market_providers = {
		MarketDataLoader.__name__: MarketDataLoader,
		MarketDataMongoLoader.__name__: MarketDataMongoLoader,
	}
	products = dict()
	strategies = {
		"ewma": EWMAStrategy,
		"sma": SMAStrategy,

		BuyAndHold.__name__: BuyAndHold,
		EWMAStrategy.__name__: EWMAStrategy,
		SMAStrategy.__name__: SMAStrategy,
	}
	strat_configs = dict()
	search_spaces = {
		"ewma": EWMAStrategy,
		"sma": SMAStrategy
	}
	estimators = {
		BacktestEstimator.__name__: BacktestEstimator,
		ClustersEstimator.__name__: ClustersEstimator,
		StratOptimEstimator.__name__: StratOptimEstimator,
		ForecastWeightsEstimator.__name__: ForecastWeightsEstimator,
		VolTargetEstimator.__name__: VolTargetEstimator,
		VaREstimator.__name__: VaREstimator,

		PFAllocationEstimator.__name__: PFAllocationEstimator,
	}
	reporters = {
		BacktestEstimator.__name__: BacktestReporter,
		ClustersEstimator.__name__: ClustersReporter,
		StratOptimEstimator.__name__: StratOptimReporter,
		ForecastWeightsEstimator.__name__: ForecastWeightsReporter,
		VolTargetEstimator.__name__: VolTargetReporter,
		VaREstimator.__name__: VaRReporter,

		PFAllocationEstimator.__name__: PFAllocationReporter,
	}

	size_policies = {
		"default": BaseSizePolicy,
		VolTargetSizePolicy.__name__: VolTargetSizePolicy,
		VolTargetInertiaPolicy.__name__: VolTargetInertiaPolicy,
		VolTargetDiscreteSizePolicy.__name__: VolTargetDiscreteSizePolicy,
	}

	@staticmethod
	def register_all():
		log = GlobalLogger.build_composite_for(QuantFlowRegistry.__name__)
		log.info("Registring Estimators...")
		any(QuantFlowFactory.register_estimator(label, estim) for label, estim in QuantFlowRegistry.estimators.items())
		any(QuantFlowFactory.register_reporter(label, reporter) for label, reporter in QuantFlowRegistry.reporters.items())
		log.info("Registring Strategies...")
		any(QuantFlowFactory.register_strategy(label, strat) for label, strat in QuantFlowRegistry.strategies.items())
		log.info("Registring Strategies Search Spaces...")
		any(QuantFlowFactory.register_search_space(label, strat_space) for label, strat_space in QuantFlowRegistry.search_spaces.items())
		log.info("Registring Size Policies...")
		any(QuantFlowFactory.register_size_policy(label, size) for label, size in QuantFlowRegistry.size_policies.items())
		log.info("Registring PF Loaders...")
		any(QuantFlowFactory.register_pf_loader(label, pf_loader) for label, pf_loader in QuantFlowRegistry.pf_loaders.items())
		log.info("Registring Market Providers Components...")
		any(QuantFlowFactory.register_market(label, market) for label, market in QuantFlowRegistry.market_providers.items())
		log.info("Registring Products/Assets historical data...")
		QuantFlowFactory.load_products_factory_map()
