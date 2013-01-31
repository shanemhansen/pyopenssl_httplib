#!/usr/bin/env python
#
# Copyright (C) 2013 Shane Hansen
#
"""
    Wrapper class which allows pyopenssl to interoperate with python's
    httplib (and thus urlib3 and other libraries). Also contains integration
    with urllib3 if present.
"""
__all__ = ["HTTPSConnection"]

import socket

from httplib import HTTPConnection, HTTPS_PORT
from OpenSSL import SSL
try:
    import urllib3
    __all__.append("HTTPSConnectionPool")
except ImportError:
    urllib3 = None


class HTTPSConnection(HTTPConnection):
    """This class allows communication via SSL using PyOpenSSL.
    It is a dropin replacement for httplib.HTTPSConnection, but optionally
    allows a ssl context to be passed.

    For host, port, key_file, cert_file, strict, timeout, source_address
    see httplib.HTTPConnection

    @param ssl_ctx: optional ssl_ctx to pass in
    @type ssl_ctx: OpenSSL.SSL.Context
    """

    default_port = HTTPS_PORT

    def __init__(
        self, host, port=None, key_file=None, cert_file=None,
        strict=None,
        timeout=socket._GLOBAL_DEFAULT_TIMEOUT,  # pylint:disable-msg=W0212
            source_address=None, ssl_ctx=None):
        HTTPConnection.__init__(self, host, port, strict, timeout,
                                source_address)
        self.key_file = key_file
        self.cert_file = cert_file
        if ssl_ctx is None:
            ssl_ctx = SSL.Context(SSL.SSLv23_METHOD)
        if self.key_file is not None:
            ssl_ctx.use_privatekey_file(self.key_file)
        if self.cert_file is not None:
            ssl_ctx.use_certificate_file(self.cert_file)
            ssl_ctx.use_certificate_chain_file(self.cert_file)
        self.ssl_ctx = ssl_ctx
        HTTPConnection.__init__(self, host, port, strict)

    def connect(self):
        """
        Create SSL socket and connect to peer. Note this uses
        socket.create_connection which is ip6 friendly.
        """
        sock = socket.create_connection((self.host, self.port),
                                        self.timeout, self.source_address)
        self.sock = Connection(self.ssl_ctx, sock)
        self.sock.set_connect_state()  # pylint:disable-msg=E1101

    def close(self):
        """Close socket and shutdown SSL connection"""
        self.sock.close()


class Connection(object):
    """
    Proxy to OpenSSL.SSL.Connection containing support for the .makefile()
    method.

    Rationale: The pyopenssl documentation states that
    OpenSSL.SSL.Connection.makefile raises a NotImplemented error because
    there are no .dup semantics for SSL connections which *is* the documented
    behaviour of of socket.makefile, but the documentation is incorrect.
    See: http://bugs.python.org/issue14303
    We can use the logic in socket._fileobject to implement .makefile(),
    allowing pyopenssl to play nice with python's httplib.
    """
    __slots__ = ["_conn"]

    def __init__(self, ctx, conn):
        self._conn = SSL.Connection(ctx, conn)

    def __getattr__(self, attr):
        return getattr(self._conn, attr)

    def makefile(self, *args):
        return socket._fileobject(self._conn,  # pylint:disable-msg=W0212
                                  *args)

if urllib3 is not None:

    class HTTPSConnectionPool(urllib3.HTTPConnectionPool):
        """
        A https connection pool backed by a pyopenssl connection.
        """

        scheme = "https"

        def __init__(self, host, port=None,
                     strict=False, timeout=None, maxsize=1,
                     block=False, headers=None, ctx=None):

            super(HTTPSConnectionPool, self).__init__(host, port,
                                                      strict, timeout, maxsize,
                                                      block, headers)
            self.ctx = ctx

        def _new_conn(self):
            """
            Return a fresh :class:`httplib.HTTPSConnection`.
            """
            self.num_connections += 1
            connection = HTTPSConnection(host=self.host, port=self.port,
                                         ssl_ctx=self.ctx)
            return connection
