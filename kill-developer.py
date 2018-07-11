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
import subprocess


def main() -> int:
    """Parameters"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', help='Path to your repo /home/user/gentoo/', required=True)
    parser.add_argument('-e', '--email', help='Email of person you want to retire user@gentoo.org', required=True)
    parser.add_argument('-r', '--repoman', help='Add if you want to run repoman', action='store_true')
    args = parser.parse_args()

    # Store packages which are maintained by the person
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

        # Search for other proxy maintainers
        other_maint = False
        for pr in maints:
            if pr.findtext('email') != args.email and not pr.findtext('email').endswith('@gentoo.org'):
                other_maint = True

        # Remove proxy maintainers project if only one proxy maintainer
        if not other_maint:
            for p in maints:
                if p.findtext('email') == 'proxy-maint@gentoo.org':
                    r.remove(p)
            maints = r.findall('maintainer')

        # a single maintainer? we need maintainer-needed now!
        if len(maints) == 1:
            c = etree.Comment(' maintainer-needed ')
            c.tail = m.tail
            r.replace(m, c)
            grabs.append('/'.join(subpath.split('/')[:2]))
        else:
            r.remove(m)

        # Write all the changes to the metadata.xml
        with open(f, 'wb') as f:
            f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
            xml.write(f, encoding='UTF-8', pretty_print=True)

    # Run repoman in edited packages
    if args.repoman:
        for p in pkg:
            print(p)
            subprocess.Popen(['repoman', 'full', '-x'], cwd=os.path.join(args.path, p)).wait()

    print('Packages up for grabs:')
    for g in grabs:
        print(g)
    return 0


if __name__ == '__main__':
    exit(main())
