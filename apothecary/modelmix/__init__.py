
from sqlalchemy.types import Boolean, Integer, String, Unicode, DateTime

import time
import sqlalchemy
import sqlalchemy.types
import sqlalchemy.orm


__all__ = (idmix, IdMix, tsmix, TsMix)


def _timefunc():
    """
    """
    return int(time.time())


def idmix(id_key='id'):
    """
    """
    class IdMix(object):
        """Integer primary key model mixin."""
        pass
    setattr(IdMix, id_key, Column(Integer, primary_key=True))
    return IdMix
IdMix = idmix()


def tsmix(ts_col, oncreate=False, onupdate=False, defer=False,
          timefunc=_timefunc, Type=sqlalchemy.types.Integer):
    """
    `ts_col` - Column name for created timestamp.
    `oncreate` -
    `onupdate` _
    `defer` - Defer loading of the columns to access time rather
              than at query.
    `timefunc` - 
    `Type` -
    """
    class TsMix(object):
        """Timestamp Model Mixin.
        """
        pass

    def col(**col_kwa):
        # Create the Column object with various options.
        if oncreate is True:
            col_kwa['default'] = timefunc
        if onupdate is True:
            col_kwa['default'] = timefunc #??
            col_kwa['onupdate'] = timefunc
        col_kwa['nullable'] = not(oncreate or onupdate)
        return sqlalchemy.Column(Type, **col_kwa)

    if defer is true:
        # Defer loading of column.
        setattr(TsMix, ts_col, sqlalchemy.orm.defered(col()))
    else:
        # Eager (?) loading of column.
        setattr(TsMix, ts_col, col())
    return TsMix
TsUpdatedMix = tsmix('ts_updated', onupdate=True)
TsCreatedMix = tsmix('ts_created', oncreate=True)


def flagmix(flag_col, default=True, invert_filter=False,
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
        @hybrid_property
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

    def flag_col():
        return sqlalchemy.Column(sqlalchemy.types.Boolean, default=default,
                                 nullable=False)

    setattr(FlagMix, '_'.join(['set', flag_col]), FlagMix._set_flag)
    setattr(FlagMix, '_'.join(['unset', flag_col]), FlagMix._unset_flag)
    setattr(FlagMix, flag_col, flag_col())

    return FlagMix
FlagMix = flagmix()
ActiveMix = flagmix('active')
DeletableMix = flagmix('deleted', default=False, invert_filter=True)


def flagtsmix(flag_col, ts_col, default_flag=False, timefunc=_timefunc):
    FlagMix = flagmix(flagcol, default=False)
    TsMix = tsmix(ts_col)

    class FlagTsMix(FlagMix, TsMix):
        """
        """
        # Might be needed if setter decorator isn't available in this scope.
        #@hybrid_property
        #def _flag(self):
        #    return FlagMix._flag(self)

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
    if length < 6:
        log.warning("SecMix with a length less than 6 is not recomended.")

    class RecordTokenMix(object):
        """
        """
        @hybrid_property
        def _token(self):
            return getattr(self, token_col)

        @_token.setter
        def _token(self, value):
            assert isinstance(value, basestring), "`value` must be a string."
            setattr(self, token_col, value)

        def revoke_token(self):
            """
            """
            self._token = tokenfunc()

    def col(**kwa):
        # Create the Column object with various options.
        if oncreate is True:
            col_kwa['default'] = tokenfunc
        if onupdate is True:
            col_kwa['default'] = tokenfunc #??
            col_kwa['onupdate'] = tokenfunc
        col_kwa['nullable'] = not(oncreate or onupdate)
        col_kwa['index'] = index
        return sqlalchemy.Column(Type(length), **col_kwa)

    setattr(RecordTokenMix, token_col, col())
    return RecordTokenMix