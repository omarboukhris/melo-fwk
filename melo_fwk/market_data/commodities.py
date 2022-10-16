
from melo_fwk.market_data.utils.market_data_loader import MarketDataLoader

class CommodityDataLoader:

	# oil
	BrentCrudeOil = MarketDataLoader.get_sanitized_commodity_hloc_datastream("Brent Crude Oil")
	CrudeOil = MarketDataLoader.get_sanitized_commodity_hloc_datastream("Crude Oil")
	HeatingOil = MarketDataLoader.get_sanitized_commodity_hloc_datastream("Heating Oil")
	NaturalGas = MarketDataLoader.get_sanitized_commodity_hloc_datastream("Natural Gas")
	RBOBGasoline = MarketDataLoader.get_sanitized_commodity_hloc_datastream("RBOB Gasoline")

	# agricultural
	# plants
	Cocoa = MarketDataLoader.get_sanitized_commodity_hloc_datastream("Cocoa")
	Coffee = MarketDataLoader.get_sanitized_commodity_hloc_datastream("Coffee")
	Corn = MarketDataLoader.get_sanitized_commodity_hloc_datastream("Copper")
	Cotton = MarketDataLoader.get_sanitized_commodity_hloc_datastream("Copper")
	Soybean = MarketDataLoader.get_sanitized_commodity_hloc_datastream("Soybean")
	SoybeanMeal = MarketDataLoader.get_sanitized_commodity_hloc_datastream("Soybean Meal")
	SoybeanOil = MarketDataLoader.get_sanitized_commodity_hloc_datastream("Soybean Oil")
	Sugar = MarketDataLoader.get_sanitized_commodity_hloc_datastream("Sugar")
	Wheat = MarketDataLoader.get_sanitized_commodity_hloc_datastream("Wheat")
	# animals
	FeederCattla = MarketDataLoader.get_sanitized_commodity_hloc_datastream("Feeder Cattle")
	LiveCattle = MarketDataLoader.get_sanitized_commodity_hloc_datastream("Live Cattle")

	# metals
	Copper = MarketDataLoader.get_sanitized_commodity_hloc_datastream("Copper")
	Gold = MarketDataLoader.get_sanitized_commodity_hloc_datastream("Gold")
	Palladium = MarketDataLoader.get_sanitized_commodity_hloc_datastream("Palladium")
	Platinum = MarketDataLoader.get_sanitized_commodity_hloc_datastream("Platinum")
	Silver = MarketDataLoader.get_sanitized_commodity_hloc_datastream("Silver")

	# unclassified
	LeanHogs = MarketDataLoader.get_sanitized_commodity_hloc_datastream("Lean Hogs")
	Lumber = MarketDataLoader.get_sanitized_commodity_hloc_datastream("Lumber")
	Oat = MarketDataLoader.get_sanitized_commodity_hloc_datastream("Oat")


