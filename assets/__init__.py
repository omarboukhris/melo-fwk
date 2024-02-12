from pathlib import Path


products_path = Path(__file__).parent
products_filepath = list(products_path.rglob("*.csv"))
products_map = {
	str(posix_path).replace(str(products_path), "").replace("/", ".")[1:-4]: posix_path
	for posix_path in products_filepath
}
pass
