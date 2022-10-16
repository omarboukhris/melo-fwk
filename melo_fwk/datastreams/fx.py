
from melo_fwk.datastreams.backtest_data_loader import BacktestDataLoader

class FxDataLoader:

	EURUSD = BacktestDataLoader.get_fx_hloc_datastream("EURUSD")
