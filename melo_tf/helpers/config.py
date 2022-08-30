
import yaml

from dataclasses import dataclass

@dataclass(frozen=True)
class MySql:
	hostname: str
	port: int
	username: str
	password: str


def parse_cfg(filename: str):
	with open(filename, "r") as stream:
		try:
			return yaml.safe_load(stream)
		except yaml.YAMLError as exc:
			print(exc)


if __name__ == "__main__":
	# cfg = parse_cfg("../data/ConfigPoints/draft.yaml")
	# mysql = MySql(**cfg["mysqldatabase"])
	# print(mysql)
	# print(cfg["complexData"])
	cfg = parse_cfg("../data/ConfigPoints/mvpWorkflow.yaml")
	print(cfg)
