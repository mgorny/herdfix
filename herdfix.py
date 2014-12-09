#!/usr/bin/env python

from collections import namedtuple
import errno
import glob
from lxml.builder import E
import lxml.etree
import os
import os.path

def main():
	herdtuple = namedtuple('herdtuple', ('email', 'name'))
	herddb = {}
	portdir = '/var/db/repos/gentoo'
	herdsfile = os.path.join(portdir, 'metadata/herds.xml')
	herdsxml = lxml.etree.parse(herdsfile)
	for h in herdsxml.getroot():
		k = h.find('name').text
		e = h.find('email').text
		d = h.find('description').text
		herddb[k] = herdtuple(e, d)

	intree = portdir
	outtree = '/tmp/1'

	# LAZINESS!
	for f in glob.glob(os.path.join(intree, '*/*/metadata.xml')):
		subpath = os.path.relpath(f, intree)
		print(subpath)
		outf = os.path.join(outtree, subpath)

		xml = lxml.etree.parse(f)
		herds = xml.getroot().findall('herd')
		if not herds: # yay, one file less to care about
			continue
		r = xml.getroot()
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
			he = herddb[h.text.strip()]
			attrs = dict(h.items())
			attrs['type'] = 'herd'
			nm = E.maintainer('\n',
				inner_indent, E.email(he.email), '\n',
				inner_indent, E.name(he.name), '\n',
				indent,
				**attrs
			)
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

			# now fix pre-indent
			prev = nm.getprevious()
			if prev is not None:
				prev.tail = '\n' + indent
			else:
				nm.getparent().text = '\n' + indent

		try:
			os.makedirs(os.path.dirname(outf))
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise
		try:
			os.unlink(outf)
		except OSError as e:
			if e.errno != errno.ENOENT:
				raise
		xml.write(outf, encoding='UTF-8', xml_declaration='1.0')
		# yay, add trailing newline because lxml is dumb
		with open(outf, 'ab') as f:
			f.write(b'\n')

if __name__ == '__main__':
	main()
