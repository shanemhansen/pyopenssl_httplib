#!/usr/bin/env python
"""
Some examples on using httplib
"""
import pyopenssl_httplib
from OpenSSL import SSL
#vanilla httplib example
conn = pyopenssl_httplib.HTTPSConnection('www.google.com', 443)
conn.request('GET', '/')
resp = conn.getresponse()
print "got {count} bytes from google".format(count=len(resp.read()))

#urllib3 example
try:
    pool = pyopenssl_httplib.HTTPSConnectionPool('www.google.com')
    resp = pool.urlopen('GET', '/', preload_content=False)
    print "got {count} bytes from google using urllib3".format(
        count=len(resp.read()))
except AttributeError:
    print "urllib3 not installed?"

#explicitly pass in a preconfigured SSL context
ctx = SSL.Context(SSL.TLSv1_METHOD)
# Ask OpenSSL to use system certificates if possible.
ctx.set_default_verify_paths()

# Just a fun example to show what kind of things you can do
# with a pyopenssl context


def verify_cb(conn, cert, errno, depth, ok):
    print "Looking at cert for subject {0}".format(cert.get_subject())
    return ok

ctx.set_verify(SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT,
               verify_cb)

pool = pyopenssl_httplib.HTTPSConnectionPool('www.google.com', ctx=ctx)
try:
    resp = pool.urlopen('GET', '/', preload_content=False)
    print "got {count} bytes from google using urllib3".format(
        count=len(resp.read()))
except SSL.Error, e:
    print "Couldn't verify google's cert. This may happen on windows or osx."
