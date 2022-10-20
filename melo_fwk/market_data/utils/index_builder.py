
from melo_fwk.datastreams.hloc_datastream import HLOCDataStream
from melo_fwk.market_data.utils.product import Product
import pandas as pd


class IndexBuilder:
	i: int = 0

	@staticmethod
	def rename_columns(products: dict):
		output_df = None
		for prod_name, product in products.items():
			close_price_vect = product.datastream.get_dataframe()[["Date", "Close"]]
			close_price_vect = close_price_vect.rename(columns={"Close": prod_name})
			output_df = close_price_vect if output_df is None else pd.merge(output_df, close_price_vect, on="Date")

		return output_df

	@staticmethod
	def build(products: dict):
		merged_df = IndexBuilder.rename_columns(products).dropna()
		merged_df["Close"] = merged_df[products.keys()].sum(axis=1)
		IndexBuilder.i += 1
		return {
			"|".join(products.keys()): Product(
				name=f"idx.{IndexBuilder.i}",
				datastream=HLOCDataStream(dataframe=merged_df[["Date", "Close"]])
			)
		}

