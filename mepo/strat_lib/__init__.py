import json
from pathlib import Path


strat_lib_path = Path(__file__).parent
js = {}
for f in strat_lib_path.rglob("*.json"):
	with open(f, "r") as fstream:
		js.update(json.loads("".join(fstream.readlines())))
pass
