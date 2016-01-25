#!/usr/bin/env python
# vim:se fileencoding=utf8 noet :
# (c) 2015 Michał Górny
# 2-clause BSD license

import glob
import lxml.etree
import os
import sys


def set_types(r, projects, devs):
	for m in r.findall('maintainer'):
		m_email = m.find('email').text.strip().lower()
		if m_email in projects:
			new_type = 'project'
		elif m_email in devs:
			new_type = 'person'
		elif not m_email.endswith('@gentoo.org'):
			new_type = 'person'
		else:
			raise ValueError("%s is neither a project nor a person"
					% m_email)
		m.set('type', new_type)


def main(repopath, projects_xml, dev_names):
	projects = set()
	projects_xml = lxml.etree.parse(projects_xml)
	for p in projects_xml.getroot():
		p_email = p.find('email').text.lower()
		projects.add(p_email)

	devs = set()
	with open(dev_names) as f:
		for d in f:
			devs.add((d.strip() + '@gentoo.org').lower())

	for f in glob.glob(os.path.join(repopath, '*/*/metadata.xml')):
		subpath = os.path.relpath(f, repopath)
		print(subpath)

		xml = lxml.etree.parse(f)
		r = xml.getroot()

		set_types(r, projects, devs)

		with open(f, 'wb') as f:
			f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
			xml.write(f, encoding='UTF-8')
			# yay, add trailing newline because lxml is dumb
			f.write(b'\n')


	return 0


if __name__ == '__main__':
	sys.exit(main(*sys.argv[1:]))
