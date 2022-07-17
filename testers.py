
import pandas as pd
import tqdm
from melo_tf.rules import EWMATradingRule, SMATradingRule
from melo_tf.process import trading_system as ts
from melo_tf.helpers import AccountPlotter, PricePlotter
from melo_tf.datastreams import datastream as ds

def test_empty_trading_system():
	df = pd.read_csv("melo_tf/data/Commodity Data/Cocoa_sanitized.csv")

	pds = ds.PandasDataStream(name="test_empty_tsys", dataframe=df)

	tr_sys = ts.TradingSystem(
		balance=10000,
		data_source=pds,
		trading_rules=[],
		forecast_weights=[]
	)

	while not tr_sys.simulation_ended():
		tr_sys.trade_next()

	assert tr_sys.simulation_ended(), "(AssertionError) Simulation not ended"


def test_datastream():
	def process_tick(_):
		pass

	pdstream = ds.PandasDataStream(
		name="FB_test",
		dataframe=pd.read_csv("melo_tf/data/Commodity Data/Cocoa_sanitized.csv"))

	for tick in pdstream:
		process_tick(tick)

def test_trading_rule():
	df = pd.read_csv("melo_tf/data/Commodity Data/Cocoa_sanitized.csv")
	pds = ds.PandasDataStream(name="test_trule", dataframe=df)

	ewma_params = {
		"fast_span": 4,
		"slow_span": 8,
		"scaling_factor": 20,
		"cap": 20,
	}
	ewma = EWMATradingRule("ewma", ewma_params)

	output_forcast = []
	for _ in pds:
		window = pds.get_window()
		if window is not None:
			output_forcast.append({
				"Balance": ewma.forecast(window),
				"Date": pds.get_current_date(),
			})

	forcast_df = pd.DataFrame(output_forcast)
	acc_plt = AccountPlotter(forcast_df)
	acc_plt.plot()
	acc_plt.save_png("test_results/test_trading_rule__forecast_plot")
	# acc_plt.show()

	price_plt = PricePlotter(df)
	price_plt.plot()
	price_plt.save_png("test_results/test_trading_rule__price_plot")
	# price_plt.show()


def test_trading_system():
	"""
	2y 1h :
		goog : 8 32
		googl : 2 8
		meta : 4 16    # mid trends
		aapl : 16 64   # long trends


	:return:
	"""

	# df = pd.read_csv("melo_tf/data/Commodity Data/Gold_sanitized.csv")
	df = pd.read_csv("melo_tf/data/Stocks/ETHEUR_1d_10y.csv")
	pds = ds.PandasDataStream(name="test_tr_sys", dataframe=df, offset=1)

	sma_params = {
		"fast_span": 4,
		"slow_span": 16,
		"scaling_factor": 20,
		"cap": 20,
	}
	sma = EWMATradingRule("sma", sma_params)

	tr_sys = ts.TradingSystem(
		balance=0,
		data_source=pds,
		trading_rules=[sma],
		forecast_weights=[1.]
	)
	tr_sys.run()

	# print(tr_sys.sharpe_ratio())
	orderbook = tr_sys.get_order_book()

	df_account = tr_sys.get_account_history()
	account_plt = AccountPlotter(df_account)
	account_plt.plot()
	account_plt.add_vlines(orderbook)
	account_plt.show()
	# account_plt.save_png("1")

	# price_plt = PricePlotter(pds.get_data())
	# price_plt.plot()
	# price_plt.show()
	# price_plt.save_png("2")

	df_account.to_csv("test_results/account.csv")
	orderbook.to_csv("test_results/book.csv")



if __name__ == "__main__":
	tests = [
		test_datastream,
		test_trading_rule,
		test_empty_trading_system,
		test_trading_system,
	]

	for t in tqdm.tqdm(tests):
		t()
