
import yfinance as yf


if __name__ == "__main__":

	stocks = ["AAPL", "GOOG", "BTC-EUR", "ETH-EUR"]
	filenames = ["data/AAPL", "data/GOOG", "data/BTCEUR", "data/ETHEUR"]

	for stock, fn in zip(stocks, filenames):
		tick = yf.Ticker(stock)

		df = tick.history(period="10y", interval="1d")
		df.to_csv(f"{fn}.csv")

		print(tick.history().columns)
		print(df)
