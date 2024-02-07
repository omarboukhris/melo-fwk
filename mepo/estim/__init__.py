
from pathlib import Path



mepo_work_dir = Path(__file__).parent
estim_filepath = [i for i in mepo_work_dir.rglob("*.json")]
estim_map = {
	f'estim.{estim.as_uri().replace(mepo_work_dir.as_uri(), "")[1:].replace(".json", "").replace("/", ".")}': estim
	for estim in estim_filepath
}
pass
