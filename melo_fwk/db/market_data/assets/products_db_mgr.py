
from tqdm import tqdm

from melo_fwk.db.mongo_db_mgr import MongodbManager
from melo_fwk.db.market_data.product import Product


class MarketDataDbManager(MongodbManager):

	def export_product_to_mongo(self, prefix: str, product: Product):
		doc = prefix + product.name
		collection = self.db_connection[doc]
		self.logger.info(f"Exporting {doc} into mongodb...")
		df_rows = product.datastream.dataframe.to_dict(orient="index").values()
		for row in tqdm(df_rows):
			collection.insert_one(row)
		self.logger.info(f"Updated rows count to table {doc} / rows : {len(df_rows)}")
