import os
from typing import List

import tqdm
import yfinance as yf
import json

def get_config(filename: str):
	with open(filename, "r") as fs:
		return json.load(fs)

class YahooFinIAC:

	def __init__(self, categories: List[str], resolution: str, lookback: str):
		self.categories = categories
		self.resolution = resolution
		self.lookback = lookback

	def run(self):
		product_map = {}
		for c in tqdm.tqdm(self.categories, leave=False):
			products = config[c]
			product_map[c] = []
			tqdm.tqdm.write(f"downloading category: {c}")
			if not os.path.exists(c):
				os.makedirs(c)

			for name, yf_symbol in tqdm.tqdm(products.items(), leave=False):
				product_map[c].append(name)
				tick = yf.Ticker(yf_symbol)
				df = tick.history(period=self.lookback, interval=self.resolution)
				df.to_csv(f"{c}/{name}.csv")
		print("Exporting products factory config")
		with open("products_factory_config.json", "w") as fs:
			json.dump(product_map, fs)


if __name__ == "__main__":

	config = get_config("products.json")

	ctgr = config["categories"]
	rsl = config["resolution"]
	lb = config["lookback"]

	y = YahooFinIAC(ctgr, rsl, lb)
	y.run()
