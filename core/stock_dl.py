
import yfinance as yf


def download_and_store(stcks, fnames):
	for stock, fn in zip(stcks, fnames):
		tick = yf.Ticker(stock)

		df = tick.history(period="1mo", interval="5m")
		df.to_csv(f"{fn}.csv")

		print(tick.history().columns)
		print(df)


if __name__ == "__main__":

	stocks = ["AAPL", "GOOG", "BTC-EUR", "ETH-EUR", "EURUSD=X"]
	filenames = ["data/AAPL", "data/GOOG", "data/BTCEUR", "data/ETHEUR", "data/EURUSD"]

	idx, ext_id = 4, 2
	ext = ["_1d_10y", "1h_2y", "5m_1mo"]

	download_and_store(
		[stocks[idx]],
		[filenames[idx] + ext[ext_id]]
	)
