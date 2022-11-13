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
		"Brent Crude Oil": "BZ=F",
		"Coffee": "KC=F",
		"Cocoa": "CC=F",
		"Copper": "HG=F",
		"Corn": "ZC=F",
		"Cotton": "CT=F",
		"Crude Oil": "CL=F",
		"Feeder Cattle": "GF=F",
		"Gold": "GC=F",
		"XAUUSD": "Gold",
		"Lean Hogs": "HE=F",
		"Live Cattle": "LE=F",
		"Lumber": "LBS=F",
		"Natural Gas": "NG=F",
		"Oat": "ZO=F",
		"Palladium": "PA=F",
		"Platinum": "PL=F",
		"RBOB Gasoline": "RB=F",
		"Silver": "SI=F",
		"Soybean": "ZS=F",
		"Soybean Meal": "ZM=F",
		"Soybean Oil": "ZL=F",
		"Sugar": "SB=F",
		"Wheat": "ZW=F",
	}
	# resolution: period
	settings = {
		"1d": "100y",
		"1h": "2y",
		"5m": "1mo",
	}

	resolution = "1d"

	for name, yf_symbol in tqdm.tqdm(comm_list.items()):
		export_comm = f"Commodity/{name}"
		download_and_store(
			yf_symbol,
			export_comm,
			settings[resolution],
			resolution
		)
