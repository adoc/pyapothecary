"""
"""
import math
import base64
import sqlalchemy.ext.hybrid
import sqlalchemy.ext.declarative

import apothecary.modelmix
import apothecary.util


__all__ = ("user_mix", "group_mix", "permission_mix")

try:
    _basestring = basestring
except NameError:
    _basestring = str


def user_mix(name_attr="name", name_col=None, name_size=32, index_name=False,
         namehash_attr="namehash", namehash_col=None,
         passhash_attr="passhash", passhash_col=None,
         salt_col="salt", salt_size=8,
         hashfunc=apothecary.util.hash,
         binary_encode=False,
         basefunc=apothecary.util.benc):
    """
    """
    assert callable(hashfunc), "`hashfunc` must be callable."
    assert callable(basefunc), "`basefunc` must be callable."

    name_col = name_col or name_attr
    namehash_col = namehash_col or namehash_attr
    passhash_col = passhash_col or passhash_attr

    hash_size = hashfunc.digest_length
    hash_benc_size = basefunc.overhead(hash_size)
    salt_benc_size = basefunc.overhead(salt_size)

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
        # Create columns
        __name = sqlalchemy.Column(name_col,
                    sqlalchemy.types.Unicode(length=name_size),
                    index=index_name is True, nullable=False)

        if binary_encode is True:
            __namehash = sqlalchemy.Column(namehash_col,
                            sqlalchemy.types.String(hash_benc_size),
                            index=True, unique=True)
            __passhash = sqlalchemy.Column(passhash_col,
                            sqlalchemy.types.String(hash_benc_size))
            __salt = sqlalchemy.Column(salt_col,
                            sqlalchemy.types.String(salt_benc_size))
        else:
            __namehash = sqlalchemy.Column(namehash_col,
                            sqlalchemy.types.LargeBinary(hash_size),
                            index=True, unique=True)
            __passhash = sqlalchemy.Column(passhash_col,
                            sqlalchemy.types.LargeBinary(hash_size))
            __salt = sqlalchemy.Column(salt_col,
                            sqlalchemy.types.LargeBinary(salt_size))

        @property
        def _name(self):
            return self.__name

        @_name.setter
        def _name(self, value):
            """Set name and namehash."""
            assert isinstance(value, _basestring), "`value` must be a string."
            assert value, "`value` cannot be empty."
            self.__namehash = encode(hashfunc(value.encode()))
            self.__name = value

        @property
        def _salt(self):
            """Get salt if exists otherwise, generate salt."""
            _salt = decode(self.__salt)
            if not _salt:
                _salt = apothecary.util.random.read(salt_size)
                self.__salt = encode(_salt)
            return _salt

        @property
        def _passhash(self):
            return decode(self.__passhash)

        @_passhash.setter
        def _passhash(self, value):
            raise AttributeError("Cannot set a password hash. Set `password`.")

        @property
        def password(self):
            raise AttributeError("Cannot get a password. Get `passhash`.")

        @password.setter
        def password(self, value):
            self.__passhash = encode(hashfunc(value.encode(), self._salt))

        def challenge(self, password):
            challenge_hash = hashfunc(password.encode(), self._salt)
            # Always comparing bytes hashes here.
            return challenge_hash == self._passhash

    setattr(User, name_attr, apothecary.util.synonym('_name'))
    setattr(User, namehash_attr, apothecary.util.synonym('_namehash'))
    setattr(User, passhash_attr, apothecary.util.synonym('_passhash'))

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
        __name = sqlalchemy.Column(name_col,
                          sqlalchemy.types.Unicode(name_size),
                          nullable=False, unique=True)

        __level = sqlalchemy.Column(level_col,
                          sqlalchemy.types.Integer(),
                          nullable=False, default=-1)

        @property
        def _name(self):
            return self.__name

        @_name.setter
        def _name(self, value):
            assert isinstance(value, _basestring), "`name` must be a string."
            self.__name = value

        @property
        def _level(self):
            return self.__level

        @_level.setter
        def _level(self, value):
            assert isinstance(value, int), '`level` must be an integer.'
            self.__level = value

        # Comparators
        def __lt__(self, other):
            return self._level < other._level

        def __gt__(self, other):
            return self._level > other._level

        def __eq__(self, other):
            return self._level == other._level

        def __le__(self, other):
            return self._level <= other._level

        def __ge__(self, other):
            return self._level >= other._level

        def __ne__(self, other):
            return self._level != other._level

    setattr(Group, name_attr, apothecary.util.synonym("_name"))
    setattr(Group, level_attr, apothecary.util.synonym("_level"))

    return Group


def permission_mix(name_attr="name", name_col=None, name_size=32):
    """
    """
    name_col = name_col or name_attr

    class Permission(object):
        """
        """
        __name = sqlalchemy.Column(name_col,
                sqlalchemy.types.Unicode(name_size),
                nullable=False, unique=True)

        @property
        def _name(self):
            return self.__name

        @_name.setter
        def _name(self, value):
            assert isinstance(value, _basestring), "`name` must be a string."
            self.__name = value

    setattr(Permission, name_attr, apothecary.util.synonym('_name'))

    return Permission

def group_permission_mix(group_cls, permission_cls,
                         group_id_colname="group_id",
                         permission_id_colname="permission_id",
                         permissions_attr="permissions"):
    """
    """
    group_pri_key_columns = group_cls.__table__.primary_key.columns.items()
    perm_pri_key_columns = permission_cls.__table__.primary_key.columns.items()

    assert len(group_pri_key_columns) == 1, "group_permission_mix has no support for multiple primary key columns yet."
    assert len(perm_pri_key_columns) == 1, "group_permission_mix has no support for multiple primary key columns yet."

    parent_group_id_col = group_pri_key_columns[0][1]
    parent_permission_id_col =  perm_pri_key_columns[0][1]

    class GroupPermission(object):
        """
        """
        __group_id = sqlalchemy.ext.declarative.declared_attr(lambda cls:
                        sqlalchemy.Column(group_id_colname,
                            parent_group_id_col.type,
                            sqlalchemy.ForeignKey(parent_group_id_col)))
        __permission_id = sqlalchemy.ext.declarative.declared_attr(lambda cls:
                        sqlalchemy.Column(permission_id_colname,
                            parent_permission_id_col.type,
                            sqlalchemy.ForeignKey(parent_permission_id_col)))

        @classmethod
        def init_group_relationship(cls):
            """Enable the relationship on the Group model.
            """
            setattr(group_cls, permissions_attr,
                    sqlalchemy.orm.relationship(
                        permission_cls, secondary=cls.__table__))

    return GroupPermission
