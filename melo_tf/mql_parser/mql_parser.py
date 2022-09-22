
from pyparse.pyparse import *
from pathlib import Path

class MqlParser:
	mql_rc_path = Path(Path(__file__).parent / "mql")
	mql_grammar_path = Path(mql_rc_path / "mql.grm")

	def __init__(self):
		self.parser = ParseSession()
		self.parser.load_grammar(str(MqlParser.mql_grammar_path), True)

	def parse_to_json(self, filepath: str):
		return self.parser.parse_to_json(filepath)


if __name__ == "__main__":
	mql_testfile_path = str(
		Path(__file__).parent.parent /
		"data/mql/backtest_example_query.sql")
	parser = MqlParser()
	parsed = parser.parse_to_json(mql_testfile_path)
	print(parsed)

