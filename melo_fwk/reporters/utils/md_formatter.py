

class MdFormatter:

	@staticmethod
	def item_list(items: list):
		ss = ""
		for i in items:
			ss += f"- {i}\n"
		return ss

	@staticmethod
	def bold(ss: str):
		return f"**{ss}**"

	@staticmethod
	def italic(ss: str):
		return f"*{ss}*"

	@staticmethod
	def h1(ss: str):
		return f"# {ss}\n"

	@staticmethod
	def h2(ss: str):
		return f"## {ss}\n"

	@staticmethod
	def h3(ss: str):
		return f"### {ss}\n"

	@staticmethod
	def image(title: str, image_file_path: str, alt_text: str):
		return f"![{alt_text}]({image_file_path} \"{title}\")\n"

	@staticmethod
	def save_md(export_folder: str, filename: str, ss: str):
		try:
			if filename[-3:] != ".md":
				filename += ".md"
			with open(f"{export_folder}/{filename}", "w") as fstream:
				fstream.write(ss)
		except Exception as e:
			print(f"(MdFormatter) Exception caught : {e}")
			