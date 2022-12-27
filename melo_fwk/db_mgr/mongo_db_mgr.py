import pymongo
import bson.objectid as boi

from melo_fwk.loggers.global_logger import GlobalLogger

class MongodbManager:

	def __init__(self, dburl: str = "mongodb://localhost:27017/"):
		"""
		:param dburl: mongodb url path
		"""

		self.dburl = dburl
		self.mongo_client = None
		self.db_connection = None
		self.connected = False
		self.logger = GlobalLogger.build_composite_for(type(self).__name__)

	def connect(self, dbname: str = "melo-db"):
		self.mongo_client = pymongo.MongoClient(self.dburl)
		self.db_connection = self.mongo_client[dbname]
		self.connected = True

	def close(self):
		self.mongo_client = None
		self.db_connection = None
		self.connected = False

	def insert_data(self, table: str, data: dict):
		collection = self.db_connection[table]
		query_result = collection.insert_one(data)
		self.logger.info(f"Inserted id in table {table} : {query_result.inserted_id} / data = {dict}")

	def update_data(self, table: str, data_id: str, data: dict):
		query, new_values = {"_id": boi.ObjectId(data_id)}, {"$set": data}
		collection = self.db_connection[table]
		query_result = collection.update_one(query, new_values)
		self.logger.info(f"Updated rows count {query_result.modified_count} in table {table} / order : {data}")

	def get_data_by_id(self, table: str, data_id: str):
		if data_id != "" or data_id is not None:
			return self.select_request(table, {"_id": data_id})

	def get_data(self, table: str):
		return self.select_request(table)


	def delete_by_id(self, table: str, data_id: str):
		query = {"_id": boi.ObjectId(data_id)}
		collection = self.db_connection[table]
		query_result = collection.delete_one(query)
		self.logger.info(f"Deleted document/row {query_result.deleted_count} from table {table} / _id : {data_id}")

	def select_request(self, table: str, request: dict = None, verbose: bool = True):
		request = {} if request is None else request
		if not self.connected:
			self.connect()

		collection = self.db_connection[table]
		orders = collection.find(request, {})

		if verbose:
			if orders is not None:
				self.logger.info("Find request executed. Result is not empty")
			else:
				self.logger.warn("Find request executed. Result is empty")

		return orders

	def __del__(self):
		self.close()
