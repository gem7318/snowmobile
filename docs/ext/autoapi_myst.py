
from pathlib import Path
from typing import List
import re
import shutil
import os

MAP_HEADER_SYMBOL = {
	'=': '#',
	'-': '##',
	'~': '###'
}

HERE = Path(__file__).absolute()  # current file location
DOC_ROOT = HERE.parent.parent     # documentation root directory
AUTOAPI_DIR = DOC_ROOT / '_build' / '_sources' / 'autoapi'


class MySTConv:
	"""Converts autoapi rst.txt to compliant MySt."""

	def __init__(self, path: Path):

		self.path = path
		self.path_final = path.parent / f"{path.stem.split('.')[0]}.md.txt"

		self.txt: str = str()

		self.sym1, self.sym2 = '{', '}'
		self.eval_rst = r'{eval-rst}```'

		self.lines = self.txt.split('\n')
		self.lines_vf: List[str] = list()

		self.line_dtl = {}

		self.line_no_f: int = int()

	def get_lines(self):
		"""Identifies lines following headers by header-level."""
		for i, line in enumerate(self.lines):
			if i != 0:
				for s_s, s_t in MAP_HEADER_SYMBOL.items():
					length = len(self.lines[i-1])
					patt = f'{s_s}{self.sym1}{length}{self.sym2}'
					if re.findall(patt, line) and length != 0:
						self.line_dtl[i] = s_s

	def to_myst(self, line: str):
		"""Converts a rst role to an MySt role."""
		if ':' not in line:
			return line
		_, role, obj = line.split(':')
		return f"{self.sym1}{role}{self.sym2}{obj}"

	@property
	def alt_header(self):
		"""First header replacement."""
		self.line_no_f = min(self.line_dtl)
		line_sym = self.line_dtl[self.line_no_f]
		header_sym = MAP_HEADER_SYMBOL[line_sym]
		header_txt = self.to_myst(self.lines[self.line_no_f - 1])
		return f"{header_sym} {header_txt}\n\n{self.eval_rst}\n"

	@property
	def is_swappable(self) -> bool:
		"""Determines if there is an h1 header to be replaced."""
		return min(self.line_dtl) == 1 if len(self.line_dtl) else False

	def swap(self):
		"""Replaced text to save as markdown."""
		self.lines_vf = [line for line in self.lines[self.line_no_f + 2:]]
		self.lines_vf.append('\n```\n')
		self.lines_vf.insert(0, self.alt_header)

	@property
	def txt_final(self) -> str:
		"""Swapped text to saved as markdown."""
		return "\n".join(self.lines_vf)

	def eval(self):
		"""Saves new file as markdown."""
		# read file
		with open(self.path, 'r') as r:
			self.txt = r.read()
		self.get_lines()

		# check if it should be messed with further
		if not self.is_swappable:
			return

		# rename with .md.txt extension and write modified text to it
		self.swap()
		os.remove(path=str(self.path))
		with open(self.path_final, 'w') as f:
			f.write(self.txt_final)
		print(f"\tconverted: {self.path.as_posix()}")


def to_myst():
	"""Batch converts all autoapi RST files to MySt-compliant markdown."""
	files = [
		f for f in AUTOAPI_DIR.rglob('**/*')
		if f.is_file() and str(f).endswith(r'.rst.txt')
	]
	print("\n----/ Starting AutoAPI to MySt /----")
	for f in files:
		c = MySTConv(path=f)
		c.eval()

