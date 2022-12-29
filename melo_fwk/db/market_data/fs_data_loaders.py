from melo_fwk.db.market_data.market_data_loader import MarketDataLoader


class FxDataLoader:

	def __init__(self):
		# "EURJPY",
		fx_products = [
			"EURUSD", "AUDUSD", "CADUSD", "CHFUSD", "EURCAD", "EURCHF", "EURGBP", "GBPUSD", "NZDUSD"]
		market_loader = MarketDataLoader()
		self.fx_data_registry = {}
		for fx in fx_products:
			self.fx_data_registry[fx] = market_loader.get_fx_product(fx)

class CommodityDataLoader:

	def __init__(self):
		commo_products = [
			# energy
			"RBOB Gasoline", "Brent Crude Oil", "Crude Oil", "Natural Gas",
			# metal
			"Palladium", "Platinum", "Silver", "Copper", "Gold",
			# agric animals
			"Lean Hogs", "Live Cattle",
			# agric vegetal
			"Coffee", "Corn", "Cotton", "Feeder Cattle", "Oat", "Lumber",
			"Soybean", "Soybean Meal", "Soybean Oil", "Sugar", "Wheat",
		]
		market_loader = MarketDataLoader()
		self.commo_data_registry = {}
		for commo in commo_products:
			self.commo_data_registry[commo] = market_loader.get_commodity_product(commo)
