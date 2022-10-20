
import datetime as dt
import pandas as pd

pd.options.mode.chained_assignment = None

def parse_year_from_date(dataframe: pd.DataFrame, date_label: str = "Date"):
	"""
	Add column "Year" to dataframe from parsing "Date" column (default)
	if DateTime is stored in another cell, you can specify the date label

	:param dataframe : DataFrame to parse date from
	:param date_label : Column label containing date as str
	:return list of years parsed from dates
	"""
	def parse_date(date: str):
		try:
			y = dt.datetime.strptime(date, "%Y-%m-%d").year
			parse_date.years.append(y)
			return y
		except ValueError:
			y = dt.datetime.strptime(date, "%Y-%m-%d %H:%M:%S%z").year
			parse_date.years.append(y)
			return y
		except Exception as e:
			print(f"HLOCDataStream can't parse date [{date}]")
			raise e
	parse_date.years = []

	dataframe["Year"] = dataframe[date_label].apply(parse_date)
	parse_date.years = list(set(parse_date.years))
	parse_date.years.sort()
	return parse_date.years

def get_daily_diff_from_value(dataframe: pd.DataFrame, price_label: str = "Close"):
	dataframe["Daily_diff"] = dataframe[price_label].diff().fillna(0)
	return dataframe
