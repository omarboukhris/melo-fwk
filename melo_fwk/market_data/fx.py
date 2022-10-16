
from melo_fwk.market_data.utils.market_data_loader import MarketDataLoader

class FxDataLoader:

	EURUSD = MarketDataLoader.get_fx_hloc_datastream("EURUSD")
