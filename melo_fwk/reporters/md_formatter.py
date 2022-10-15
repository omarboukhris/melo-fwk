

class MdFormatter:

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
		return f"![{alt_text}][{image_file_path} {title}]\n"

	@staticmethod
	def save_md(filename: str, ss: str):
		try:
			with open(filename, "w") as fstream:
				fstream.write(ss)
		except Exception as e:
			print(f"(MdFormatter) Exception caught : {e}")
			