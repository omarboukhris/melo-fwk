from melo_fwk.utils import quantflow_factory

from melo_fwk.datastreams.commodities import CommodityDataLoader

from melo_fwk.estimators.backtest_estimator import BacktestEstimator
from melo_fwk.estimators.fw_optim_estimator import ForecastWeightsEstimator

from melo_fwk.rules import ewma_rule, sma_rule

from melo_fwk.policies import vol_target_policy

def register_all():
	register_estimator()
	register_strats()
	register_size_policies()
	register_products()

def register_estimator():
	quantflow_factory.QuantFlowFactory.register_workflow("BacktestEstimator", BacktestEstimator)
	quantflow_factory.QuantFlowFactory.register_workflow("ForecastWeightsEstimator", ForecastWeightsEstimator)

def register_strats():
	quantflow_factory.QuantFlowFactory.register_strategy("ewma", ewma_rule.EWMATradingRule)
	quantflow_factory.QuantFlowFactory.register_strategy("sma", sma_rule.SMATradingRule)


def register_size_policies():
	quantflow_factory.QuantFlowFactory.register_size_policy("VolTargetSizePolicy", vol_target_policy.VolTargetSizePolicy)
	quantflow_factory.QuantFlowFactory.register_size_policy("default", vol_target_policy.ConstSizePolicy)

def register_products():
	# =============================================================
	# Products Factory Registration
	# =============================================================
	# Commodities
	# -------------------------------------------------------------
	# oil
	quantflow_factory.QuantFlowFactory.register_product("Commodities.BrentCrudeOil", CommodityDataLoader.BrentCrudeOil)
	quantflow_factory.QuantFlowFactory.register_product("Commodities.CrudeOil", CommodityDataLoader.CrudeOil)
	quantflow_factory.QuantFlowFactory.register_product("Commodities.HeatingOil", CommodityDataLoader.HeatingOil)
	quantflow_factory.QuantFlowFactory.register_product("Commodities.NaturalGas", CommodityDataLoader.NaturalGas)
	quantflow_factory.QuantFlowFactory.register_product("Commodities.RBOBGasoline", CommodityDataLoader.RBOBGasoline)

	# agricultural
	# plants
	quantflow_factory.QuantFlowFactory.register_product("Commodities.Cocoa", CommodityDataLoader.Cocoa)
	quantflow_factory.QuantFlowFactory.register_product("Commodities.Coffee", CommodityDataLoader.Coffee)
	quantflow_factory.QuantFlowFactory.register_product("Commodities.Corn", CommodityDataLoader.Corn)
	quantflow_factory.QuantFlowFactory.register_product("Commodities.Cotton", CommodityDataLoader.Cotton)
	quantflow_factory.QuantFlowFactory.register_product("Commodities.Soybean", CommodityDataLoader.Soybean)
	quantflow_factory.QuantFlowFactory.register_product("Commodities.SoybeanMeal", CommodityDataLoader.SoybeanMeal)
	quantflow_factory.QuantFlowFactory.register_product("Commodities.SoybeanOil", CommodityDataLoader.SoybeanOil)
	quantflow_factory.QuantFlowFactory.register_product("Commodities.Sugar", CommodityDataLoader.Sugar)
	quantflow_factory.QuantFlowFactory.register_product("Commodities.Wheat", CommodityDataLoader.Wheat)

	# animals
	quantflow_factory.QuantFlowFactory.register_product("Commodities.FeederCattla", CommodityDataLoader.FeederCattla)
	quantflow_factory.QuantFlowFactory.register_product("Commodities.LiveCattle", CommodityDataLoader.LiveCattle)

	# metals
	quantflow_factory.QuantFlowFactory.register_product("Commodities.Copper", CommodityDataLoader.Copper)
	quantflow_factory.QuantFlowFactory.register_product("Commodities.Gold", CommodityDataLoader.Gold)
	quantflow_factory.QuantFlowFactory.register_product("Commodities.Palladium", CommodityDataLoader.Palladium)
	quantflow_factory.QuantFlowFactory.register_product("Commodities.Platinum", CommodityDataLoader.Platinum)
	quantflow_factory.QuantFlowFactory.register_product("Commodities.Silver", CommodityDataLoader.Silver)

	# unclassified
	quantflow_factory.QuantFlowFactory.register_product("Commodities.LeanHogs", CommodityDataLoader.LeanHogs)
	quantflow_factory.QuantFlowFactory.register_product("Commodities.Lumber", CommodityDataLoader.Lumber)
	quantflow_factory.QuantFlowFactory.register_product("Commodities.Oat", CommodityDataLoader.Oat)

	# =============================================================
