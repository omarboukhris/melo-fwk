
import yfinance as yf


def download_and_store(stcks, fnames):
	for stock, fn in zip(stcks, fnames):
		tick = yf.Ticker(stock)

		df = tick.history(period="10y", interval="1d")
		df.to_csv(f"{fn}.csv")

		print(tick.history().columns)
		print(df)


if __name__ == "__main__":

	stocks = ["AAPL", "GOOG", "BTC-EUR", "ETH-EUR"]
	filenames = ["data/AAPL", "data/GOOG", "data/BTCEUR", "data/ETHEUR"]

	download_and_store(stocks, filenames)
