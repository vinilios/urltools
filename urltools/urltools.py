"""
Copyright (c) 2013 Roderick Baier

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import os
import re
import urllib
from collections import namedtuple
from urlparse import urlparse


PSL_URL = "http://mxr.mozilla.org/mozilla-central/source/netwerk/dns/effective_tld_names.dat?raw=1"

def _get_public_suffix_list():
    if os.environ.get("PUBLIC_SUFFIX_LIST"):
        psl_raw = open(os.environ['PUBLIC_SUFFIX_LIST']).readlines()
    else:
        psl_raw = urllib.urlopen(PSL_URL).readlines()
    psl = {}
    for line in psl_raw:
        line = line.strip()
        if line != '' and not line.startswith('//'):
            psl[line] = 1
    return psl

PSL = _get_public_suffix_list()


PORT_RE = re.compile(r'(?<=.:)[1-9]+[0-9]{0,4}$')


ResultSet = namedtuple("ResultSet", "scheme domain tld port path query fragment")


def normalize(url):
    parts = parse(url)
    nurl = parts.scheme + '://'
    nurl += parts.domain
    nurl += "." + parts.tld
    if parts.port != "80":
        nurl += ":" + parts.port
    nurl += parts.path
    if parts.query:
        nurl += "?" + parts.query
    if parts.fragment:
        nurl += "#" + parts.fragment
    return nurl


def parse(url):
    parts = urlparse(url)
    netloc = parts.netloc.rstrip('.').lower()
    port = "80"
    if PORT_RE.findall(netloc):
        netloc, port = netloc.split(":")
    path = parts.path if parts.path else '/'

    domain = netloc
    tld = ''
    d = netloc.split('.')
    for i in range(len(d)):
        tld = '.'.join(d[i:])
        wildcard_tld = "*." + tld
        if PSL.get(tld):
            domain = '.'.join(d[:i])
            break
        if PSL.get(wildcard_tld):
            domain = '.'.join(d[:i-1])
            tld = '.'.join(d[i-1:])
            break

    return ResultSet(parts.scheme, domain, tld, port, path, parts.query, parts.fragment)
