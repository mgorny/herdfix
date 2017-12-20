#!/usr/bin/env python
# vim:se fileencoding=utf8 noet :
# (c) 2017 Michał Górny
# 2-clause BSD license

from collections import defaultdict, namedtuple
import errno
import glob
import io
import json
from lxml.builder import E
import lxml.etree
import os
import os.path
import sys


def main(repopath, dev_email):
	if '@' not in dev_email:
		dev_email += '@gentoo.org'

	for f in glob.glob(os.path.join(repopath, '*/*/metadata.xml')):
		subpath = os.path.relpath(f, repopath)

		xml = lxml.etree.parse(f)
		r = xml.getroot()

		# check if dev maintains it
		maints = r.findall('maintainer')
		for m in maints:
			if m.findtext('email') == dev_email:
				break
		else:
			continue

		# a single maintainer? we need maintainer-needed now!
		if len(maints) == 1:
			c = lxml.etree.Comment(' maintainer-needed ')
			c.tail = m.tail
			r.replace(m, c)

			# print for 'up for grabs'
			print('/'.join(subpath.split('/')[:2]))
		else:
			r.remove(m)

		with open(f, 'wb') as f:
			f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
			xml.write(f, encoding='UTF-8')
			# yay, add trailing newline because lxml is dumb
			f.write(b'\n')

	return 0


if __name__ == '__main__':
	sys.exit(main(*sys.argv[1:]))
