#!/usr/bin/env python
# vim:se fileencoding=utf8 noet :
# (c) 2015 Michał Górny
# 2-clause BSD license

import os.path
import sys


# needs to match projects.xml
WIKI_BASE_URL = 'https://wiki.gentoo.org/wiki/'


def main(path):
	with open(path) as f:
		for l in f:
			# as dumb as possible
			if l.startswith('| '):
				herd, project = (x.strip(' |[]') for x in l.split('||')[:2])
				print('%s: %s' % (herd, os.path.join(WIKI_BASE_URL,
					project.replace(' ', '_')) if project else ''))


if __name__ == '__main__':
	sys.exit(main(*sys.argv[1:]))
