#!/usr/bin/env python
# vim:se fileencoding=utf8 noet :
# (c) 2015 Michał Górny
# 2-clause BSD license

import json
import lxml.etree
import sys
import urllib.parse


def main(name_mapping, herds_xml, projects_xml):
	outmap = {}

	# mapping of herds to herd maintainers
	herds_db = {}
	herds_xml = lxml.etree.parse(herds_xml)
	for h in herds_xml.getroot():
		h_name = h.find('name').text
		herds_db[h_name] = []
		for m in h.findall('maintainer'):
			try:
				m_name = m.find('name').text
			except AttributeError:
				m_name = None
			m_email = m.find('email').text
			herds_db[h_name].append({
				'email': m_email,
				'name': m_name,
			})

	# mapping of project urls to project info
	projects_db = {}
	projects_xml = lxml.etree.parse(projects_xml)
	for p in projects_xml.getroot():
		p_url = urllib.parse.unquote(p.find('url').text)
		p_name = p.find('name').text
		p_email = p.find('email').text
		projects_db[p_url] = {
			'email': p_email,
			'name': p_name,
		}

	with open(name_mapping) as f:
		for l in f:
			herd, project = (x.strip() for x in l.split(':', 1))
			outmap[herd] = []
			if project:
				outmap[herd].append(projects_db[project])
			else:
				outmap[herd].extend(herds_db[herd])

	json.dump(outmap, sys.stdout)

	return 0


if __name__ == '__main__':
	sys.exit(main(*sys.argv[1:]))
