"""
"""
import math
import base64
import sqlalchemy.ext.hybrid
import cryptu.hash
import cryptu.random
import apothecary.modelmix

__all__ = ("user_mix", "group_mix", "permission_mix")


if hasattr(base64, 'b85encode'):
    b85encode = base64.b85encode
    b85decode = base64.b85decode
else:
    from ascii85 import b85encode, b85decode


def _hashfunc(*args):
    return cryptu.hash.shash(*args).digest()

_hashfunc.digest_length = 64 # SHA512 length


class _bencfunc(object):

    @classmethod
    def encode(self, value):
        return b85encode(value)

    @classmethod
    def decode(self, value):
        return b85decode(value)

    overhead = 1.25 # Base85 overhead.


def user_mix(name_col="name", name_size=32,
         namehash_col="namehash",
         passhash_col="passhash",
         salt_col="salt", salt_size=8,
         binary_encode=False, hashfunc=_hashfunc, basefunc=_bencfunc):
    """
    """
    assert callable(hashfunc), "`hashfunc` must be callable."
    assert callable(basefunc), "`basefunc` must be callable."

    internal_name_col = ''.join(['__', name_col])
    internal_namehash_col = ''.join(['__', namehash_col])
    internal_passhash_col = ''.join(['__', passhash_col])
    internal_salt_col = ''.join(['__', salt_col])

    hash_size = hashfunc.digest_length
    hash_benc_size = math.ceil(hash_size *
                                (basefunc.overhead+1))
    salt_benc_size = math.ceil(salt_size *
                                (basefunc.overhead+1))

    def encode(value):
        if binary_encode is True and value:
            return basefunc.encode(value)
        return value

    def decode(value):
        if binary_encode is True and value:
            return basefunc.decode(value)
        return value

    class User(object):
        """
        """
        @sqlalchemy.ext.hybrid.hybrid_property
        def _name(self):
            return getattr(self, internal_name_col)

        @_name.setter
        def _name(self, value):
            """Set name and namehash."""
            assert isinstance(value, basestring), "`value` must be a string."
            assert value, "`value` cannot be empty."
            setattr(self, internal_name_col, value)
            setattr(self, internal_namehash_col, encode(hashfunc(value)))

        @property
        def _salt(self):
            """Get salt if exists otherwise, create salt."""
            _salt = decode(getattr(self, internal_salt_col))
            if not _salt:
                _salt = cryptu.random.read(salt_size)
                setattr(self, internal_salt_col, encode(_salt))
            return _salt

        @sqlalchemy.ext.hybrid.hybrid_property
        def _passhash(self):
            return decode(getattr(self, internal_passhash_col))

        @_passhash.setter
        def _passhash(self, password):
            setattr(self, internal_passhash_col,
                    encode(hashfunc(password, self._salt)))

        @property
        def _password(self):
            raise AttributeError("Cannot get a password.")

        @_password.setter
        def _password(self, password):
            # Alias to _passhash setter.
            self._passhash = password

        def _challenge(self, password):
            challenge_hash = hashfunc(password, self._salt)
            # Always comparing binary hashes here.
            return challenge_hash == self._passhash

    # Create columns
    setattr(User, internal_name_col,
        sqlalchemy.Column(name_col,
            sqlalchemy.types.Unicode(length=name_size),
            unique=True))

    if binary_encode is True:
        setattr(User, internal_namehash_col,
            sqlalchemy.Column(namehash_col,
                sqlalchemy.types.String(hash_benc_size),
                index=True))
        setattr(User, internal_passhash_col,
            sqlalchemy.Column(passhash_col,
                sqlalchemy.types.String(hash_benc_size)))
        setattr(User, internal_salt_col,
            sqlalchemy.Column(salt_col,
                sqlalchemy.types.String(salt_benc_size)))
    else:
        setattr(User, internal_namehash_col,
            sqlalchemy.Column(namehash_col,
                sqlalchemy.types.LargeBinary(hash_size),
                index=True))
        setattr(User, internal_passhash_col,
            sqlalchemy.Column(passhash_col,
                sqlalchemy.types.LargeBinary(hash_size)))
        setattr(User, internal_salt_col,
            sqlalchemy.Column(salt_col,
                sqlalchemy.types.LargeBinary(salt_size)))

    return User


def group_mix(name_attr="name", name_col=None, name_size=32,
              level_attr="level", level_col=None):
    """
    """
    name_col = name_col or name_attr
    level_col = level_col or level_attr

    class Group(object):
        """
        """
        @property
        def _name(self):
            return getattr(self, name_attr)

        @_name.setter
        def _name(self, value):
            setattr(self, name_attr, value)

        @property
        def _level(self):
            return getattr(self, level_attr)

        @_level.setter
        def _level(self, value):
            setattr(self, level_attr, value)

        def __cmp__(self, target):
            return self._level - target._level

    setattr(Group, name_attr,
        sqlalchemy.Column(name_col,
                          sqlalchemy.types.Unicode(name_size),
                          nullable=False, unique=True))

    setattr(Group, level_attr,
        sqlalchemy.Column(level_col,
                          sqlalchemy.types.Integer(),
                          nullable=False, default=0))

    return Group


def permission_mix(name_attr="name", name_col=None, name_size=32):
    """
    """
    name_col = name_col or name_attr

    class Permission(object):
        """
        """
        @property
        def _name(self):
            return getattr(self, name_attr)

        @_name.setter
        def _name(self, value):
            setattr(self, name_attr, value)

    setattr(Permission, name_attr,
        sqlalchemy.Column(name_col,
            sqlalchemy.types.Unicode(name_size),
            nullable=False, unique=True))

    return Permission