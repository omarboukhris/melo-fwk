
from melo_fwk.market_data.utils.market_data_loader import MarketDataLoader

class FxDataLoader:

	EURUSD = MarketDataLoader.get_fx_hloc_datastream("EURUSD")
	AUDUSD = MarketDataLoader.get_fx_hloc_datastream("AUDUSD")
	CADUSD = MarketDataLoader.get_fx_hloc_datastream("CADUSD")
	CHFUSD = MarketDataLoader.get_fx_hloc_datastream("CHFUSD")
	EURCAD = MarketDataLoader.get_fx_hloc_datastream("EURCAD")
	EURCHF = MarketDataLoader.get_fx_hloc_datastream("EURCHF")
	EURGBP = MarketDataLoader.get_fx_hloc_datastream("EURGBP")
	EURJPY = MarketDataLoader.get_fx_hloc_datastream("EURJPY")
	GBPUSD = MarketDataLoader.get_fx_hloc_datastream("GBPUSD")
	NZDUSD = MarketDataLoader.get_fx_hloc_datastream("NZDUSD")

	@staticmethod
	def get_product_pool():
		return [str(x) for x in dir(FxDataLoader) if not x.startswith("__")]

	@staticmethod
	def get_product_by_name(name: str):
		assert name in dir(FxDataLoader), \
			f"(FxDataLoader) {name} not in FxDataLoader pool [{FxDataLoader.get_product_pool()}]"
		return getattr(FxDataLoader, name)

