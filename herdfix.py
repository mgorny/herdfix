#!/usr/bin/env python
# vim:se fileencoding=utf8 noet :
# (c) 2015 Michał Górny
# 2-clause BSD license

from collections import namedtuple
import errno
import glob
import json
from lxml.builder import E
import lxml.etree
import os
import os.path
import sys


def replace(r, herddb):
	"""
	Replace <herd/> with <maintainer/> elements, guessing indent.

	r: XML root element
	herddb: Herds replacement database
	"""
	herds = r.findall('herd')
	if not herds: # yay, one file less to care about
		return
	maints = r.findall('maintainer')
	if maints:
		insertpoint = maints[-1]
	else:
		insertpoint = herds[-1]

	# try to guess indentation
	def all_texts(node):
		first = True
		for e in node:
			if first:
				yield node.text
				first = False
			yield e.tail

	def all_indents(node):
		for t in all_texts(node):
			if t is None:
				yield ''
				return
			spl = t.split('\n')
			# go to last line without text
			for l in spl:
				if l.lstrip(' \t') != '':
					break
			# go to the last line
			t = l[:len(l) - len(l.lstrip(' \t'))]
			yield t

	def sub_indents(node):
		for e in node:
			for x in all_indents(e):
				yield x

	# some random defaults
	indent = '\t'
	try:
		indent = max(all_indents(r), key=len)
	except ValueError:
		pass

	inner_indent = indent*2 if indent else '\t'
	try:
		inner_indent = max(sub_indents(r), key=len)
	except ValueError:
		pass

	# start adding new herds after maintainers
	for h in herds:
		new_maints = herddb[h.text.strip()]

		# look for duplicate <herd/> entries
		for m in maints:
			m_email = m.find('email').text.strip()
			for nmc in new_maints:
				if m_email == nmc['email']:
					new_maints.remove(nmc)
					break

		if not new_maints:
			r.remove(h)
		else:
			first_m = None

			for new_maint in new_maints:
				els = ['\n',
					inner_indent, E.email(new_maint['email']), '\n']
				if new_maint['name']:
					els += [
						inner_indent, E.name(new_maint['name']), '\n']
				els += [indent]
				nm = E.maintainer(*els)
				if first_m is not None:
					first_m = nm

				nextinsert = insertpoint.getnext()
				nm.tail = insertpoint.tail
				if nextinsert is not None:
					r.insert(r.index(nextinsert), nm)
				else:
					# avoid extra indent
					nm.tail = '\n'
					r.append(nm)
				insertpoint = nm

			# now we can remove it safely
			r.remove(h)

			if first_m is not None:
				# now fix pre-indent
				prev = first_m.getprevious()
				if prev is not None:
					prev.tail = '\n' + indent
				else:
					first_m.getparent().text = '\n' + indent


def main(repopath, herd_mapping):
	with open(herd_mapping) as f:
		herddb = json.load(f)

	# special cases
	herddb['maintainer-needed'] = []
	herddb['no-herd'] = []

	# LAZINESS!
	for f in glob.glob(os.path.join(repopath, '*/*/metadata.xml')):
		subpath = os.path.relpath(f, repopath)
		print(subpath)

		xml = lxml.etree.parse(f)
		r = xml.getroot()

		replace(r, herddb)

		try:
			os.unlink(f)
		except OSError as e:
			if e.errno != errno.ENOENT:
				raise
		xml.write(f, encoding='UTF-8', xml_declaration='1.0')
		# yay, add trailing newline because lxml is dumb
		with open(f, 'ab') as f:
			f.write(b'\n')

	return 0


if __name__ == '__main__':
	sys.exit(main(*sys.argv[1:]))
