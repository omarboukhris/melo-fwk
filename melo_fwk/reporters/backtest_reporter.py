
from melo_fwk.reporters.md_formatter import MdFormatter
from melo_fwk.config.melo_config import MeloConfig

class BacktestReporter:

	def __init__(self):
		pass

	@staticmethod
	def process_input_config(input_config: MeloConfig):
		"""
		Displays input parameter responsible for the generated results
		Could be report header

		:param input_config:
		:return:
		"""
		pass

	@staticmethod
	def process_results(raw_results: dict):
		"""
		raw_results dict :
			key = product name
			Value = dict :
				key = product_filepath + year
				value = TSAR
		"""
		for product_name, tsar_dict in raw_results.items():

			assert isinstance(tsar_dict, dict), \
				f"(BacktestReporter) TSAR result {product_name} is not associated to a dict"

			for prod_fn_y, tsar in tsar_dict.items():

				pass

