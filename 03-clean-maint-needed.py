#!/usr/bin/env python
# vim:se fileencoding=utf8 noet :
# (c) 2015 Michał Górny
# 2-clause BSD license

import glob
import lxml.etree
import os
import sys


def remove_m_needed(r):
	for m in list(r.findall('maintainer')):
		m_email = m.find('email').text.strip()
		if m_email == 'maintainer-needed@gentoo.org':
			r.remove(m)

	if len(r) == 0:
		r.text = '\n'
		r.tail = ''


def main(repopath):
	for f in glob.glob(os.path.join(repopath, '*/*/metadata.xml')):
		subpath = os.path.relpath(f, repopath)
		print(subpath)

		xml = lxml.etree.parse(f)
		r = xml.getroot()

		remove_m_needed(r)

		with open(f, 'wb') as f:
			f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
			xml.write(f, encoding='UTF-8')
			# yay, add trailing newline because lxml is dumb
			f.write(b'\n')


	return 0


if __name__ == '__main__':
	sys.exit(main(*sys.argv[1:]))
