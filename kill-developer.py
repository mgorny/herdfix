#!/usr/bin/env python
# vim:se fileencoding=utf8 noet :
# (c) 2017 Michał Górny
# (c) 2018 Amy Liffey
# 2-clause BSD license

import argparse
from collections import defaultdict, namedtuple
import errno
import glob
import io
import json
from lxml.builder import E
import lxml.etree as etree
import os
import os.path
import sys


def main() -> int:
    """Parameters"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', help='Path to your repo /home/user/gentoo/')
    parser.add_argument('-e', '--email', help='Email of person you want to retire user@gentoo.org')
    parser.add_argument('-r', '--repoman', help='Add if you want to run repoman', action='store_true')
    args = parser.parse_args()

    if args.email is None or args.path is None:
        parser.print_help(sys.stdout)
        return 0

    # Store packages which are maintained by the person
    proxy_maint = False
    if '@gentoo.org' not in args.email:
        proxy_maint = True
    pkg = []
    grabs = []

    for f in glob.glob(os.path.join(args.path, '*/*/metadata.xml')):
        # Store subpath, parse xml
        subpath = os.path.relpath(f, args.path)
        xml = etree.parse(f)
        r = xml.getroot()

        # Check if person maintains the package
        maints = r.findall('maintainer')

        for m in maints:
            if m.findtext('email') == args.email:
                pkg.append('/'.join(subpath.split('/')[:2]))
                break
        else:
            continue

        # a single maintainer? we need maintainer-needed now!
        if proxy_maint and len(maints) == 2:
            c = etree.Comment(' maintainer-needed ')
            r.replace(m, c)
            for p in maints:
                if p.findtext('email') == 'proxy-maint@gentoo.org':
                    r.remove(p)
            c.tail = p.tail
            grabs.append('/'.join(subpath.split('/')[:2]))
        elif len(maints) == 1:
            c = etree.Comment(' maintainer-needed ')
            c.tail = m.tail
            r.replace(m, c)
            grabs.append('/'.join(subpath.split('/')[:2]))
        else:
            if proxy_maint:
                r.remove(m)
                for p in maints:
                    if p.findtext('email') == 'proxy-maint@gentoo.org':
                        r.remove(p)
            else:
                r.remove(m)

#        f.write(f, pretty_print=True, encoding="unicode")
        with open(f, 'wb') as f:
           f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
           xml.write(f, encoding='UTF-8', pretty_print=True)
           # yay, add trailing newline because lxml is dumb
           f.write(b'\n')

    if args.repoman:
        for p in pkg:
            print(p)
            os.chdir(args.path + p)
            os.system('repoman -x full')

    print('Packages up for grabs:')
    for g in grabs:
        print(g)
    return 0


if __name__ == '__main__':
    exit(main())
