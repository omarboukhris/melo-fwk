
import yfinance as yf


def download_and_store(stock, filename, period, interval):
	tick = yf.Ticker(stock)

	df = tick.history(period=period, interval=interval)
	df.to_csv(f"{filename}_{interval}_{period}.csv")

	print(tick.history().columns)
	print(df)


if __name__ == "__main__":

	stocks = ["AAPL", "GOOG", "BTC-EUR", "ETH-EUR", "EURUSD=X", "FB"]
	filenames = ["data/AAPL", "data/GOOG", "data/BTCEUR", "data/ETHEUR", "data/EURUSD", "data/FB"]
	settings = [
		{
			"period": "10y",
			"interval": "1d",
		},
		{
			"period": "2y",
			"interval": "1h",
		},
		{
			"period": "1mo",
			"interval": "5m",
		},
	]

	idx, ext_id = 5, 2

	download_and_store(
		stocks[idx],
		filenames[idx],
		settings[ext_id]["period"],
		settings[ext_id]["interval"]
	)
