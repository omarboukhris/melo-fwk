
from melo_fwk.market_data.market_data_loader import MarketDataLoader

class CommodityDataLoader:

	# oil
	BrentCrudeOil = MarketDataLoader.get_commodity_hloc_datastream("Brent Crude Oil")
	CrudeOil = MarketDataLoader.get_commodity_hloc_datastream("Crude Oil")
	NaturalGas = MarketDataLoader.get_commodity_hloc_datastream("Natural Gas")
	RBOBGasoline = MarketDataLoader.get_commodity_hloc_datastream("RBOB Gasoline")

	# agricultural
	# plants
	Cocoa = MarketDataLoader.get_commodity_hloc_datastream("Cocoa")
	Coffee = MarketDataLoader.get_commodity_hloc_datastream("Coffee")
	Corn = MarketDataLoader.get_commodity_hloc_datastream("Copper")
	Cotton = MarketDataLoader.get_commodity_hloc_datastream("Copper")
	Soybean = MarketDataLoader.get_commodity_hloc_datastream("Soybean")
	SoybeanMeal = MarketDataLoader.get_commodity_hloc_datastream("Soybean Meal")
	SoybeanOil = MarketDataLoader.get_commodity_hloc_datastream("Soybean Oil")
	Sugar = MarketDataLoader.get_commodity_hloc_datastream("Sugar")
	Wheat = MarketDataLoader.get_commodity_hloc_datastream("Wheat")
	# animals
	FeederCattla = MarketDataLoader.get_commodity_hloc_datastream("Feeder Cattle")
	LiveCattle = MarketDataLoader.get_commodity_hloc_datastream("Live Cattle")

	# metals
	Copper = MarketDataLoader.get_commodity_hloc_datastream("Copper")
	Gold = MarketDataLoader.get_commodity_hloc_datastream("Gold")
	Palladium = MarketDataLoader.get_commodity_hloc_datastream("Palladium")
	Platinum = MarketDataLoader.get_commodity_hloc_datastream("Platinum")
	Silver = MarketDataLoader.get_commodity_hloc_datastream("Silver")

	# unclassified
	LeanHogs = MarketDataLoader.get_commodity_hloc_datastream("Lean Hogs")
	Lumber = MarketDataLoader.get_commodity_hloc_datastream("Lumber")
	Oat = MarketDataLoader.get_commodity_hloc_datastream("Oat")

	@staticmethod
	def get_product_pool():
		return [str(x) for x in dir(CommodityDataLoader) if not x.startswith("__")]

	@staticmethod
	def get_product_by_name(name: str):
		assert name in dir(CommodityDataLoader), \
			f"(CommodityDataLoader) {name} not in CommodityDataLoader pool [{CommodityDataLoader.get_product_pool()}]"
		return getattr(CommodityDataLoader, name)

