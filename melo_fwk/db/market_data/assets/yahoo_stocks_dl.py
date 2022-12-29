
import yfinance as yf
import tqdm


def download_and_store(stock, filename, period, interval):
	tick = yf.Ticker(stock)

	df = tick.history(period=period, interval=interval)
	df.to_csv(f"{filename}.csv")

	# print(tick.history().columns)
	# print(df)


if __name__ == "__main__":


	comm_list = {
		"AAPL": "AAPL",
		"GOOG": "GOOG",
		"GOOGL": "GOOGL",
		"TSLA": "TSLA",
		"NFLX": "NFLX",
		"INTC": "INTC",
		"META": "META",
	}

	# resolution: period
	settings = {
		"1d": "100y",
		"1h": "2y",
		"5m": "1mo",
	}

	resolution = "1d"

	for name, yf_symbol in tqdm.tqdm(comm_list.items()):
		export_comm = f"Stocks/{name}"
		download_and_store(
			yf_symbol,
			export_comm,
			settings[resolution],
			resolution
		)
