#!/usr/bin/env python
#  vim:se fileencoding=utf8
# (c) 2015 Michał Górny

import bugz.bugzilla
import json
import os
import os.path
import readline
import sys
import textwrap


token_file = os.path.expanduser('~/.bugz_token')
try:
    with open(token_file, 'r') as f:
        token = f.read().strip()
except IOError:
    print('! Bugz token not found, please run "bugz login" first')
    sys.exit(1)

bz = bugz.bugzilla.BugzillaProxy('https://bugs.gentoo.org/xmlrpc.cgi')

for mail in sys.argv[1:]:
    if mail.endswith('@g.o'):
        mail = mail[:-4]

    msg = '''
The herds have been deprecated by the Council and are being replaced
by projects. For this reason, please decide on the fate of the herd
stated in the summary and update [1] or state the request here.

The common choices are:

1. Map the herd to an existing project (in this case all packages
in the herd will be maintained by the project) -- let us know which
project to use.

2. Create a new project for the herd -- create the wiki page, let us
know the new mail alias name to be created, create the wiki page
and let us know about it.

3. Decide to disband the herd -- just let us know (but keep it for now
in herds.xml!), we'll replace it with individual maintainers when herds
are removed.

[1]:https://wiki.gentoo.org/wiki/Project:Metastructure/Herd_to_project_mapping

'''.strip()

    params = {
        'Bugzilla_token': token,
        'product': 'Gentoo Infrastructure',
        'component': 'Other',
        'version': 'unspecified',
        'summary': 'Please provide mapping for herd %s@g.o (GLEP67)' % mail,
        'description': msg,
        'assigned_to': '%s@gentoo.org' % mail,
        'blocks': ['glep67-tracker'],
    }
    print(mail)

    ret = bz.Bug.create(params)

    print('%s filed as #%d' % (mail, ret['id']))
