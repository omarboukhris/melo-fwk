import tqdm
import yfinance as yf


def download_and_store(inst, filename, period, interval):
	tick = yf.Ticker(inst)

	df = tick.history(period=period, interval=interval)
	df.to_csv(f"{filename}.csv")

	print(tick.history().columns)
	print(df)


if __name__ == "__main__":

	fx_list = [
		"EURUSD",
		"EURGBP",
		"EURCHF",
		"EURCAD",
		"EURJPY",
		"GBPUSD",
		"AUDUSD",
		"NZDUSD",
		"CHF",  # CHFUSD
		"CAD",  # CADUSD
	]

	# resolution: period
	settings = {
		"1d": "20y",
		"1h": "2y",
		"5m": "1mo",
	}

	resolution = "1d"

	for fx in tqdm.tqdm(fx_list):
		fx_name = f"{fx}=X"
		export_fx = f"Fx/{fx}" if len(fx) > 3 else f"Fx/{fx}USD"
		download_and_store(
			fx_name,
			export_fx,
			settings[resolution],
			resolution
		)
