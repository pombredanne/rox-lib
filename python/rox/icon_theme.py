"""This is an internal module. Do not use it. GTK 2.4 will contain functions
that replace those defined here."""

import os
import basedir
import rox

theme_dirs = [os.path.join(os.environ.get('HOME', '/'), '.icons')] + \
		list(basedir.load_data_paths('icons'))

class Index:
	def __init__(self, dir):
		self.dir = dir
		sections = file(os.path.join(dir, "index.theme")).read().split('\n[')
		self.sections = {}
		for s in sections:
			lines = s.split('\n')
			sname = lines[0].strip('[] \t')
			section = self.sections[sname] = {}
			for line in lines[1:]:
				if not line.strip(): continue
				if line.startswith('#'): continue
				key, value = map(str.strip, line.split('=', 1))
				section[key] = value

		self.subdirs = [SubDir(self, d) for
			d in self.get('Icon Theme', 'Directories').split(';')]

	def get(self, section, key):
		"None if not found"
		return self.sections.get(section, {}).get(key, None)

def DirectoryMatchesSize(index, subdir, iconsize):
	type = index.get(subdir, 'Type')
	size = int(index.get(subdir, 'Size'))
	print index, subdir, iconsize, type, size
	if type == "Fixed":
		return size == iconsize
	if type == "Scaled":
		min_size = int(index.get(subdir, 'MinSize'))
		max_size = int(index.get(subdir, 'MaxSize'))
		return min_size <= iconsize <= max_size
	if type == "Threshold":
		threshold = int(index.get(subdir, 'Threshold'))
		return size - threshold <= iconsize <= size + threshold
	return False

def DirectorySizeDistance(index, subdir, iconsize):
	type = index.get(subdir, 'Type')
	size = int(index.get(subdir, 'Size'))
	if type == "Fixed":
		return abs(size - iconsize)
	if type == "Threshold":
		threshold = int(index.get(subdir, 'Threshold'))
		min_size = size - threshold
		max_size = size + threshold
	elif type == "Scaled":
		min_size = int(index.get(subdir, 'MinSize'))
		max_size = int(index.get(subdir, 'MaxSize'))
	else:
		return 1000

	if iconsize < min_size:
		return min_size - iconsize
	if iconsize > max_size:
		return iconsize - max_size
	return 0

class SubDir:
	def __init__(self, index, subdir):
		type = index.get(subdir, 'Type')
		self.name = subdir
		self.size = int(index.get(subdir, 'Size'))
		if type == "Fixed":
			self.min_size = self.max_size = self.size
		elif type == "Threshold":
			threshold = int(index.get(subdir, 'Threshold'))
			self.min_size = self.size - threshold
			self.max_size = self.size + threshold
		elif type == "Scaled":
			self.min_size = int(index.get(subdir, 'MinSize'))
			self.max_size = int(index.get(subdir, 'MaxSize'))
		else:
			self.min_size = self.max_size = 100000

class IconTheme:
	def __init__(self, name):
		self.name = name

		self.indexes = []
		for dir in theme_dirs:
			theme_dir = os.path.join(dir, name)
			index_file = os.path.join(theme_dir, 'index.theme')
			if os.path.exists(os.path.join(index_file)):
				try:
					self.indexes.append(Index(theme_dir))
				except:
					rox.report_error()
	
	def lookup_icon(self, iconname, size):
		icon = self._lookup_this_theme(iconname, size)
		if icon: return icon
		# XXX: inherits
	
	def _lookup_this_theme(self, iconname, size):
		dirs = []
		for i in self.indexes:
			for d in i.subdirs:
				if size < d.min_size:
					diff = d.min_size - size
				elif size > d.max_size:
					diff = size - d.max_size
				else:
					diff = 0
				dirs.append((diff, os.path.join(i.dir, d.name)))

		# Sort by closeness of size
		dirs.sort()

		minimal_size = 1000000
		for _, subdir in dirs:
			for extension in ("png", "svg"):
				filename = os.path.join(subdir,
					iconname + '.' + extension)
				if os.path.exists(filename):
					return filename

rox_theme = IconTheme('ROX')
