#!/usr/bin/env python
# vim:se fileencoding=utf8 noet :
# (c) 2015 Michał Górny
# 2-clause BSD license

import glob
import lxml.etree
import os
import sys


def main(projects_xml, dev_names):
	devs = set()
	with open(dev_names) as f:
		for d in f:
			devs.add((d.strip() + '@gentoo.org').lower())

	projects_xml = lxml.etree.parse(projects_xml)
	for p in projects_xml.getroot():
		p_name = p.find('url').text
		p_email = p.find('email').text.lower()
		if p_email in devs:
			print('%s: %s' % (p_name, p_email))

	return 0


if __name__ == '__main__':
	sys.exit(main(*sys.argv[1:]))
