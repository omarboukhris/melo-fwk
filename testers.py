
import pandas as pd
import tqdm
from core.rules import trade_rule as tr
from core.process import trading_system
from core.helpers import plots as plt
from core.datastreams import datastream as ds

def test_trading_system():
	df = pd.read_csv("data/FB_1d_10y.csv")

	pds = ds.PandasDataStream(df)

	tr_sys = trading_system.TradingSystem(
		balance=10000,
		data_source=pds,
		trading_rules=[],
		forcast_weights=[]
	)

	while not tr_sys.simulation_ended():
		tr_sys.trade_next()

	assert tr_sys.simulation_ended(), "(AssertionError) Simulation not ended"
	# print(tr_sys.get_account_history())
	# plotter = plt.AccountPlotter(tr_sys.get_account_history())
	# plotter.plot()

def test_datastream():
	def process_tick(_):
		pass

	pdstream = ds.PandasDataStream(pd.read_csv("data/FB_1d_10y.csv"))

	for tick in pdstream:
		process_tick(tick)


if __name__ == "__main__":
	tests = [
		test_datastream,
		test_trading_system,
	]

	for t in tqdm.tqdm(tests):
		t()
