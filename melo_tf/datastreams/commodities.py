
from backtest_data_loader import BacktestDataLoader

class CommodityDataLoader:

	# oil
	BrentCrudeOil = BacktestDataLoader.get_sanitized_commodity_hloc_datastream("Brent Crude Oil")
	CrudeOil = BacktestDataLoader.get_sanitized_commodity_hloc_datastream("Crude Oil")
	HeatingOil = BacktestDataLoader.get_sanitized_commodity_hloc_datastream("Heating Oil")
	NaturalGas = BacktestDataLoader.get_sanitized_commodity_hloc_datastream("Natural Gas")
	RBOBGasoline = BacktestDataLoader.get_sanitized_commodity_hloc_datastream("RBOB Gasoline")

	# agricultural
	# plants
	Cocoa = BacktestDataLoader.get_sanitized_commodity_hloc_datastream("Cocoa")
	Coffee = BacktestDataLoader.get_sanitized_commodity_hloc_datastream("Coffee")
	Corn = BacktestDataLoader.get_sanitized_commodity_hloc_datastream("Copper")
	Cotton = BacktestDataLoader.get_sanitized_commodity_hloc_datastream("Copper")
	Soybean = BacktestDataLoader.get_sanitized_commodity_hloc_datastream("Soybean")
	SoybeanMeal = BacktestDataLoader.get_sanitized_commodity_hloc_datastream("Soybean Meal")
	SoybeanOil = BacktestDataLoader.get_sanitized_commodity_hloc_datastream("Soybean Oil")
	Sugar = BacktestDataLoader.get_sanitized_commodity_hloc_datastream("Sugar")
	Wheat = BacktestDataLoader.get_sanitized_commodity_hloc_datastream("Wheat")
	# animals
	FeederCattla = BacktestDataLoader.get_sanitized_commodity_hloc_datastream("Feeder Cattle")
	LiveCattle = BacktestDataLoader.get_sanitized_commodity_hloc_datastream("Live Cattle")

	# metals
	Copper = BacktestDataLoader.get_sanitized_commodity_hloc_datastream("Copper")
	Gold = BacktestDataLoader.get_sanitized_commodity_hloc_datastream("Gold")
	Palladium = BacktestDataLoader.get_sanitized_commodity_hloc_datastream("Palladium")
	Platinum = BacktestDataLoader.get_sanitized_commodity_hloc_datastream("Platinum")
	Silver = BacktestDataLoader.get_sanitized_commodity_hloc_datastream("Silver")

	# unclassified
	LeanHogs = BacktestDataLoader.get_sanitized_commodity_hloc_datastream("Lean Hogs")
	Lumber = BacktestDataLoader.get_sanitized_commodity_hloc_datastream("Lumber")
	Oat = BacktestDataLoader.get_sanitized_commodity_hloc_datastream("Oat")


