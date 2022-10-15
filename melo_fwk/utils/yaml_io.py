
import yaml

def read_strat_config_point(config_point_fn: str):
	config_points_registry = {}
	try:
		with open(config_point_fn, "r") as stream:
			for strat_config in yaml.safe_load(stream):
				config_points_registry.update(
					strat_config)
	except yaml.YAMLError as exc:
		print(f"(YAMLError) {exc}")
	except Exception as e:
		print(f"(Exception) {e}")
	finally:
		return config_points_registry

