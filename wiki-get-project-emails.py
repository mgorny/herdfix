#!/usr/bin/env python
# vim:se fileencoding=utf8 noet :
# (c) 2015 Michał Górny
# 2-clause BSD license

import errno
import json
import lxml.etree
import os.path
import sys
import urllib.request


WIKI_BASE = 'https://wiki.gentoo.org/index.php?action=formedit&title='


def main(name_mapping, project_db):
	projects = {}

	try:
		with open(project_db) as f:
			projects = json.load(f)
	except OSError as e:
		if e.errno != errno.ENOENT:
			raise

	try:
		with open(name_mapping) as f:
			for l in f:
				project = l.split(':', 1)[1].strip()
				if project and project not in projects:
					print(project)
					project_url = WIKI_BASE + project
					with urllib.request.urlopen(project_url) as f:
						html = lxml.etree.parse(f, lxml.etree.HTMLParser())
						name, email = (
								html.xpath('//input[@name="Project[%s]"]' % x)[0]
								.get('value') for x in ('Name', 'Email'))
						projects[project] = {
							'name': name,
							'email': email,
						}
	finally:
		with open(project_db, 'w') as f:
			json.dump(projects, f)

	return 0


if __name__ == '__main__':
	sys.exit(main(*sys.argv[1:]))
