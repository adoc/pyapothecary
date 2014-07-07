import os
import time as _time
import math
import base64
import logging
import sqlalchemy.orm
import sqlalchemy.ext.declarative


__all__ = ('hash', 'benc', 'random', 'time', 'token')

logger = logging.getLogger(__name__)


try:
    range = xrange
except NameError:
    pass # Py3 already.


try:
    import cryptu.hash
except ImportError:
    logger.warning("`cryptu` is unavailable. Using less secure hash "
                   "function.")
    import hashlib
    def hash(*args, **kwa):
        n = kwa.get('n', 100)
        alg = hashlib.sha512()
        for n in range(n):
            for arg in args:
                alg.update(arg)
        return alg.digest()
    hash.digest_length = 64
else:
    def hash(*args):
        return cryptu.hash.shash(*args).digest()
    hash.digest_length = 64 # SHA512 length


if hasattr(base64, 'b85encode'):
    # Check for py3.
    b85encode = base64.b85encode
    b85decode = base64.b85decode

    class benc(object):
        @classmethod
        def encode(cls, value):
            if not isinstance(value, bytes):
                value = value.encode()
            return base64.b85encode(value)

        @classmethod
        def decode(cls, value):
            if not isinstance(value, bytes):
                value = value.encode()
            return base64.b85decode(value)

        @classmethod
        def overhead(cls, n):
            return math.ceil(n / 4.0) * 5
else:
    try:
        import ascii85
    except ImportError:
        logger.warning("Base85 encoding is unavailable. Using base64. "
                       "(Install `ascii85`)")
        class benc(object):
            @classmethod
            def encode(cls, value):
                return base64.b64encode(value)

            @classmethod
            def decode(cls, value):
                return base64.b64decode(value)

            @classmethod
            def overhead(cls, n):
                return math.ceil(n / 3.0) * 4
    else:
        class benc(object):
            @classmethod
            def encode(cls, value):
                return ascii85.b85encode(value, begin_tag=False,
                                         end_tag=False).rstrip('\n')

            @classmethod
            def decode(cls, value):
                # Ascii85 expects an escape sequence.
                return ascii85.b85decode("<~%s~>\n" % value)

            @classmethod
            def overhead(cls, n):
                return math.ceil(n / 4.0) * 5


def time():
    return int(_time.time())


try:
    import cryptu.random as random
except ImportError:
    logger.warning("`cryptu` is unavailable. Using less secure hash "
                   "function.")
    import hashlib
    def read(length):
        # Don't use for greater than 10,000 bytes.
        def gen():
            for i in range(int(math.ceil(length/32.0))):
                rnd = os.urandom(length*8) # for attempted entropy.
                yield hashlib.sha256(rnd).digest()
        return ''.join(gen())[:length]

    def random():
        pass

    random.read = read


def token(length):
    # 2.7 here. Put 3.0+ handling in another func.
    return random.read(length)
    #return base64.b64encode(os.urandom(length*2)).encode()[:length]


def synonym(attr_name, *prop, **kwa):
    """Shortcut for a declarative synonym attribute.
    (*fget, fset, fdel)
    """

    if prop:
        kwa['descriptor'] = property(*prop)

    return sqlalchemy.ext.declarative.declared_attr(lambda cls:
                sqlalchemy.orm.synonym(attr_name, **kwa))


def column(*args, **kwa):
    """Shortcut for a declarative column attribute.
    """
    return sqlalchemy.ext.declarative.declared_attr(lambda cls:
                sqlalchemy.Column(*args, **kwa))