
from pyparse.pyparse import *
from pathlib import Path

from mql.mql_decoder import MqlDecoder


class MqlParser:
	_mqlDecoder = MqlDecoder
	_mql_rc_path = Path(Path(__file__).parent / "mql_grammar")
	_mql_grammar_path = Path(_mql_rc_path / "mql.grm")

	def __init__(self):
		self.parser = ParseSession(0)
		self.parser.load_grammar(
			filepath=str(MqlParser._mql_grammar_path),
			verbose=False)

	def parse_to_json(self, filepath: str):
		return self.parser.parse_to_json(filepath)

	def parse_to_config(self, filepath: str):
		raw_parsed_mql = str(self.parse_to_json(filepath)).replace("'", '"')
		return json.loads(raw_parsed_mql, cls=self._mqlDecoder)


if __name__ == "__main__":
	mql_testfile_path = str(
		Path(__file__).parent /
		"data/mql_strat_opt_template/stratoptim_example_query.sql")
	print(mql_testfile_path)
	parser = MqlParser()
	parsed = parser.parse_to_json(mql_testfile_path)
	print(parsed)

