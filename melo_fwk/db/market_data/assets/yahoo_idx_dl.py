import tqdm
import yfinance as yf


def download_and_store(inst, filename, period, interval):
	tick = yf.Ticker(inst)

	df = tick.history(period=period, interval=interval)
	df.to_csv(f"{filename}.csv")

	# print(tick.history().columns)
	# print(df)


if __name__ == "__main__":


	comm_list = {
		"CAC40": "^FCHI",
		"ESTX50": "^STOXX50E",
		"DAX": "^GDAXI",
		"FTSE": "^FTSE",
		"NIKKEI225": "^N225",
		"HANGSENG": "^HSI",
		"DAWJONES": "^DJI",
		"SP500": "^GSPC",
		"NASDAQ": "^IXIC",
	}

	# resolution: period
	settings = {
		"1d": "100y",
		"1h": "2y",
		"5m": "1mo",
	}

	resolution = "1d"

	for name, yf_symbol in tqdm.tqdm(comm_list.items()):
		export_comm = f"Idx/{name}"
		download_and_store(
			yf_symbol,
			export_comm,
			settings[resolution],
			resolution
		)
