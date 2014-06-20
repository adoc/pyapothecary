"""SQLAlchemy Model Mixins
"""

import os
import time
import base64
import logging
import sqlalchemy
import sqlalchemy.types
import sqlalchemy.orm
import sqlalchemy.ext.hybrid


logger = logging.getLogger(__name__)

__all__ = ("id_mix", "IdMix", "ts_mix")


def _timefunc():
    """
    """
    return int(time.time())


def _tokenfunc(length):
    # 2.7 here. Put 3.0+ handling in another func.
    return base64.b64encode(os.urandom(length*2)).encode()[:length]


class ConstructorMix(object):
    """This sets column values using constructor keyword args.
    """
    def __init__(self, *args, **kwa):
        """
        """
        cls = self.__class__
        for key, val in kwa.items():
            # Set primary attribute.
            if self.__table__.columns.has_key(key):
                setattr(self, key, val) # Set
            # Set descriptor attribute.
            elif hasattr(cls, key):
                attr = getattr(cls, key)
                if hasattr(attr, 'descriptor'):
                    if isinstance(getattr(attr, 'descriptor'), property):
                        setattr(self, key, val) # Set
            else:
                # Raise here I think.
                # kwa ignored.
                logger.warning("Key `%s` was not found in model. Ignoring.")


def id_mix(id_key='id'):
    """
    """
    class IdMix(object):
        """Integer primary key model mixin."""
        pass

    def col(**kwa):
        kwa['primary_key'] = True
        return sqlalchemy.Column(sqlalchemy.types.Integer, **kwa)

    setattr(IdMix, id_key, col())
    return IdMix
IdMix = id_mix()



def ts_mix(ts_col, oncreate=False, onupdate=False, defer=False,
          timefunc=_timefunc, Type=sqlalchemy.types.Integer):
    """
    `ts_col` - Column name for created timestamp.
    `oncreate` -
    `onupdate` -
    `defer` - Defer loading of the columns to access time rather
              than at query.
    `timefunc` - 
    `Type` -
    """
    assert isinstance(ts_col, basestring), "`ts_col` attribute must be a string."

    class TsMix(object):
        """Timestamp Model Mixin.
        """
        @sqlalchemy.ext.hybrid.hybrid_property
        def _ts(self):
            return getattr(self, ts_col)

        @_ts.setter
        def _ts(self, value):
            setattr(self, ts_col, value)

        def _set_now(self):
            self._ts = timefunc()

    def col(**col_kwa):
        # Create the Column object with various options.
        if oncreate is True:
            col_kwa['default'] = timefunc
        if onupdate is True:
            col_kwa['default'] = timefunc #??
            col_kwa['onupdate'] = timefunc
        col_kwa['nullable'] = not(oncreate or onupdate)
        return sqlalchemy.Column(Type, **col_kwa)

    setattr(TsMix, '_'.join([ts_col, 'set_now']), TsMix._set_now)

    if defer is True:
        # Defer loading of column.
        setattr(TsMix, ts_col, sqlalchemy.orm.defered(col()))
    else:
        # Eager (?) loading of column.
        setattr(TsMix, ts_col, col())
    return TsMix
TsUpdatedMix = ts_mix('ts_updated', onupdate=True)
TsCreatedMix = ts_mix('ts_created', oncreate=True)


def flag_mix(flag_col, default=True, invert_filter=False,
            Type=sqlalchemy.types.Boolean):
    """Allows for the arbitrary creation of flag (boolean) attributes.
    Queries are automatically filtered based on the flag when coupled
    with .unique_constructor, .query_filters, or .rebase metaclass.

    `flag_col` - the name of the flag attribute.
        This is also doubles as the table column name unless
        `col_name` is set. Two methods are added based on this name:
            flag_[flagattr] - Sets the flag. (alias of FlagMix._flag)
            unflag_[flagattr] - Unsets the flag. (alias of FlagMix._unflag)

    `default` - This is the default value set upon row insert.

    `invert_filter` - This inverts the filter from expecting a True
        value to Fale.

    `Type` - The SQLAlchemy type to use for the column.
    """
    # Removed the confusion of `inverse`. Replaced with `invert_filter`
    # Removed col_name.
    class FlagMix(object):
        """ """
        @sqlalchemy.ext.hybrid.hybrid_property
        def _flag(self):
            return getattr(self, flag_col)

        @_flag.setter
        def _flag(self, value):
            assert isinstance(value, bool), "`value` must be boolean."
            setattr(self, flag_col, value)

        def _set_flag(self):
            self._flag = True

        def _unset_flag(self):
            self._flag = False

        @property
        def __filter__(self):
            return self._flag is False if invert_filter else True

    def col():
        return sqlalchemy.Column(sqlalchemy.types.Boolean, default=default,
                                 nullable=False)

    setattr(FlagMix, '_'.join(['set', flag_col]), FlagMix._set_flag)
    setattr(FlagMix, '_'.join(['unset', flag_col]), FlagMix._unset_flag)
    setattr(FlagMix, flag_col, col())

    return FlagMix
