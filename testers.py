
import pandas as pd
import tqdm
from core.rules import EWMATradingRule, SMATradingRule
from core.process import trading_system as ts
from core.helpers import AccountPlotter, PricePlotter
from core.datastreams import datastream as ds

def test_empty_trading_system():
	df = pd.read_csv("core/data/FB_1d_10y.csv")

	pds = ds.PandasDataStream(df)

	tr_sys = ts.TradingSystem(
		balance=10000,
		data_source=pds,
		trading_rules=[],
		forecast_weights=[]
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

	pdstream = ds.PandasDataStream(pd.read_csv("core/data/FB_1d_10y.csv"))

	for tick in pdstream:
		process_tick(tick)

def test_trading_rule():
	df = pd.read_csv("core/data/FB_1d_10y.csv")
	pds = ds.PandasDataStream(df)

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
	acc_plt.show()

	price_plt = PricePlotter(df)
	price_plt.plot()
	price_plt.show()


def test_trading_system():
	"""
	goog : 8 32
	googl : 2 8
	meta : 4 16
	aapl : 16 64


	:return:
	"""

	df = pd.read_csv("core/data/FB_1h_2y.csv")
	pds = ds.PandasDataStream(name="FB", dataframe=df, offset=1, date_label="Datetime")

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

	while not tr_sys.simulation_ended():
		tr_sys.trade_next()

	print(tr_sys.sharpe_ratio())

	df_account = tr_sys.get_account_history()
	account_plt = AccountPlotter(df_account)
	account_plt.plot()
	account_plt.show()

	orderbook = tr_sys.get_order_book()
	df_account.to_csv("account.csv")
	orderbook.to_csv("book.csv")



if __name__ == "__main__":
	tests = [
		# test_datastream,
		# test_trading_rule,
		# test_empty_trading_system,
		test_trading_system,
	]

	for t in tqdm.tqdm(tests):
		t()
