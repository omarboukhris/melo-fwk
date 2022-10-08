
from pyparse.pyparse import *
from pathlib import Path

class MqlParser:
	mql_rc_path = Path(Path(__file__).parent / "mql_grammar")
	mql_grammar_path = Path(mql_rc_path / "mql.grm")

	def __init__(self):
		self.parser = ParseSession(0)
		self.parser.load_grammar(
			filepath=str(MqlParser.mql_grammar_path),
			verbose=False)

	def parse_to_json(self, filepath: str):
		return self.parser.parse_to_json(filepath)


if __name__ == "__main__":
	mql_testfile_path = str(
		Path(__file__).parent /
		"data/mql/backtest_example_query.sql")
	print(mql_testfile_path)
	parser = MqlParser()
	parsed = parser.parse_to_json(mql_testfile_path)
	print(parsed)