ActiveMix = flag_mix('active')
DeletableMix = flag_mix('deleted', default=False, invert_filter=True)


def flag_ts_mix(flag_col, ts_col, default_flag=False, timefunc=_timefunc):
    FlagMix = flag_mix(flag_col, default=default_flag)
    TsMix = ts_mix(ts_col, timefunc=timefunc, oncreate=default_flag is True)

    class FlagTsMix(FlagMix, TsMix):
        """
        """
        @sqlalchemy.ext.hybrid.hybrid_property
        def _flag(self):
            return FlagMix._flag(self)

        @_flag.setter
        def _flag(self, value):
            # Can this be refactored to not repeat what's in FlagMix?
            assert isinstance(value, bool), "`value` must be boolean."
            setattr(self, flag_col, value)

            if value is True:
                setattr(self, ts_col, timefunc())
            else:
                setattr(self, ts_col, None)

    return FlagTsMix


def record_token_mix(token_col, length=6, oncreate=False, onupdate=False,
                     tokenfunc=_tokenfunc, index=True,
                     Type=sqlalchemy.types.String):
    """
    """
    def gentoken():
        # Closure to pass to SQLA events.
        return tokenfunc(length)

    if length < 6:
        log.warning("SecMix with a length less than 6 is not recomended.")

    class RecordTokenMix(object):
        """
        """
        @sqlalchemy.ext.hybrid.hybrid_property
        def _token(self):
            return getattr(self, token_col)

        @_token.setter
        def _token(self, value):
            assert isinstance(value, basestring), "`value` must be a string."
            setattr(self, token_col, value)

        def revoke_token(self):
            """
            """
            self._token = gentoken()

    def col(**kwa):
        # Create the Column object with various options.
        if oncreate is True:
            kwa['default'] = gentoken
        if onupdate is True:
            kwa['default'] = gentoken #??
            kwa['onupdate'] = gentoken
        kwa['nullable'] = not(oncreate or onupdate)
        kwa['index'] = index
        return sqlalchemy.Column(Type(length), **kwa)

    setattr(RecordTokenMix, token_col, col())
    return RecordTokenMix


def sequence_mix(sequence_col, default=0, index=True):
    class SequenceMix(object):
        """Base Sequence mixin class """
        
        @sqlalchemy.ext.hybrid.hybrid_property
        def _sequence(self):
            return getattr(self, sequence_col)

        @_sequence.setter
        def _sequence(self, value):
            assert isinstance(value, int), "`value` must be an integer."
            setattr(self, sequence_col, value)

        def _sequence_inc(self):
            self._sequence += 1

        def _sequence_dec(self):
            self._sequence -= 1

    def col(**kwa):
        return sqlalchemy.Column(sqlalchemy.types.Integer, index=index,
                                 nullable=True, default=default)

    setattr(SequenceMix, sequence_col, col())
    return SequenceMix
SequenceMix = sequence_mix('sequence')


def lookup_mix(key_col='key', value_col='desc', ext_col=None,
               index_name=True, key_len=32, value_len=160, ext_len=1024):
    """Provides a simple 'key', 'value', and optionally 'extended'
    columns. While resembling a key/value store, there are better tools
    for that.
    'key' is always required and indexed by default.
    'value' and 'extended value' expect Unicode and are
        nullable.
    """
    class LookupMix(object):
        """Base Simple Lookup model"""
        pass

    setattr(LookupMix, key_col,
                sqlalchemy.Column(sqlalchemy.types.String(length=key_len),
                                  unique=index_name, index=index_name,
                                  nullable=False))
    setattr(LookupMix, value_col,
                sqlalchemy.Column(sqlalchemy.types.Unicode(length=value_len),
                                  nullable=True))
    if ext_col is not None:
        setattr(LookupMix, ext_col,
                    sqlalchemy.Column(sqlalchemy.types.Unicode(length=ext_len),
                                      nullable=True))
    return LookupMix

LookupMix = lookup_mix()
LookupMixExt = lookup_mix(ext_col='ext')


