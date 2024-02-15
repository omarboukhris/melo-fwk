
from pathlib import Path


mepo_work_dir = Path(__file__).parent
books_filepath = [i for i in mepo_work_dir.rglob("*.sql")]
auto_books = {
	f'mepo.{auto_book.as_uri().replace(mepo_work_dir.as_uri(), "")[1:].replace(".sql", "").replace("/", ".")}': auto_book
	for auto_book in books_filepath
}
pass
