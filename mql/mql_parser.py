
from pyparse.pyparse import *
from pathlib import Path

from mql.mql_decoder import MqlDecoder


class MqlParser:
	"""
	TODO: Make second parsesession for pf simulations
		motivation: grammar got big, splitting parsers is the only way
		to not mess with the engine
		best alternative (but expensive) is to implement a better language parsing engine
	"""

	_mqlDecoder = MqlDecoder
	_mql_rc_path = Path(Path(__file__).parent / "grammar")

	def __init__(self):
		self.parser = ParseSession(0)
		self.parser_books = ParseSession(0)
		_mql_grammar_path = str(Path(MqlParser._mql_rc_path / "mql.grm"))
		_mql_books_grammar_path = str(Path(MqlParser._mql_rc_path / "mql_books.grm"))
		self.parser.load_grammar(
			filepath=_mql_grammar_path,
			verbose=False)
		self.parser_books.load_grammar(
			filepath=_mql_books_grammar_path,
			verbose=False)

	def parse_to_json(self, filepath: str):
		_parser = self._select_parser(filepath)
		return _parser.parse_to_json(filepath)

	def get_books_parser(self):
		return self.parser_books

	def parse_to_config(self, filepath: str):
		raw_parsed_mql = str(self.parse_to_json(filepath)).replace("'", '"')
		return json.loads(raw_parsed_mql, cls=self._mqlDecoder)

	def _select_parser(self, filepath: str) -> ParseSession:
		with open(filepath, "r") as fs:
			line = fs.readline().strip()
		return self.parser_books if line == "@books" else self.parser


if __name__ == "__main__":
	mql_testfile_path = str(
		Path(__file__).parent /
		"data/mql_strat_opt_template/stratoptim_example_query.sql")
	print(mql_testfile_path)
	parser, _ = MqlParser()
	parsed = parser.parse_to_json(mql_testfile_path)
	print(parsed)

