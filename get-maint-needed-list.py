#!/usr/bin/env python
# vim:se fileencoding=utf8 noet :
# (c) 2015 Michał Górny
# 2-clause BSD license

import glob
import lxml.etree
import os
import sys


def is_m_needed(r):
	found_mn = False
	for h in list(r.findall('herd')):
		if h.text.strip() == 'maintainer-needed':
			found_mn = True
			r.remove(h)
	for m in list(r.findall('maintainer')):
		m_email = m.find('email').text.strip()
		if m_email == 'maintainer-needed@gentoo.org':
			found_mn = True
			r.remove(m)

	maints = list(r.findall('herd')) + list(r.findall('maintainer'))
#	if found_mn and len(maints) > 0:
#		raise ValueError('Found both maintainer-needed@ and real maintainers!')
	return len(maints) == 0


def main(repopath, out_file):
	with open(out_file, 'w') as outf:
		for f in glob.glob(os.path.join(repopath, '*/*/metadata.xml')):
			subpath = os.path.relpath(f, repopath)
			print(subpath)

			xml = lxml.etree.parse(f)
			r = xml.getroot()

			if is_m_needed(r):
				outf.write(subpath.rpartition('/')[0] + '\n')

	return 0


if __name__ == '__main__':
	sys.exit(main(*sys.argv[1:]))
