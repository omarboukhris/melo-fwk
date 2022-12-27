
from tqdm import tqdm

from melo_fwk.db_mgr.mongo_db_mgr import MongodbManager
from melo_fwk.market_data.product import Product


class MarketDataDbManager(MongodbManager):

	def export_product_to_mongo(self, product: Product):
		collection = self.db_connection[product.name]
		self.logger.info(f"Exporting {product.name} into mongodb...")
		df_rows = product.datastream.dataframe.to_dict(orient="index").values()
		for row in tqdm(df_rows):
			collection.insert_one(row)
		self.logger.info(f"Updated rows count to table {product.name} / rows : {len(df_rows)}")
