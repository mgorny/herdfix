#!/usr/bin/env python
# vim:se fileencoding=utf8 noet :
# (c) 2015 Michał Górny
# 2-clause BSD license

import lxml.etree
import sys
import urllib.request


def main(url):
	with urllib.request.urlopen(url) as f:
		html = lxml.etree.parse(f, lxml.etree.HTMLParser())
		print(html.xpath('//textarea')[0].text)


if __name__ == '__main__':
	sys.exit(main(*sys.argv[1:]))
