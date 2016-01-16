#!/usr/bin/env python
# vim:se fileencoding=utf8 noet :
# (c) 2016 Michał Górny
# 2-clause BSD license

import glob
import lxml.etree
import os
import sys


def in_herd(r, herd, herd_email):
	for h in list(r.findall('herd')):
		if h.text.strip() == herd:
			return True
	if herd_email is not None:
		for m in list(r.findall('maintainer')):
			if m.find('email').text.strip() == herd_email:
				return True
	return False


def other_maints(r, herd, herd_email):
	for h in list(r.findall('herd')):
		if h.text.strip() != herd:
			yield h.text.strip()

	for m in list(r.findall('maintainer')):
		m_email = m.find('email').text.strip()
		if m_email != herd_email:
			yield m_email.replace('@gentoo.org', '@')


def main(repopath, herd_name, extra_email = None):
	for f in glob.glob(os.path.join(repopath, '*/*/metadata.xml')):
		subpath = os.path.relpath(f, repopath)

		xml = lxml.etree.parse(f)
		r = xml.getroot()

		if in_herd(r, herd_name, extra_email):
			print('%-28s : %s'
					% (subpath.rpartition('/')[0],
						', '.join(other_maints(r, herd_name, extra_email))))

	return 0


if __name__ == '__main__':
	sys.exit(main(*sys.argv[1:]))
